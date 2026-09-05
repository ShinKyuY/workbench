---
name: md2html
description: Use when turning long-form Markdown (plans, specs, RFCs, runbooks, notes) into one themed HTML file to read or share — supports KaTeX math, flow diagrams, wireframe mockups, sidebar TOC, Korean/English UI. Portable across Claude Code / Codex / any AI agent.
trigger: /md2html
---

# /md2html

Convert a verbose Markdown document into a single HTML file that a tired
human can actually scan: diagrams instead of paragraphs, step cards
instead of numbered lists, callouts for the parts that matter.

## Usage

```
/md2html <file.md>             # output <file>.html next to source
/md2html <file.md> --out X.html # custom output path
/md2html                       # if no arg, ask user which file
```

## Skill files (resolved relative to this SKILL.md)

- `template.html`   — HTML skeleton with embedded CSS (Claude orange light+dark), SVG diagram marker defs, theme toggle, TOC sidebar, footer. Contains `{{PLACEHOLDER}}` strings and `<!-- COMMENT -->` slots. **Do NOT read this file** — its contract (placeholder list + content slots) is fully documented below, and `scripts/build.py` does the assembly. Reading 1,200 lines of CSS wastes context and tempts you to re-type it, which is the #1 source of drift and cost.
- `components.md`  — catalog of HTML snippets you must copy verbatim (step cards, callouts, SVG diagram recipes, pros-cons, comparison cards, collapsibles). **Read this in full before writing content.** Do not invent CSS classes or skip the catalog.
- `scripts/build.py` — assembler. Takes your metadata JSON + TOC fragment + content fragment, converts the Markdown you pasted inside `<!-- MD -->…<!-- /MD -->` blocks (via `scripts/md_passthrough.py`), merges everything into `template.html`, and verifies the result (leftover placeholders, broken anchors, SVG diagram structure and label widths, raw `<` in math/code, emoji, math delimiters, math-as-code; optional headless-Chrome render check). You author only the component sections; it does the mechanics.
- `examples/`     — reference `<doc>.md` → `<doc>.html` pairs. Optional calibration: if unsure what good output looks like, read only the part of an example `.html` between `<!-- CONTENT_START -->` and `<!-- CONTENT_END -->`.

## What you must do when invoked

Follow these steps in order. Do not skip.

### Step 1 — Resolve inputs

1. Determine the source file from the user's invocation. If none given, ask which `.md` file to convert (in the language of the conversation) and stop.
2. Read the source `.md` fully.
3. Read `components.md` from the same directory as this SKILL.md. Do not read `template.html` (see above).

### Step 2 — Analyze the source document

Do this analysis silently in your head (or as one short summary line to the user). Identify:

- **Language of the source** — detect from the actual prose, not the filename. Korean source → `<html lang="ko">` + Korean UI labels; any other language → `<html lang="en">` + English UI labels. Body content always stays in the source language.

  | Key            | EN                 | KO (한국어)         |
  |---             |---                 |---                  |
  | TOC title      | Contents           | 목차                |
  | Read-time      | ~N min read        | ~N분 소요           |
  | Recommended    | ★ Recommended      | ★ 추천              |
  | Key point      | Key point          | 핵심                |
  | Pros           | ✓ Pros             | ✓ 장점              |
  | Cons           | ✕ Cons             | ✕ 단점              |
  | Print tooltip  | Print / Save PDF   | 인쇄 / PDF 저장     |
  | Theme tooltip  | Toggle theme       | 테마 전환           |
  | Source: prefix | Source:            | 소스:               |

  The "Recommended" badge is configured via the `--rec-label` CSS variable set on `<html>` (no per-language CSS needed) — see `{{REC_LABEL}}` below.

