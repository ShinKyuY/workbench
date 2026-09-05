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
                on KaTeX errors, diagram labels that overflow their node, or
                diagrams drawn outside their viewBox.

Exits non-zero and prints the reason if verification fails.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import md_passthrough  # noqa: E402

REQUIRED_KEYS = [
    "LANG", "REC_LABEL", "TITLE", "SUBTITLE", "DOC_TYPE", "SOURCE_FILE",
    "DATE", "READ_TIME", "BRAND_LABEL", "TOC_TITLE", "PRINT_TOOLTIP",
    "THEME_TOOLTIP", "CLOSE_LABEL", "SKIP_LINK_LABEL", "FOOTER_NOTE",
]
START, END = "<!-- CONTENT_START -->", "<!-- CONTENT_END -->"
# These glyphs inside <code> usually mean LaTeX was flattened instead of
# rendered via KaTeX (components.md §15).
MATH_GLYPHS = "≈∝∑Σ∫√𝔼ℙℝ≤≥∈∉⊂⊆⊃·⋅μλΛπτΔδηφψαβγσΩω"
# Raw "<" followed by a tag-like character inside math or code is parsed as
# HTML by the browser and silently swallows text (`\(x<y\)` loses everything
# after x; `List<String>` renders as `List`).
RAW_TAG_RE = re.compile(r"<[A-Za-z/!?]")
# Dingbats / misc symbols emoji (✅ ⚠️ ❌ …) plus the SMP emoji planes. The
# template's own glyphs (✓ ✕ ★ ☆ ✔ ✗) are allowed.
EMOJI_RE = re.compile("[\U0001F000-\U0001FAFF\u2600-\u27BF]")
EMOJI_ALLOWED = set("✓✕★☆✔✗")
# Inline SVG diagrams (components.md §6): shared marker ids live in the
# template; diagrams may only reference them, never define their own.
DG_MARKER_IDS = ("dg-arrow", "dg-arrow-accent", "dg-arrow-muted", "dg-arrow-open",
                 "dg-crow-one", "dg-crow-many", "dg-dot")
DG_FORBIDDEN_TAGS = ("script", "style", "foreignObject", "image", "a", "use", "defs", "marker", "svg")
DG_FORBIDDEN_ATTRS = ("style", "fill", "stroke", "color", "font-size", "font-family", "href", "xlink:href")
DG_CLASS_RE = re.compile(r'class="[^"]*\bdg\b[^"]*"')
DG_ROOT_RE = re.compile(r'<svg class="dg" viewBox="0 0 (\d+) (\d+)" width="(\d+)" role="img" aria-label="[^"]+">')
DG_SVG_RE = re.compile(DG_ROOT_RE.pattern + r".*?</svg>", re.S)
DG_CJK_RE = re.compile("[ᄀ-ᇿ぀-ヿ㄰-㆏㐀-䶿一-鿿가-힣＀-￯]")
DG_TEXT_BUDGET = {"dg-process": lambda w: w - 16, "dg-external": lambda w: w - 16, "dg-note": lambda w: w - 16,
                  "dg-state": lambda w: w - 16, "dg-datastore": lambda w: w - 16, "dg-decision": lambda w: 0.7 * w,
                  "dg-queue": lambda w: w - 32, "dg-entity": lambda w: w - 20, "dg-actor": lambda w: 112}
DG_SHAPES = tuple(DG_TEXT_BUDGET) + ("dg-state-start", "dg-state-end")
DG_SHAPE_TAGS = ("rect", "polygon", "path", "ellipse", "circle", "line", "polyline")
DG_TEXT_EM = {"dg-text": 13, "dg-entity-title": 13, "dg-sub": 11, "dg-entity-row": 12}
DG_MARKER_ATTRS = ("marker-start", "marker-mid", "marker-end")
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


