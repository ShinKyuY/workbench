#!/usr/bin/env python3
"""Markdown passthrough for md2html — converts `<!-- MD -->…<!-- /MD -->`
blocks inside content.html into HTML that uses only vanilla elements the
template already styles.

Why: the agent should hand-write HTML only for sections that become
components (flows, step cards, callouts, cards). Every other section is
pasted verbatim from the source Markdown and converted here, so the
mechanical 80% of the document can no longer lose a table row or a
number in transcription.

Supported (stdlib only, CommonMark subset):
  headings (#..######, optional `{#custom-id}`) → <hN id="slug">
  paragraphs, hard breaks (two trailing spaces)
  fenced code ``` / ~~~ with language → <pre><code class="language-x">
  blockquotes, horizontal rules
  ul / ol with indentation nesting, task lists
  pipe tables (≥ 4 columns → wrapped in .table-wrap)
  inline: `code`, **bold**, *em*, ~~del~~, [text](url), ![alt](src), autolinks
  math: $$…$$ (display, own <p>), $…$ / \\(…\\) (inline → \\(…\\)), \\[…\\] → $$…$$
  Raw HTML in a block is escaped, not passed through.
"""
from __future__ import annotations

import html
import re

MD_START, MD_END = "<!-- MD -->", "<!-- /MD -->"

_FENCE_RE = re.compile(r"^(?P<indent>\s{0,3})(?P<fence>```+|~~~+)\s*(?P<lang>[\w+#.-]*)\s*$")
_HEADING_RE = re.compile(r"^(?P<hashes>#{1,6})\s+(?P<text>.+?)(?:\s+\{#(?P<id>[\w\-가-힣]+)\})?\s*#*\s*$")
_HR_RE = re.compile(r"^\s{0,3}(?:-{3,}|\*{3,}|_{3,})\s*$")
_UL_RE = re.compile(r"^(?P<indent>\s*)[-*+]\s+(?P<text>.*)$")
_OL_RE = re.compile(r"^(?P<indent>\s*)(?P<num>\d{1,9})[.)]\s+(?P<text>.*)$")
_TASK_RE = re.compile(r"^\[(?P<mark>[ xX])\]\s+(?P<text>.*)$")
_TABLE_SEP_RE = re.compile(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)*\|?\s*$")
_DISPLAY_MATH_RE = re.compile(r"^\s*(\$\$.*?\$\$|\\\[.*?\\\])\s*$", re.S)


def slugify(text: str, used: set[str]) -> str:
    """Kebab-case id from heading text; letters, digits and Hangul survive."""
    plain = re.sub(r"`([^`]*)`", r"\1", text)
    plain = re.sub(r"[*_~]", "", plain).lower()
    slug = re.sub(r"[^\w가-힣]+", "-", plain).strip("-") or "section"
    base, n = slug, 2
    while slug in used:
        slug, n = f"{base}-{n}", n + 1
    used.add(slug)
    return slug


# ---------------------------------------------------------------- inline ----

