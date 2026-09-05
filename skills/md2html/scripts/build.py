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
                Sections pasted as source Markdown inside <!-- MD --> … <!-- /MD -->
                are converted here (see md_passthrough.py).
  --no-toc      strip the TOC sidebar entirely (short documents).
  --render-check  load the result in headless Chrome/Chromium/Edge and fail
                on Mermaid syntax errors, KaTeX errors, or unrendered diagrams.

Exits non-zero and prints the reason if verification fails.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import md_passthrough  # noqa: E402

REQUIRED_KEYS = [
    "LANG", "REC_LABEL", "TITLE", "SUBTITLE", "DOC_TYPE", "SOURCE_FILE",
    "DATE", "READ_TIME", "BRAND_LABEL", "TOC_TITLE", "PRINT_TOOLTIP",
    "THEME_TOOLTIP", "CLOSE_LABEL", "SKIP_LINK_LABEL", "FOOTER_NOTE",
]
MERMAID_TYPES = ("flowchart", "sequenceDiagram", "erDiagram", "stateDiagram-v2",
                 "gantt", "classDiagram", "journey", "pie", "timeline")
START, END = "<!-- CONTENT_START -->", "<!-- CONTENT_END -->"
# These glyphs inside <code> usually mean LaTeX was flattened instead of
# rendered via KaTeX (components.md §15).
MATH_GLYPHS = "≈∝∑Σ∫√𝔼ℙℝ≤≥∈∉⊂⊆⊃·⋅μλΛπτΔδηφψαβγσΩω"
# Raw "<" followed by a tag-like character inside math, code, or mermaid is
# parsed as HTML by the browser and silently swallows text (`\(x<y\)` loses
# everything after x; `List<String>` renders as `List`).
RAW_TAG_RE = re.compile(r"<[A-Za-z/!?]")
# Dingbats / misc symbols emoji (✅ ⚠️ ❌ …) plus the SMP emoji planes. The
# template's own glyphs (✓ ✕ ★ ☆ ✔ ✗) are allowed.
EMOJI_RE = re.compile("[\U0001F000-\U0001FAFF\u2600-\u27BF]")
EMOJI_ALLOWED = set("✓✕★☆✔✗")
# Mermaid: node/edge labels with unquoted parentheses, and `end` used as a
# node id, both produce "Syntax error in text" at render time.
MERMAID_UNQUOTED_PAREN_RE = re.compile(
    r'\w\[(?!["(/\\\[])[^\]"]*[()]'        # A[Service (v2)]   (shapes like [(db)] [/q/] [[sub]] are fine)
    r'|\w\((?!["(\[])[^)"\n]*\('             # B(API (v2))
    r'|\|(?!")[^|"\n]*[()][^|\n]*\|'          # -->|POST /x (json)| B
)
MERMAID_END_ID_RE = re.compile(r"(?:-->|---|-\.->|==>|-\.-|\|)\s*end\b|^\s*end\s*(?:-->|---|\[|\(|\{)", re.M)
CHROME_CANDIDATES = [
    os.environ.get("MD2HTML_CHROME", ""),
    "google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome", "msedge",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
]


def fail(msg):
    print(f"BUILD FAILED: {msg}")
    sys.exit(1)


def find_chrome():
    for c in CHROME_CANDIDATES:
        if not c:
            continue
        if os.path.sep in c:
            if Path(c).is_file():
                return c
        elif shutil.which(c):
            return shutil.which(c)
    return None