def render_check(out_path, expected_diagrams):
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
    katex_err = len(re.findall(r'class="katex-error"', dom))
    if katex_err:
        errors.append(f"{katex_err} KaTeX error(s) — check the LaTeX and the <, >, & escaping")
    checked = dom.count('data-dg-checked="1"')
    if expected_diagrams and checked < expected_diagrams:
        errors.append(f"only {checked} of {expected_diagrams} svg diagrams were checked (boot script did not run)")
    overflow = sum(int(n) for n in re.findall(r'data-dg-overflow="(\d+)"', dom))
    if overflow:
        errors.append(f"{overflow} diagram label(s) overflow their shape — shorten the label or widen the node")
    clipped = dom.count('data-dg-clipped="1"')
    if clipped:
        errors.append(f"{clipped} diagram(s) draw outside their viewBox — enlarge viewBox or move the element")
    return errors


def dg_classes(el):
    return el.get("class", "").split()


def dg_text_width(s, em):
    """Estimated rendered width: CJK glyphs 1.0 em, everything else 0.6 em."""
    return sum((1.0 if DG_CJK_RE.match(ch) else 0.6) * em for ch in s)


def dg_shape_width(node):
    """Width of the first rect / polygon / ellipse / circle child of a node."""
    for child in node:
        if child.tag == "rect":
            return float(child.get("width", 0))
        if child.tag == "polygon":
            xs = [float(n) for n in re.findall(r"-?\d+(?:\.\d+)?", child.get("points", ""))][0::2]
            return max(xs) - min(xs) if xs else 0
        if child.tag == "ellipse":
            return 2 * float(child.get("rx", 0))
        if child.tag == "circle":
            return 2 * float(child.get("r", 0))
    return 0