- **Title** — from first H1 or filename. Title should be ≤ 80 chars.
- **Subtitle** — first paragraph after H1, or the document's TL;DR sentence. ≤ 200 chars.
- **Doc type** — infer one of: `PLAN`, `SPEC`, `SYSTEM DESIGN`, `RFC`, `RUNBOOK`, `POSTMORTEM`, `BRAINSTORM`, `NOTES`. Pick the closest match based on the document's *purpose*, not its filename. Brainstorm = exploring options with rationale; Plan = ordered steps to a goal; Spec = exact behavior contract; System design = architecture + tradeoffs; RFC = proposal seeking feedback; Runbook = operational procedure; Postmortem = incident review. The uppercase code in the eyebrow stays universal; the topbar `BRAND_LABEL` localizes (Plan / 계획).
- **Reading time** — words ÷ 250, round to nearest minute. For Korean sources whitespace word-counting undercounts badly — use characters ÷ 500 instead. Format follows the language table: `~N min read` / `~N분 소요`.
- **Math presence** — scan for LaTeX delimiters (`$...$`, `$$...$$`, `\(...\)`, `\[...\]`). If present, every formula goes through KaTeX per Critical rule 2 and §15 in `components.md`.
- **Section map** — walk each H2/H3 and tag with the BEST component using §11 cheatsheet in `components.md`. The deciding test for visual vs text: **would the reader understand this section better by seeing it than by reading it?** Layouts, flows, state machines, schemas → visual; requirements, tradeoffs, conceptual choices → text components. A section *about* a UI is not automatically visual — "어떤 위저드를 만들까" is conceptual (text), "위저드 화면 구성은 이렇다" is visual (wireframe).
  - numbered action list → Timeline
  - architecture/flow prose → Native flow component (§6b) for simple flows (linear / one fan-out, ≤ ~8 nodes); SVG diagram (§6) for dense flowcharts, sequence, ER, state, architecture; roadmaps/gantt → Timeline
  - screen/layout description → Wireframe mockup (§6c); "layout A vs B" → two mockups in `.split`
  - LaTeX math → KaTeX (§15), display equations stay display
  - "pros/cons", "장점/단점" → Pros-Cons
  - "option A vs B" → Comparison cards. If the document records a decision, put `class="recommended"` on the chosen card (★ badge) — even when each option also lists pros/cons. The reader must see which option won without hunting through prose.
  - critical conclusion → Key-point highlight
  - warnings/decisions → Callouts
  - long appendix → Collapsible
  - everything else → paste the source Markdown as an MD block (Step 3); `build.py` converts it

### Step 3 — Build the output HTML

You write three small part files; `scripts/build.py` merges them into `template.html` and verifies the result.

1. **Write `<output-dir>/.md2html-parts/meta.json`** — one value per template placeholder (all values come from Step 2 analysis, language-matched):
   - `{{LANG}}` → `ko` for Korean sources, `en` otherwise
   - `{{REC_LABEL}}` → text shown on the "Recommended" comparison-card badge: `★ Recommended` / `★ 추천`. Sets the `--rec-label` CSS variable on `<html>`. If you forget this, CSS falls back to `★ Recommended`.
   - `{{TITLE}}` (appears twice: `<title>` and `.doc-title`)
   - `{{SUBTITLE}}`
   - `{{DOC_TYPE}}` → universal uppercase code: `PLAN`, `SPEC`, `SYSTEM DESIGN`, `RFC`, `RUNBOOK`, `POSTMORTEM`, `BRAINSTORM`, `NOTES`
   - `{{SOURCE_FILE}}` → basename of source (e.g. `plan.md`)
   - `{{DATE}}` → ISO date or localized "Updated <today>"
   - `{{READ_TIME}}` → localized reading time, e.g. `~3 min read` / `~3분 소요`
   - `{{BRAND_LABEL}}` → localized doc-type label for the topbar
   - `{{TOC_TITLE}}` → localized "Contents" (also used as `aria-label` for the TOC drawer)
   - `{{PRINT_TOOLTIP}}` → localized print tooltip
   - `{{THEME_TOOLTIP}}` → localized theme-toggle tooltip
   - `{{CLOSE_LABEL}}` → localized "Close" (used for the mobile TOC drawer close button): `Close` / `닫기`
   - `{{SKIP_LINK_LABEL}}` → localized skip-to-content link text: `Skip to content` / `본문 바로가기`
   - `{{FOOTER_NOTE}}` → localized source attribution: `Source: plan.md` / `소스: plan.md`