class _Inline:
    """Inline converter. Math and code spans are cut out first so emphasis
    markers inside them (`x_i`, `a*b`) are never touched."""

    def __init__(self) -> None:
        self.slots: list[str] = []

    def _stash(self, rendered: str) -> str:
        self.slots.append(rendered)
        return f"\x00{len(self.slots) - 1}\x00"

    def run(self, text: str) -> str:
        self.slots = []
        text = self._protect_math_and_code(text)
        text = html.escape(text, quote=False)
        text = re.sub(r"!\[([^\]]*)\]\(([^)\s]+)(?:\s+\"([^\"]*)\")?\)",
                      lambda m: f'<img src="{m.group(2)}" alt="{m.group(1)}"'
                                + (f' title="{m.group(3)}"' if m.group(3) else "") + ">", text)
        text = re.sub(r"\[([^\]]+)\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)", r'<a href="\2">\1</a>', text)
        text = re.sub(r"(?<![\w\"=])(https?://[^\s<>\"]+[^\s<>\".,;:!?)])", r'<a href="\1">\1</a>', text)
        text = re.sub(r"\*\*(?=\S)(.+?)(?<=\S)\*\*", r"<strong>\1</strong>", text)
        text = re.sub(r"__(?=\S)(.+?)(?<=\S)__", r"<strong>\1</strong>", text)
        text = re.sub(r"(?<![\w*])\*(?=\S)(.+?)(?<=\S)\*(?![\w*])", r"<em>\1</em>", text)
        text = re.sub(r"(?<![\w_])_(?=\S)(.+?)(?<=\S)_(?![\w_])", r"<em>\1</em>", text)
        text = re.sub(r"~~(?=\S)(.+?)(?<=\S)~~", r"<del>\1</del>", text)
        text = re.sub(r"  $", "<br>", text, flags=re.M)
        return re.sub(r"\x00(\d+)\x00", lambda m: self.slots[int(m.group(1))], text)

    def _protect_math_and_code(self, text: str) -> str:
        out, i, n = [], 0, len(text)
        while i < n:
            ch = text[i]
            if ch == "\\" and text.startswith(("\\(", "\\["), i):
                close = "\\)" if text[i + 1] == "(" else "\\]"
                j = text.find(close, i + 2)
                if j != -1:
                    body = text[i + 2:j]
                    rendered = (f"\\({_esc(body)}\\)" if close == "\\)" else f"$${_esc(body)}$$")
                    out.append(self._stash(rendered))
                    i = j + 2
                    continue
            if ch == "$":
                if text.startswith("$$", i):
                    j = text.find("$$", i + 2)
                    if j != -1:
                        out.append(self._stash(f"$${_esc(text[i + 2:j])}$$"))
                        i = j + 2
                        continue
                else:
                    j = _find_inline_dollar(text, i)
                    if j != -1:
                        out.append(self._stash(f"\\({_esc(text[i + 1:j])}\\)"))
                        i = j + 1
                        continue
            if ch == "`":
                m = re.match(r"`+", text[i:])
                ticks = m.group(0)
                j = text.find(ticks, i + len(ticks))
                if j != -1:
                    code = text[i + len(ticks):j].strip() if len(ticks) > 1 else text[i + len(ticks):j]
                    out.append(self._stash(f"<code>{_esc(code)}</code>"))
                    i = j + len(ticks)
                    continue
            out.append(ch)
            i += 1
        return "".join(out)


def _esc(s: str) -> str:
    return html.escape(s, quote=False)


def _find_inline_dollar(text: str, i: int) -> int:
    """Closing `$` for an inline formula opened at i, or -1.

    Pandoc rule: the opener is followed by non-space, the closer is preceded
    by non-space and not followed by a digit — so "$5 and $10" stays prose.
    """
    if i + 1 >= len(text) or text[i + 1].isspace() or text[i + 1] == "$":
        return -1
    j = text.find("$", i + 1)
    while j != -1:
        if not text[j - 1].isspace() and (j + 1 >= len(text) or not text[j + 1].isdigit()):
            if "\n" not in text[i:j]:
                return j
            return -1
        j = text.find("$", j + 1)
    return -1


# ----------------------------------------------------------------- block ----