def check_diagram(src):
    """Static checks for one svg.dg (components.md §6). Returns a list of errors."""
    errors = []
    m = DG_ROOT_RE.match(src)
    vb_w, width = int(m.group(1)), int(m.group(3))
    if vb_w > 880:
        errors.append(f"viewBox width {vb_w} exceeds 880 — split the diagram or tighten the grid")
    if width != vb_w:
        errors.append(f'width="{width}" must equal the viewBox width {vb_w}')
    try:
        root = ET.fromstring(src)
    except ET.ParseError:
        errors.append("svg.dg is not well-formed XML (raw < or &, unclosed tag) — write &lt; / &amp;")
        return errors
    parent = {child: el for el in root.iter() for child in el}

    def ancestors(el):
        while el in parent:
            el = parent[el]
            yield el

    accent_nodes = accent_edges = 0
    for el in root.iter():
        if el is root:
            continue
        cls = dg_classes(el)
        if el.tag in DG_FORBIDDEN_TAGS:
            errors.append(f"<{el.tag}> is not allowed inside svg.dg")
        bad = [k for k in el.attrib if k in DG_FORBIDDEN_ATTRS]
        if bad:
            errors.append(f"<{el.tag} {bad[0]}=…> — colors and fonts come from classes, not attributes")
        for attr in DG_MARKER_ATTRS:
            v = el.get(attr)
            if v is None:
                continue
            ref = re.fullmatch(r"url\(#([^)]+)\)", v)
            if not ref or ref.group(1) not in DG_MARKER_IDS:
                errors.append(f"{attr}={v!r} is not a shared marker — use url(#ID) with ID in {DG_MARKER_IDS}")
        if "dg-edge" in cls and not any(attr in el.attrib for attr in DG_MARKER_ATTRS):
            errors.append("dg-edge without a marker-* attribute — every edge needs an arrowhead")
        accent_nodes += "dg-node-accent" in cls
        accent_edges += "dg-edge-accent" in cls

        if el.tag == "text":
            in_node = any("dg-node" in dg_classes(a) and a.tag == "g" for a in ancestors(el))
            in_group = ("dg-group-title" in cls and el in parent
                        and parent[el].tag == "g" and "dg-group" in dg_classes(parent[el]))
            if not (in_node or "dg-edge-label" in cls or in_group):
                errors.append(f"text outside a known container: {(el.text or '').strip()[:60]!r}")
            tspans = list(el)
            if any(t.tag != "tspan" for t in tspans):
                errors.append("<text> may only contain <tspan>")
            if len(tspans) > 2:
                errors.append("<text> has more than 2 lines — shorten or split the node")
            if len(tspans) == 2 and "dg-sub" not in dg_classes(tspans[1]):
                errors.append('second <tspan> must carry class="dg-sub"')
            if "dg-edge-label" in cls:
                for line in tspans or [el]:
                    label = (line.text or "").strip()
                    est = dg_text_width(label, 12)
                    if est > 144:
                        errors.append(f'edge label "{label[:60]}" (~{est:.0f}px) is too long (max 144px) — shorten it')

        if el.tag == "g" and "dg-node" in cls:
            shapes = [c for c in cls if c in DG_SHAPES]
            if len(shapes) != 1:
                errors.append(f"dg-node must have exactly one shape class, got {shapes}")
                continue
            shape = shapes[0]
            if not any(c.tag in DG_SHAPE_TAGS for c in el):
                errors.append(f"{shape} node has no shape element")
            if shape in ("dg-state-start", "dg-state-end"):
                continue
            texts = [c for c in el if c.tag == "text"]
            if shape == "dg-entity":
                titles = [t for t in texts if "dg-entity-title" in dg_classes(t)]
                rows = [t for t in texts if "dg-entity-row" in dg_classes(t)]
                if len(titles) != 1 or not rows:
                    errors.append("dg-entity needs one dg-entity-title and at least one dg-entity-row")
            elif len(texts) != 1:
                errors.append(f"{shape} node must contain exactly one <text>, got {len(texts)}")
            if any(c.startswith("dg-status-") for c in cls) and not any(
                    "dg-sub" in dg_classes(t) for t in el.iter("tspan")):
                errors.append("dg-status-* node needs a tspan.dg-sub naming the state in words")
            width = 0 if shape == "dg-actor" else dg_shape_width(el)
            budget = DG_TEXT_BUDGET[shape](width)
            for t in texts:
                em_text = DG_TEXT_EM.get(next((c for c in dg_classes(t) if c in DG_TEXT_EM), "dg-text"))
                for line in list(t) or [t]:
                    em = DG_TEXT_EM.get(next((c for c in dg_classes(line) if c in DG_TEXT_EM), ""), em_text)
                    label = (line.text or "").strip()
                    est = dg_text_width(label, em)
                    if est > budget:
                        errors.append(f'label "{label[:60]}" (~{est:.0f}px) does not fit its {shape} '
                                      f"(budget {budget:.0f}px) — shorten or widen")

    if accent_nodes > 1:
        errors.append(f"{accent_nodes} dg-node-accent nodes — at most one accent per diagram")
    if accent_edges and not accent_nodes:
        errors.append("dg-edge-accent without a dg-node-accent — the accent edge must lead to the accent node")
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
                   help="render in headless Chrome and fail on diagram/KaTeX errors (skipped if no browser)")
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

    for tag in re.findall(r"<svg\b[^>]*>", content):
        if DG_CLASS_RE.search(tag) and not DG_ROOT_RE.fullmatch(tag):
            errors.append('svg.dg root tag must be <svg class="dg" viewBox="0 0 W H" width="W" role="img" '
                          f'aria-label="…">: {tag[:60]!r}')
    diagrams = [m.group(0) for m in DG_SVG_RE.finditer(content)]
    for n, svg in enumerate(diagrams, 1):
        errors.extend(f"svg.dg #{n}: {e}" for e in check_diagram(svg))

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
    inline_math = content.count("\\(")

    render_note = ""
    if a.render_check:
        render_errors = render_check(out, len(diagrams))
        if render_errors is None:
            render_note = ", render check skipped (no Chrome/Chromium/Edge found; set MD2HTML_CHROME)"
        elif render_errors:
            out.unlink(missing_ok=True)
            fail("render check: " + "; ".join(render_errors))
        else:
            render_note = ", rendered in headless Chrome without diagram/KaTeX errors"

    print(f"BUILD OK: {out} ({len(html.splitlines())} lines, {len(anchors)} anchors verified, "
          f"{md_blocks} markdown blocks converted, "
          f"{flows} native flows, {mockups} wireframes, {len(diagrams)} svg diagrams, "
          f"{content.count('$$') // 2} display + {inline_math} inline math, "
          f"no leftover placeholders{render_note})")


if __name__ == "__main__":
    main()