2. **Write `<output-dir>/.md2html-parts/toc.html`** — one `<a>` per H2/H3 (see §2 in components.md). Heading ids follow one rule everywhere: lowercase, runs of non-alphanumerics → `-`, Hangul kept (`## 목표와 범위` → `목표와-범위`, `## Goals & scope` → `goals-scope`). Markdown blocks get their ids from this rule automatically; to pin one, write `## Title {#my-id}`. Skip this file for very short documents (see Edge cases).
3. **Write `<output-dir>/.md2html-parts/content.html`** — the document body, section by section. For each H2 section decide once:
   - **Component section** (flow, timeline, wireframe, cards, callout, pros-cons — anything from the §11 cheatsheet): hand-write HTML with the snippets in `components.md`. Start with `<h2 id="...">`, ONE primary component per logical chunk, math per Critical rule 2.
   - **Everything else — the default**: paste the section's source Markdown **verbatim** between `<!-- MD -->` and `<!-- /MD -->`. `build.py` converts headings (with ids), paragraphs, lists, task lists, tables (≥ 4 columns get `.table-wrap`), code fences, blockquotes, inline code/bold/links, and math (`$…$` → `\(…\)`, `$$…$$` stays display). Raw HTML inside an MD block is escaped, not passed through. Never retype these sections as HTML by hand — transcription is where table rows and numbers get lost.
   - Preserve original meaning in the component sections — do not summarize away technical detail; condense only filler/repetition. md2html **restructures**, it does not **abridge**: a reader holding only the HTML must be able to reconstruct every claim, definition, derivation step, number, and caveat of the source. If a sentence feels "too detailed to keep", that's usually the sentence the author cared about most.
4. **Fidelity sweep** — before building, re-walk the source against the **component sections** of `content.html` (MD blocks are verbatim, so they need no sweep) and check off: every display equation still a display equation, every inline formula still math, every table row, list item, numeric fact, file/column name, and cross-reference present. Fix gaps now — this catch-step is cheap, a thin output is a rewrite.
5. **Run the assembler** (script path relative to this SKILL.md):

   ```bash
   python3 <skill-dir>/scripts/build.py \
     --meta <parts>/meta.json --toc <parts>/toc.html \
     --content <parts>/content.html --out <output>.html --render-check
   # short doc without a sidebar: omit --toc and add --no-toc
   ```

   It converts the MD blocks, substitutes placeholders, injects your fragments, then verifies: no leftover `{{PLACEHOLDER}}`, every anchor resolves to an `id`, every `svg.dg` has the fixed root tag, is well-formed, references only the shared markers, keeps text inside known containers, and every node label fits its shape (width estimate), no raw `<` inside math or `<pre><code>` (write `&lt;` — the browser otherwise parses `<y…` as a tag and the text vanishes), no emoji glyphs, balanced math delimiters (`\(`/`\)`, even `$$` count), and no math-like unicode squeezed into `<code>` spans. `--render-check` then loads the file in headless Chrome/Chromium/Edge and fails on any KaTeX error, a diagram label that overflows its node, or a diagram drawn outside its viewBox — always pass it; when no browser is installed it prints "render check skipped" and the static checks stand alone. On `BUILD FAILED`, fix the named problem in your part file and re-run. If the math-glyph check flags a `<code>` span that is genuinely code (a unit like `10μs`, a variable named `λ`), re-run with `--allow-unicode-math-in-code` instead of rewriting it as math. On `BUILD OK`, delete the `.md2html-parts/` directory.

   **Fallback** — if `python3` is unavailable in your environment: read `template.html`, build the full output buffer in memory (placeholders + TOC + content slot between `<!-- CONTENT_START -->` and `<!-- CONTENT_END -->`), `Write` once, and run the checks listed above (leftover placeholders, anchors, SVG diagram rules (§6), emoji, math delimiters, math glyphs in `<code>`) manually by re-reading your generated sections.

### Step 4 — Report