class _Block:
    def __init__(self, used_ids: set[str]) -> None:
        self.inline = _Inline()
        self.used_ids = used_ids

    def convert(self, md: str) -> str:
        lines = md.replace("\r\n", "\n").split("\n")
        return "\n".join(self._blocks(lines))

    # -- dispatcher --------------------------------------------------------
    def _blocks(self, lines: list[str]) -> list[str]:
        out: list[str] = []
        i, n = 0, len(lines)
        while i < n:
            line = lines[i]
            if not line.strip():
                i += 1
                continue
            m = _FENCE_RE.match(line)
            if m:
                i = self._fence(lines, i, m, out)
                continue
            m = _HEADING_RE.match(line)
            if m:
                out.append(self._heading(m))
                i += 1
                continue
            if _HR_RE.match(line):
                out.append("<hr>")
                i += 1
                continue
            if line.lstrip().startswith(">"):
                i = self._blockquote(lines, i, out)
                continue
            if _UL_RE.match(line) or _OL_RE.match(line):
                i = self._list(lines, i, out)
                continue
            if "|" in line and i + 1 < n and _TABLE_SEP_RE.match(lines[i + 1]):
                i = self._table(lines, i, out)
                continue
            i = self._paragraph(lines, i, out)
        return out

    # -- leaf blocks -------------------------------------------------------
    def _heading(self, m: re.Match) -> str:
        level = max(2, len(m.group("hashes")))  # H1 is the document title; body starts at H2
        text = m.group("text").strip()
        hid = m.group("id") or slugify(text, self.used_ids)
        if m.group("id"):
            self.used_ids.add(hid)
        return f'<h{level} id="{hid}">{self.inline.run(text)}</h{level}>'

    def _fence(self, lines: list[str], i: int, m: re.Match, out: list[str]) -> int:
        fence, lang, indent = m.group("fence"), m.group("lang"), len(m.group("indent"))
        body: list[str] = []
        i += 1
        while i < len(lines) and not (lines[i].strip().startswith(fence[0] * 3) and lines[i].strip().rstrip(fence[0]) == ""):
            body.append(lines[i][indent:] if lines[i][:indent].isspace() else lines[i])
            i += 1
        cls = f' class="language-{_esc(lang)}"' if lang else ""
        out.append(f"<pre><code{cls}>{_esc(chr(10).join(body))}</code></pre>")
        return i + 1

    def _blockquote(self, lines: list[str], i: int, out: list[str]) -> int:
        inner: list[str] = []
        while i < len(lines) and (lines[i].lstrip().startswith(">") or (lines[i].strip() and inner and not _is_block_start(lines[i]))):
            s = lines[i].lstrip()
            inner.append(s[1:].lstrip() if s.startswith(">") else s)
            i += 1
        out.append("<blockquote>\n" + "\n".join(self._blocks(inner)) + "\n</blockquote>")
        return i

    def _paragraph(self, lines: list[str], i: int, out: list[str]) -> int:
        buf: list[str] = []
        while i < len(lines) and lines[i].strip() and not _is_block_start(lines[i]):
            buf.append(lines[i].rstrip("\n"))
            i += 1
            # a display-math line closes the paragraph on its own
            if _DISPLAY_MATH_RE.match(buf[-1]):
                break
        text = "\n".join(buf)
        if _DISPLAY_MATH_RE.match(text):
            body = text.strip()
            body = body[2:-2] if body.startswith("$$") else body[2:-2]
            out.append(f"<p>$${_esc(body)}$$</p>")
        else:
            out.append(f"<p>{self.inline.run(text)}</p>")
        return i

    # -- container blocks --------------------------------------------------
    def _list(self, lines: list[str], i: int, out: list[str]) -> int:
        items: list[tuple[int, str, bool, list[str]]] = []  # indent, marker-kind, ordered, content lines
        n = len(lines)
        while i < n:
            line = lines[i]
            if not line.strip():
                # blank line: list continues only if the next non-blank line is indented or another item
                j = i + 1
                while j < n and not lines[j].strip():
                    j += 1
                nxt = lines[j] if j < n else ""
                nm = _UL_RE.match(nxt) or _OL_RE.match(nxt)
                same_kind = nm is not None and (nm.re is _OL_RE) == items[0][2]
                if nxt.startswith((" ", "\t")) or (nm and (same_kind or len(nm.group("indent")) > items[0][0])):
                    items[-1][3].append("")
                    i = j
                    continue
                break
            m = _UL_RE.match(line) or _OL_RE.match(line)
            if m:
                ordered = m.re is _OL_RE
                # a top-level item of the other kind starts a new list
                if items and len(m.group("indent")) <= items[0][0] and ordered != items[0][2]:
                    break
                items.append((len(m.group("indent")), m.group("num") if ordered else "-", ordered, [m.group("text")]))
                i += 1
                continue
            if items and (line.startswith((" ", "\t"))):
                items[-1][3].append(line)
                i += 1
                continue
            break
        out.append(self._render_list(items))
        return i

    def _render_list(self, items: list[tuple[int, str, bool, list[str]]]) -> str:
        if not items:
            return ""
        base_indent = items[0][0]
        ordered = items[0][2]
        tag = "ol" if ordered else "ul"
        start = f' start="{items[0][1]}"' if ordered and items[0][1] not in ("1", "-") else ""
        parts = [f"<{tag}{start}>"]
        k = 0
        while k < len(items):
            indent, _, _, content = items[k]
            # gather nested items (deeper indent) that follow this item
            nested: list[tuple[int, str, bool, list[str]]] = []
            k2 = k + 1
            while k2 < len(items) and items[k2][0] > base_indent:
                nested.append(items[k2])
                k2 += 1
            first, rest = content[0], content[1:]
            task = _TASK_RE.match(first)
            if task:
                checked = " checked" if task.group("mark").lower() == "x" else ""
                first_html = f'<input type="checkbox" disabled{checked}> {self.inline.run(task.group("text"))}'
            else:
                first_html = self.inline.run(first)
            li = [first_html]
            trailing = [l[min(indent + 2, len(l) - len(l.lstrip())):] if l.strip() else "" for l in rest]
            if any(t.strip() for t in trailing):
                li.append("\n" + "\n".join(self._blocks(trailing)))
            if nested:
                li.append("\n" + self._render_list(nested))
            parts.append(f"<li>{''.join(li)}</li>")
            k = k2
        parts.append(f"</{tag}>")
        return "\n".join(parts)

    def _table(self, lines: list[str], i: int, out: list[str]) -> int:
        header = _split_row(lines[i])
        i += 2
        rows: list[list[str]] = []
        while i < len(lines) and lines[i].strip() and "|" in lines[i]:
            rows.append(_split_row(lines[i]))
            i += 1
        ncol = len(header)
        thead = "<tr>" + "".join(f"<th>{self.inline.run(c)}</th>" for c in header) + "</tr>"
        body = []
        for r in rows:
            r = (r + [""] * ncol)[:ncol]
            body.append("<tr>" + "".join(f"<td>{self.inline.run(c)}</td>" for c in r) + "</tr>")
        table = f"<table>\n<thead>{thead}</thead>\n<tbody>\n" + "\n".join(body) + "\n</tbody>\n</table>"
        out.append(f'<div class="table-wrap">\n{table}\n</div>' if ncol >= 4 else table)
        return i


