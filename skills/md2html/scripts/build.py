#!/usr/bin/env python3
"""md2html assembler — merges template.html + metadata + fragments into the final page.

Why this exists: re-typing the 1,100-line template by hand wastes effort and
risks drift. You (the AI) only author the *content*; this script does the
mechanical assembly and then verifies the result.

Usage:
  python3 build.py --meta meta.json --toc toc.html --content content.html \
                   --out /path/to/output.html [--no-toc]

  meta.json     {"LANG": "ko", "TITLE": "...", ...} — every {{KEY}} in the template.
  toc.html      <a href="#...">...</a> entries only (omit with --no-toc).
  content.html  the body that goes between CONTENT_START and CONTENT_END.
  --no-toc      strip the TOC sidebar entirely (short documents).

Exits non-zero and prints the reason if verification fails.
"""
import argparse
import json
import re
import sys
from pathlib import Path

REQUIRED_KEYS = [
    "LANG", "REC_LABEL", "TITLE", "SUBTITLE", "DOC_TYPE", "SOURCE_FILE",
    "DATE", "READ_TIME", "BRAND_LABEL", "TOC_TITLE", "PRINT_TOOLTIP",
    "THEME_TOOLTIP", "CLOSE_LABEL", "SKIP_LINK_LABEL", "FOOTER_NOTE",
]
MERMAID_TYPES = ("flowchart", "sequenceDiagram", "erDiagram", "stateDiagram-v2",
                 "gantt", "classDiagram", "journey", "pie", "timeline")
START, END = "<!-- CONTENT_START -->", "<!-- CONTENT_END -->"


def fail(msg):
    print(f"BUILD FAILED: {msg}")
    sys.exit(1)


def splice(html, start_marker, end_marker, payload):
    i = html.find(start_marker)
    j = html.find(end_marker)
    if i == -1 or j == -1 or j < i:
        fail(f"markers not found or out of order: {start_marker} / {end_marker}")
    return html[: i + len(start_marker)] + "\n" + payload + "\n" + html[j:]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--template", default=str(Path(__file__).resolve().parent.parent / "template.html"))
    p.add_argument("--meta", required=True)
    p.add_argument("--toc", default=None)
    p.add_argument("--content", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--no-toc", action="store_true")
    a = p.parse_args()

    html = Path(a.template).read_text(encoding="utf-8")
    meta = json.loads(Path(a.meta).read_text(encoding="utf-8"))
    content = Path(a.content).read_text(encoding="utf-8")

    missing = [k for k in REQUIRED_KEYS if k not in meta]
    if missing:
        fail(f"meta.json missing keys: {missing}")

    for k, v in meta.items():
        html = html.replace("{{%s}}" % k, str(v))

    if a.no_toc:
        html = re.sub(r'<aside class="toc".*?</aside>\s*', "", html, count=1, flags=re.S)
        # drop the mobile trigger so it doesn't open an empty drawer
        html = re.sub(r'<button class="icon-btn toc-mobile-trigger".*?</button>\s*', "", html, count=1, flags=re.S)
    else:
        toc = Path(a.toc).read_text(encoding="utf-8") if a.toc else ""
        if not toc.strip():
            fail("TOC fragment is empty; pass --no-toc to build without a sidebar")
        html = html.replace("<!-- TOC_ENTRIES -->", toc, 1)

    html = splice(html, START, END, content)

    # ---- verification ----
    errors = []
    leftover = sorted(set(re.findall(r"\{\{[A-Z_]+\}\}", html)))
    if leftover:
        errors.append(f"leftover placeholders: {leftover}")

    anchors = re.findall(r'<a[^>]+href="#([^"]+)"', html)
    ids = set(re.findall(r'\bid="([^"]+)"', html))
    broken = [x for x in anchors if x not in ids]
    if broken:
        errors.append(f"anchors with no matching id: {broken}")

    for block in re.findall(r'<pre class="mermaid">\s*(\S+)', html):
        if not block.startswith(MERMAID_TYPES):
            errors.append(f"mermaid block starts with unsupported type: {block!r}")

    emoji = sorted(set(re.findall("[\U0001F000-\U0001FAFF]", html)))
    if emoji:
        errors.append(f"emoji glyphs found (use SVG sprite icons): {emoji}")

    if errors:
        fail("; ".join(errors))

    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print(f"BUILD OK: {out} ({len(html.splitlines())} lines, {len(anchors)} anchors verified, "
          f"{html.count('class=\"mermaid\"')} mermaid blocks, no leftover placeholders)")


if __name__ == "__main__":
    main()