`build.py` already verified the structure and, with `--render-check`, the rendering (that's its exit condition), so don't re-read the output file. Report back to the user with:
- Output file path
- 1-line summary of what changed (e.g. *"Rendered 7 sections: 1 SVG sequence diagram, 2 step timelines, 4 callouts. ~6 min read."* — written in the conversation language)
- A reminder they can open it with `xdg-open <file>.html` (Linux) / `open <file>.html` (mac).

## Critical rules

1. **Never paraphrase technical content into vague prose.** A step `0042_user_schema.sql 마이그레이션 실행` must keep that exact filename — don't change it to `새 마이그레이션 실행`.
2. **Math renders via KaTeX — never as `<code>`/unicode approximation.** Inline `$x$` → `\(x\)`, display `$$...$$` stays display in its own `<p>`, LaTeX body verbatim (`m_{\mathrm{gap}}` stays `m_{\mathrm{gap}}`). Escape `<` `>` `&` inside math. See `components.md` §15.
3. **One component per chunk.** Don't wrap a callout inside a step card inside a collapsible. Keep nesting flat.
4. **Diagram > prose for any flow ≥ 3 hops.** Simple flows ship as the native flow component (§6b); dense flowcharts, sequence, ER, state and architecture diagrams are hand-drawn inline SVG per `components.md` §6. Never a rendering library.
5. **Key-point highlights are rare.** Max 1 per H2 section, ideally 2-3 total per document.
6. **UI text follows the detected source language** — Korean source → Korean labels, anything else → English labels (see the table in Step 2). Code, commands, file names, library names, error messages stay verbatim regardless of language.
7. **Single-file output with known CDN hooks.** No external references
   beyond what `template.html` already ships (KaTeX CDN + Google Fonts,
   both degrade gracefully offline). Never add more.
8. **Do not modify `template.html`, `components.md`, or `scripts/build.py`** — those are the skill's source of truth. Only write the part files and the output `.html`.
9. **Use SVG icons only — never emojis.** Every icon is `<svg class="..."><use href="#i-NAME"/></svg>` referencing the sprite at the top of `<body>`. See §13 in `components.md` for the catalog. No emoji glyphs anywhere in callouts, doc-meta, topbar, or body content.
10. **Anchor links and copy-to-clipboard auto-inject via JS** — do NOT add them manually. Just give H2/H3 a proper `id`, and put code in `<pre><code>`. The template's boot script handles the rest.
11. **Wrap wide tables in `.table-wrap`** — see components.md §14b. Tables ≥ 4 columns or with long cells need the wrapper for mobile scroll.
12. **Use `<figure>` + `<figcaption>` for images** with descriptive `alt`. See components.md §14a.

## Cross-AI compatibility

Runs identically on Claude Code (`~/.claude/skills/md2html/`, invoke
with `/md2html <file>`), Codex CLI (SKILL.md copied to
`~/.codex/prompts/md2html.md`, support files kept at a stable path),
and any agent with Read/Write access to this folder. Only runtime
dependency: `python3` (stdlib only) for `scripts/build.py` — if truly
missing, use the Step 3 manual fallback. KaTeX and fonts resolve
from the CDNs declared in `template.html` and degrade gracefully
offline; no npm/pip install.

## Edge cases

- **Source has no headings** — wrap content in one `<h2 id="content">Content</h2>` (KO: `내용`) and infer logical breaks from blank lines + topic shifts.
- **Source has existing mermaid code blocks** — if it's a simple flowchart (linear / one fan-out, ≤ ~8 nodes), convert it to the native flow component (§6b); anything else is redrawn as an SVG diagram (§6) from the same nodes and edges. Never paste mermaid source into the output.
- **Source has HTML embedded** — pass through as-is inside `<div>` if safe, else escape.
- **Source is very short (< 200 words, or < 400 characters for CJK)** — skip the TOC sidebar: omit `--toc` and pass `--no-toc` to `build.py` (it removes the sidebar and the mobile drawer trigger for you).
- **Source is very long (> 5000 words)** — collapse low-priority sections by default with `<details>`.
- **Output file already exists** — overwrite. The source `.md` is canonical; HTML is regenerated artifact.

## Anti-patterns

- ❌ Re-typing `template.html` into the output (or assembling it via many Edit calls) — slow, expensive, and one typo silently breaks CSS/JS. Always go through `scripts/build.py`.
- ❌ Adding new CSS via `<style>` or editing `template.html` — use only the classes in `components.md`. If a style is truly missing, tell the user so it can be added to the template.
- ❌ Translating proper nouns or code identifiers.
- ❌ "Improving" the source by adding info not in the original.
- ❌ Reporting success without `BUILD OK` from `build.py` (or, in the fallback, the manual Step 3 checks).