def _split_row(line: str) -> list[str]:
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|") and not s.endswith("\\|"):
        s = s[:-1]
    cells, cur, k = [], [], 0
    while k < len(s):
        if s[k] == "\\" and k + 1 < len(s) and s[k + 1] == "|":
            cur.append("|")
            k += 2
        elif s[k] == "|":
            cells.append("".join(cur).strip())
            cur = []
            k += 1
        else:
            cur.append(s[k])
            k += 1
    cells.append("".join(cur).strip())
    return cells


def _is_block_start(line: str) -> bool:
    return bool(_FENCE_RE.match(line) or _HEADING_RE.match(line) or _HR_RE.match(line)
                or line.lstrip().startswith(">") or _UL_RE.match(line) or _OL_RE.match(line))


# ------------------------------------------------------------------ API -----

def convert(md: str, used_ids: set[str] | None = None) -> str:
    """Convert one Markdown fragment to HTML."""
    return _Block(used_ids if used_ids is not None else set()).convert(md)


def expand(content_html: str) -> tuple[str, int]:
    """Replace every MD block in a content fragment. Returns (html, block_count)."""
    used: set[str] = set(re.findall(r'\bid="([^"]+)"', content_html))
    count = 0

    def repl(m: re.Match) -> str:
        nonlocal count
        count += 1
        return convert(m.group(1).strip("\n"), used)

    pattern = re.compile(re.escape(MD_START) + r"(.*?)" + re.escape(MD_END), re.S)
    return pattern.sub(repl, content_html), count


if __name__ == "__main__":
    import sys
    print(convert(sys.stdin.read()))