def render_check(out_path, expected_mermaid):
    """Render in headless Chrome and inspect the DOM. Returns a list of errors,
    or None when no browser is available."""
    chrome = find_chrome()
    if not chrome:
        return None
    cmd = [chrome, "--headless=new", "--disable-gpu", "--no-sandbox", "--hide-scrollbars",
           "--virtual-time-budget=10000", "--dump-dom", Path(out_path).resolve().as_uri()]
    try:
        dom = subprocess.run(cmd, capture_output=True, text=True, timeout=90).stdout
    except (subprocess.TimeoutExpired, OSError) as e:
        return [f"render check could not run ({e})"]
    errors = []
    syntax = dom.count("Syntax error in text")
    if syntax:
        errors.append(f"{syntax} mermaid block(s) failed to parse (\"Syntax error in text\")")
    katex_err = len(re.findall(r'class="katex-error"', dom))
    if katex_err:
        errors.append(f"{katex_err} KaTeX error(s) — check the LaTeX and the <, >, & escaping")
    rendered = len(re.findall(r'<svg[^>]+id="mermaid-', dom))
    if expected_mermaid and rendered < expected_mermaid:
        if rendered == 0:
            errors.append(f"0 of {expected_mermaid} mermaid diagrams rendered — CDN unreachable or every block failed")
        else:
            errors.append(f"only {rendered} of {expected_mermaid} mermaid diagrams rendered")
    return errors


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
    p.add_argument("--allow-unicode-math-in-code", action="store_true",
                   help="skip the math-glyph-in-<code> check (only for code that genuinely uses these glyphs)")
    p.add_argument("--render-check", action="store_true",
                   help="render in headless Chrome and fail on mermaid/KaTeX errors (skipped if no browser)")
    a = p.parse_args()

    html = Path(a.template).read_text(encoding="utf-8")
    meta = json.loads(Path(a.meta).read_text(encoding="utf-8"))
    content = Path(a.content).read_text(encoding="utf-8")
    content, md_blocks = md_passthrough.expand(content)
    if md_passthrough.MD_START in content or md_passthrough.MD_END in content:
        fail("unbalanced <!-- MD --> / <!-- /MD --> markers in content.html")

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

    mermaid_bodies = re.findall(r'<pre class="mermaid">(.*?)</pre>', content, flags=re.S)
    for body in mermaid_bodies:
        head = body.strip().split(None, 1)[0] if body.strip() else ""
        if not head.startswith(MERMAID_TYPES):
            errors.append(f"mermaid block starts with unsupported type: {head!r}")
        if RAW_TAG_RE.search(body):
            errors.append("mermaid block contains raw HTML (<br/>, <b>, …) — escape it as &lt;br/&gt;; "
                          f"see {body.strip()[:50]!r}")
        if head.startswith("flowchart"):
            for line in body.splitlines():
                if MERMAID_UNQUOTED_PAREN_RE.search(line):
                    errors.append(f"mermaid label with unquoted parentheses — wrap it as A[\"…\"]: {line.strip()[:60]!r}")
                if MERMAID_END_ID_RE.search(line):
                    errors.append(f"mermaid node id `end` is reserved — rename it: {line.strip()[:60]!r}")

    emoji = sorted(set(EMOJI_RE.findall(html)) - EMOJI_ALLOWED)
    if emoji:
        errors.append(f"emoji glyphs found (use SVG sprite icons): {emoji}")

    for m in re.finditer(r"\\\((.*?)\\\)|\$\$(.*?)\$\$", content, flags=re.S):
        body = m.group(1) if m.group(1) is not None else m.group(2)
        if RAW_TAG_RE.search(body):
            errors.append(f"raw < inside math — write &lt; (the browser eats `<y…` as a tag): {body.strip()[:50]!r}")
            break
    for m in re.finditer(r"<pre><code[^>]*>(.*?)</code></pre>", content, flags=re.S):
        if RAW_TAG_RE.search(m.group(1)):
            errors.append("raw < inside <pre><code> — escape as &lt; (generics, HTML samples, `2>&1` all vanish otherwise): "
                          f"{m.group(1).strip()[:50]!r}")
            break

    # math checks run on the content fragment only (template JS legitimately contains \( \))
    if content.count("\\(") != content.count("\\)"):
        errors.append(f"unbalanced inline math delimiters: {content.count(chr(92)+'(')} \\( vs "
                      f"{content.count(chr(92)+')')} \\)")
    if content.count("$$") % 2 != 0:
        errors.append("odd number of $$ — a display math block is unterminated")
    if not a.allow_unicode_math_in_code:
        flat = [m for m in re.findall(r"<code>(.*?)</code>", content, flags=re.S)
                if any(g in m for g in MATH_GLYPHS)]
        if flat:
            sample = "; ".join(f"<code>{m.strip()[:60]}</code>" for m in flat[:3])
            errors.append(f"{len(flat)} <code> span(s) contain math glyphs — render math with KaTeX "
                          f"(components.md §15), e.g. {sample}")

    if errors:
        fail("; ".join(errors))

    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    flows = len(re.findall(r'<div class="flow[\s"]', content))
    mockups = len(re.findall(r'<div class="mockup"', content))
    mermaids = len(mermaid_bodies)
    inline_math = content.count("\\(")

    render_note = ""
    if a.render_check:
        render_errors = render_check(out, mermaids)
        if render_errors is None:
            render_note = ", render check skipped (no Chrome/Chromium/Edge found; set MD2HTML_CHROME)"
        elif render_errors:
            out.unlink(missing_ok=True)
            fail("render check: " + "; ".join(render_errors))
        else:
            render_note = ", rendered in headless Chrome without mermaid/KaTeX errors"

    print(f"BUILD OK: {out} ({len(html.splitlines())} lines, {len(anchors)} anchors verified, "
          f"{md_blocks} markdown blocks converted, "
          f"{flows} native flows, {mockups} wireframes, {mermaids} mermaid blocks, "
          f"{content.count('$$') // 2} display + {inline_math} inline math, "
          f"no leftover placeholders{render_note})")


if __name__ == "__main__":
    main()
