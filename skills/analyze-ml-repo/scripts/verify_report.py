#!/usr/bin/env python3
"""Verify an analysis document's code citations and Mermaid blocks.

Usage:
    python3 verify_report.py <doc.md> --repo <analyzed-repo-root>

Checks every `path:line` / `path:start-end` citation in the document
(file exists under the repo root, line numbers within file length) and
lints Mermaid blocks (direction stated, bracket labels quoted,
subgraph/end balanced). Exit 0 when clean, 1 when anything fails.

Stdlib only. Sample-verification of *meaning* (does the cited code say
what the report claims?) stays a human/orchestrator job — this script
only removes the mechanical part: hallucinated paths, out-of-range
lines, diagrams that fail to render.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

CITATION_RE = re.compile(
    r"(?P<path>[A-Za-z0-9_.\-/]*[A-Za-z0-9_\-]\.[A-Za-z][A-Za-z0-9_]*)"
    r":(?P<start>\d+)(?:\s*[-–]\s*(?P<end>\d+))?"
)
URL_RE = re.compile(r"\bhttps?://\S+|\bwww\.\S+")
# Extensions that usually mean "host, not file" when the path resolves
# to nothing (example.com:8080). Real files with these names still pass
# because existence is checked first.
HOSTLIKE_EXTS = {"com", "net", "org", "io", "ai", "dev"}
DIRECTIONS = {"TD", "TB", "BT", "LR", "RL"}
UNQUOTED_BRACKET_RE = re.compile(r"\w\[(?!\")[^\]\"]*\[")


def line_count(path: Path, cache: dict) -> int:
    if path not in cache:
        data = path.read_bytes()
        cache[path] = data.count(b"\n") + (1 if data and not data.endswith(b"\n") else 0)
    return cache[path]


SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", ".tox", ".mypy_cache"}


def index_basenames(roots: list[Path]) -> dict[str, list[Path]]:
    """basename -> every file with that name under the roots (for ambiguity checks)."""
    index: dict[str, list[Path]] = {}
    for root in roots:
        if not root.is_dir():
            continue
        for path in root.rglob("*"):
            if any(part in SKIP_DIRS for part in path.relative_to(root).parts):
                continue
            if path.is_file():
                index.setdefault(path.name, []).append(path)
    return index


def resolve(cited: str, roots: list[Path], index: dict[str, list[Path]]) -> tuple[Path | None, list[Path]]:
    """Returns (resolved file or None, same-basename candidates).

    A bare basename (no directory) is accepted only when exactly one file
    with that name exists; otherwise it is ambiguous and the caller fails it.
    """
    p = Path(cited)
    if p.is_absolute():
        return (p if p.is_file() else None), []
    candidates = index.get(p.name, [])
    if "/" not in cited:
        if len(candidates) == 1:
            return candidates[0], candidates
        return None, candidates
    for root in roots:
        cand = root / cited
        if cand.is_file():
            return cand, candidates
    return None, candidates


def check_citations(doc_text: str, roots: list[Path]) -> tuple[int, int, list[str]]:
    """Returns (checked, ignored, failures)."""
    cache: dict = {}
    seen: set = set()
    failures: list[str] = []
    checked = ignored = 0
    index = index_basenames(roots)
    for lineno, line in enumerate(doc_text.splitlines(), 1):
        for m in CITATION_RE.finditer(URL_RE.sub("", line)):
            cited, start = m.group("path"), int(m.group("start"))
            end = int(m.group("end")) if m.group("end") else start
            key = (cited, start, end)
            if key in seen:
                continue
            seen.add(key)
            target, candidates = resolve(cited, roots, index)
            if target is None:
                if cited.rsplit(".", 1)[-1].lower() in HOSTLIKE_EXTS:
                    ignored += 1
                    continue
                checked += 1
                rel = [str(c.relative_to(r)) for c in candidates for r in roots if r in c.parents]
                if "/" not in cited and len(candidates) > 1:
                    failures.append(
                        f"{cited}:{start} — ambiguous basename, {len(candidates)} candidates: "
                        f"{', '.join(rel[:5])} (doc line {lineno})"
                    )
                elif rel:
                    failures.append(
                        f"{cited}:{start} — file not found; same basename at: "
                        f"{', '.join(rel[:5])} (doc line {lineno})"
                    )
                else:
                    failures.append(f"{cited}:{start} — file not found (doc line {lineno})")
                continue
            checked += 1
            n = line_count(target, cache)
            if start > n or end > n:
                failures.append(
                    f"{cited}:{start}" + (f"-{end}" if end != start else "")
                    + f" — line exceeds file length {n} (doc line {lineno})"
                )
            elif start > end:
                failures.append(f"{cited}:{start}-{end} — inverted range (doc line {lineno})")
    return checked, ignored, failures


def extract_mermaid_blocks(doc_text: str) -> list[tuple[int, list[str]]]:
    blocks, current, start = [], None, 0
    for lineno, line in enumerate(doc_text.splitlines(), 1):
        stripped = line.strip()
        if current is None:
            if stripped.startswith("```") and stripped[3:].strip().lower() == "mermaid":
                current, start = [], lineno
        elif stripped.startswith("```"):
            blocks.append((start, current))
            current = None
        else:
            current.append(line)
    return blocks


def check_mermaid(doc_text: str) -> tuple[int, list[str]]:
    blocks = extract_mermaid_blocks(doc_text)
    failures: list[str] = []
    for start, lines in blocks:
        meaningful = [l.strip() for l in lines if l.strip() and not l.strip().startswith("%%")]
        if not meaningful:
            failures.append(f"block at doc line {start}: empty mermaid block")
            continue
        head = meaningful[0].split()
        flowchart = head[0] in ("flowchart", "graph")
        if flowchart and (len(head) < 2 or head[1] not in DIRECTIONS):
            failures.append(
                f"block at doc line {start}: '{head[0]}' without direction (TD/LR/...)"
            )
        if flowchart:
            for l in meaningful:
                if UNQUOTED_BRACKET_RE.search(l):
                    failures.append(
                        f"block at doc line {start}: unquoted [..] inside a node label: {l[:60]}"
                    )
            subs = sum(1 for l in meaningful if l.startswith("subgraph"))
            ends = sum(1 for l in meaningful if l == "end")
            if subs != ends:
                failures.append(
                    f"block at doc line {start}: {subs} subgraph vs {ends} end"
                )
    return len(blocks), failures


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("doc", type=Path, help="analysis markdown document")
    ap.add_argument("--repo", type=Path, default=None,
                    help="analyzed repo root citations are relative to "
                         "(default: CWD, then the document's directory)")
    args = ap.parse_args()

    if not args.doc.is_file():
        print(f"error: document not found: {args.doc}", file=sys.stderr)
        return 2
    doc_text = args.doc.read_text(encoding="utf-8", errors="replace")
    # With --repo, citations resolve against that tree only. Falling back to
    # CWD or the doc's directory would let a same-named file elsewhere pass.
    roots = [args.repo.resolve()] if args.repo else [Path.cwd(), args.doc.parent.resolve()]

    checked, ignored, cite_fail = check_citations(doc_text, roots)
    n_blocks, mer_fail = check_mermaid(doc_text)

    print(f"citations: {checked} checked, {checked - len(cite_fail)} ok, "
          f"{len(cite_fail)} failed, {ignored} ignored (host-like)")
    for f in cite_fail:
        print(f"  FAIL {f}")
    by_kind: dict[str, int] = {}
    for f in cite_fail:
        kind = "ambiguous basename" if "ambiguous basename" in f else (
            "missing path prefix" if "same basename at" in f else "other")
        by_kind[kind] = by_kind.get(kind, 0) + 1
    if by_kind.get("ambiguous basename", 0) + by_kind.get("missing path prefix", 0) > 0:
        print(f"  hint: {by_kind.get('ambiguous basename', 0)} ambiguous + "
              f"{by_kind.get('missing path prefix', 0)} prefix failures — "
              "fix the cited paths to be repo-relative, then re-run")
    print(f"mermaid: {n_blocks} blocks, {len(mer_fail)} failures")
    for f in mer_fail:
        print(f"  FAIL {f}")

    if cite_fail or mer_fail:
        print("result: FAIL")
        return 1
    print("result: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
