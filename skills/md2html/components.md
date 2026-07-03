# md2html — Component Catalog

This file is the **single source of truth** for the HTML snippets you (the AI) must use when filling `template.html`.

**Rules:**
- Copy snippets verbatim, only replace the bracketed `{{...}}` placeholders.
- Never invent new CSS classes — every visual element MUST be one of these components or vanilla markdown HTML (`<h2>`, `<p>`, `<ul>`, etc.).
- All sample text in this catalog is illustrative — replace with real content from the source `.md`.
- **Language follows the source**: Korean source → Korean UI labels; any other language → English UI labels. See the label table below. Body content always stays in the source language.
- **Use SVG icons via the sprite, never emojis.** All icons reference IDs defined in `template.html`'s `<svg class="icon-sprite">`. Form: `<svg class="icon" viewBox="0 0 24 24" aria-hidden="true"><use href="#i-NAME"/></svg>`. See §13 for the full catalog of available icon IDs.

## Language label table

The HTML's `<html lang="...">` attribute MUST be `ko` for Korean sources and `en` for everything else. The "Recommended" badge label is set via the `--rec-label` CSS variable on `<html>`.

```html
<!-- example: Korean source -->
<html lang="ko" data-theme="light" style="--rec-label: '★ 추천'">

<!-- example: English (or any non-Korean) source -->
<html lang="en" data-theme="light" style="--rec-label: '★ Recommended'">
```

### UI labels by language

| Key                | EN                  | KO (한국어)         |
|---                 |---                  |---                  |
| `{{TOC_TITLE}}`    | Contents            | 목차                |
| `{{REC_LABEL}}`    | ★ Recommended       | ★ 추천              |
| `{{PRINT_TOOLTIP}}`| Print / Save PDF    | 인쇄 / PDF 저장     |
| `{{THEME_TOOLTIP}}`| Toggle theme        | 테마 전환           |
| Read-time suffix   | ~N min read         | ~N분 소요           |
| Highlight label    | Key point           | 핵심                |
| Pros heading       | ✓ Pros              | ✓ 장점              |
| Cons heading       | ✕ Cons              | ✕ 단점              |
| Source: prefix     | Source:             | 소스:               |
| Brand — PLAN       | Plan                | 계획                |
| Brand — SPEC       | Spec                | 사양                |
| Brand — SYSTEM DESIGN | System Design    | 시스템 설계         |
| Brand — RFC / RUNBOOK / POSTMORTEM | (keep) | (keep)            |
| Brand — BRAINSTORM | Brainstorm          | 브레인스토밍        |
| Brand — NOTES      | Notes               | 메모                |

### Default callout titles (override with source-specific phrases when possible)

| Variant                  | EN                | KO                |
|---                       |---                |---                |
| info                     | Context           | 배경              |
| warn                     | Heads up          | 주의              |
| danger                   | Do not do this    | 금지              |
| success                  | Done              | 완료              |
| decision                 | Decision          | 결정              |
| tip                      | Tip               | 팁                |

**Notes:**
- The "Doc-type eyebrow" (`PLAN`, `SPEC`, `RFC`, `RUNBOOK`, `POSTMORTEM`, `NOTES`) stays as the uppercase English code in **all languages** — it's a universal tag, not a translatable label.
- Body content (paragraphs, step descriptions, callout bodies, headings H2/H3) is always in the source language — paraphrased but never translated to another language.
- Korean inherits `font-family: var(--font-sans)` which falls back to system fonts with CJK glyphs (Apple SD Gothic / PingFang on macOS, Malgun Gothic on Windows, Noto Sans CJK on Linux). No font change needed for correct rendering.

---

## 1. Title block (in `<header class="doc-header">`)

Replace `{{TITLE}}`, `{{SUBTITLE}}`, `{{DOC_TYPE}}`, `{{SOURCE_FILE}}`, `{{DATE}}`, `{{READ_TIME}}` in `template.html`.

- `{{DOC_TYPE}}` examples: `PLAN`, `SPEC`, `SYSTEM DESIGN`, `RFC`, `NOTES`, `RUNBOOK`, `POSTMORTEM`.
- `{{READ_TIME}}` format: `~5 min read` / `~5분 소요` (estimate ~250 words/minute; Korean: ~500 characters/minute).

---

## 2. TOC entry — goes inside `<nav class="toc-nav">`

```html
<a href="#section-id" class="lvl-2">Section name</a>
<a href="#subsection-id" class="lvl-3">Sub-section name</a>
```

- One `<a>` per H2/H3 in the document.
- The `href` must match an `id="..."` on the target heading: `<h2 id="section-id">...</h2>`.
- Use `class="lvl-2"` for top-level (H2), `class="lvl-3"` for nested (H3). Skip H4 to avoid clutter.

---

## 3. Step card / Timeline

For numbered sequences (action items, plan steps, migration steps, workflow). Wrap multiple `.step` in a `.timeline`.

```html
<div class="timeline">
  <article class="step">
    <div class="step-num">1</div>
    <div class="step-body">
      <h3>Step title</h3>
      <p>One or two short sentences: what to do and why.</p>
      <div class="step-tags">
        <span class="tag">backend</span>
        <span class="tag">~2 days</span>
      </div>
    </div>
  </article>
  <article class="step">
    <div class="step-num">2</div>
    <div class="step-body">
      <h3>Next step</h3>
      <p>...</p>
    </div>
  </article>
</div>
```

- Add `class="step done"` to mark a completed step (circle filled).
- Tags are optional — use for owner, ETA, area, dependencies.
- Keep `<h3>` short (≤ 60 chars); detail goes in `<p>`.

---

## 4. Callouts

Use for important asides. One HTML shape, six variants — pick by semantic meaning, then swap the variant class, the icon id, and the title (localized defaults in the table above).

```html
<aside class="callout callout-warn">
  <svg class="callout-icon" viewBox="0 0 24 24" aria-hidden="true"><use href="#i-warn"/></svg>
  <div class="callout-body">
    <p class="callout-title">Heads up</p>
    <p>This migration locks the <code>orders</code> table for ~30s in production.</p>
  </div>
</aside>
```

| Variant class | Icon | Use for |
|---|---|---|
| `callout-info` | `#i-info` | context, background, FYI — use `#i-lock` for security/auth notes |
| `callout-warn` | `#i-warn` | gotcha, edge case, risk |
| `callout-danger` | `#i-danger` | blocker, breaking change, must-not-do |
| `callout-success` | `#i-success` | confirmation, what's already done |
| `callout-decision` | `#i-decision` | recorded decision / ADR |
| `callout-tip` | `#i-tip` | recommendation, best practice |

---

## 5. Key-point highlight

For the single most important insight/conclusion of a section.

```html
<div class="highlight">
  <span class="highlight-label">핵심</span>
  <p>결론: 폴링을 웹훅으로 바꾸면 지연이 3분에서 5초 미만으로 줄고 API 호출이 60% 감소한다.</p>
</div>
```

- Use sparingly (≤ 1 per major section). If everything is highlighted, nothing is.
- The `highlight-label` text follows the language table (`Key point` / `핵심`).

---

## 6. Mermaid diagram (complex diagrams only)

**Simple flows do NOT belong here** — a linear chain or a single fan-out/fan-in with ≤ ~8 nodes uses the native flow component (§6b): it matches the theme, supports KaTeX in labels, and has no CDN/render flash. Use mermaid only when the structure genuinely needs a layout engine:
- "client calls server, server calls DB" (lifelines, ordered messages) → `sequenceDiagram`
- "table A has an FK to table B" → `erDiagram`
- "state machine / 상태 전이" → `stateDiagram-v2`
- "phases / roadmap / timeline" → `gantt`
- dense flowcharts: > 8 nodes, multiple branch points, or cross edges → `flowchart LR`/`TD`

`build.py` also accepts `classDiagram`, `journey`, `pie`, and `timeline` (see its `MERMAID_TYPES`) for the rarer cases; the block must start with one of these keywords, never bare `graph`.

```html
<figure class="diagram">
  <pre class="mermaid">
flowchart LR
  A[User] -->|POST /order| B(API Gateway)
  B --> C{Auth?}
  C -->|yes| D[Order Service]
  C -->|no| E[401]
  D --> F[(Postgres)]
  D --> G[/Event bus/]
  </pre>
  <figcaption class="diagram-caption">Order creation flow from user to event bus.</figcaption>
</figure>
```

**Mermaid tips for readable output:**
- Prefer `LR` (left-right) for flows with ≤ 6 nodes, `TD` for vertical hierarchies.
- Keep node labels short (≤ 3 words). Detail goes in caption.
- Use `(...)` for service/process, `[...]` for box, `[(...)]` for database, `((...)) ` for circle, `{...}` for decision, `/.../` for queue/event.
- Always add a `<figcaption>` explaining what the diagram shows.

---

## 6b. Native flow diagram (the default for simple flows)

For linear chains and single fan-out/fan-in flows (≤ ~8 nodes) — the majority of flows in real documents. Pure theme-styled HTML/CSS: light/dark aware, print-safe, no CDN, and **labels can contain KaTeX** (`\(\Lambda(x)\)`), which mermaid can't do. You may sketch the topology in mermaid mentally or on scratch, but the shipped HTML uses this component.

```html
<figure class="diagram">
  <div class="flow" role="img" aria-label="2-head 학습과 score 조립 흐름">
    <div class="flow-node">win(IMP) 로그 <small>입력 \(x\)</small></div>
    <div class="flow-arrow" aria-hidden="true"></div>
    <div class="flow-node">HyFormer backbone</div>
    <div class="flow-arrow" aria-hidden="true"></div>
    <div class="flow-row">
      <div class="flow-node">\(\Lambda(x)\) head <small>Poisson NLL</small></div>
      <div class="flow-node">\(m_{\mathrm{gap}}(x)\) head <small>regression</small></div>
    </div>
    <div class="flow-arrow" aria-hidden="true"><span class="flow-arrow-label">곱으로 조립</span></div>
    <div class="flow-node flow-node-accent">\(s_i \propto \mathbb{E}[K_i]\cdot m_{\mathrm{gap},i}\)</div>
  </div>
  <figcaption class="diagram-caption">2-head 학습과 score 조립 흐름.</figcaption>
</figure>
```

**Building blocks:**

| Class | Role |
|---|---|
| `.flow` | container, vertical (top-down). Add `flow-lr` for horizontal. |
| `.flow-node` | one box. `<small>` inside = secondary line. KaTeX OK. |
| `.flow-node-accent` | highlighted box (result/outcome) — use once, at most. |
| `.flow-arrow` | connector between siblings. Optional `<span class="flow-arrow-label">label</span>` inside. |
| `.flow-row` | parallel branches (fan-out): put 2-4 `.flow-node` inside, between two `.flow-arrow`s. |

**Rules:**
- Alternate node/arrow as direct children of `.flow`: node, arrow, node, arrow, …
- `role="img"` + `aria-label` describing the flow on the `.flow` container; `aria-hidden="true"` on arrows.
- Keep node text short (≤ 6 words); detail goes in `<small>` or the `<figcaption>`.
- Needs more than one `.flow-row` level of branching, back-edges, or > ~8 nodes? It's not a simple flow — use mermaid (§6).

---

## 6c. Wireframe mockup (UI/layout descriptions)

When the source *describes a screen* — "상단에 네비게이션, 좌측에 메뉴, 메인에 카드 3개" — prose makes the reader rebuild the layout in their head. Render it as a wireframe instead: structure over pixels, placeholder for content areas. The reader sees the screen in one glance.

```html
<figure class="diagram">
  <div class="mockup" role="img" aria-label="대시보드 화면 구성">
    <div class="mockup-header">Pool 현황 대시보드</div>
    <div class="mockup-body">
      <div class="mock-nav">로고 · adset 선택 · 기간 · <span class="mock-button">새로고침</span></div>
      <div class="mock-row">
        <div class="mock-sidebar">
          <ul>
            <li class="active">Pool 현황</li>
            <li>Score 분포</li>
            <li>제약 모니터링</li>
          </ul>
        </div>
        <div class="mock-content">
          <div class="placeholder">기회량 / 지출 / ROAS 카드 3개</div>
        </div>
      </div>
    </div>
  </div>
  <figcaption class="diagram-caption">대시보드 레이아웃 — 메뉴별 화면은 §2 참조.</figcaption>
</figure>
```

**Building blocks:**

| Class | Role |
|---|---|
| `.mockup` + `.mockup-header` + `.mockup-body` | framed screen with a title bar |
| `.mock-nav` | top navigation bar |
| `.mock-row` | horizontal band (sidebar + content) |
| `.mock-sidebar` (`<li class="active">` = selected) | side menu |
| `.mock-content` | main area |
| `.mock-button`, `.mock-input` | interactive element stand-ins |
| `.placeholder` | hatched box for "content goes here" areas |
| `.split` | two mockups side-by-side (layout A vs B, before/after) |

**Rules:**
- **Structure over pixel fidelity** — a wireframe answers "what goes where", not "what does it look like". Use `.placeholder` for anything that's content, not layout.
- Label every region with the source's own terms (menu names, button labels verbatim — Critical rule 1 applies to UI text too).
- For "layout A vs B" decisions, put two `.mockup`s in `.split` and mark the chosen one in the caption or with a decision callout — same logic as comparison cards (§8).
- Wrap in `<figure class="diagram">` + `<figcaption>` like other diagrams.
- One mockup per screen. A multi-screen journey = flow (§6b) of screen names, plus a mockup for the 1-2 screens the document actually details.
- No inline `style=` attributes — these classes are the whole vocabulary.

---

## 7. Pros / Cons table

For trade-off discussions ("Trade-offs of X…" / "X의 장단점…").

```html
<div class="proscons">
  <div class="proscons-col pros">
    <h4>✓ 장점</h4>
    <ul>
      <li>스키마 변경 없이 빠르게 배포할 수 있다.</li>
      <li>기존 클라이언트와 하위 호환된다.</li>
    </ul>
  </div>
  <div class="proscons-col cons">
    <h4>✕ 단점</h4>
    <ul>
      <li>라우팅 레이어 복잡도가 올라간다.</li>
      <li>한 분기 동안 코드 경로 2개를 유지해야 한다.</li>
    </ul>
  </div>
</div>
```

- The `<h4>` text follows the language table (`✓ Pros` / `✓ 장점`, `✕ Cons` / `✕ 단점`).

---

## 8. Comparison cards

For "Option A vs B vs C" — when there are ≥ 2 alternatives to compare.

```html
<div class="compare">
  <div class="compare-card recommended">
    <h4>Option B — Hybrid cache</h4>
    <p>Redis L1 + DB fallback. Balances latency and complexity.</p>
  </div>
  <div class="compare-card">
    <h4>Option A — DB only</h4>
    <p>Simplest but p99 latency hits 800ms at peak.</p>
  </div>
  <div class="compare-card">
    <h4>Option C — In-memory map</h4>
    <p>Fastest but loses state on restart, no horizontal scaling.</p>
  </div>
</div>
```

- Add `class="recommended"` to the preferred option → ★ badge appears automatically. The badge text comes from `--rec-label` set on `<html style="...">` (see the language table above). Falls back to `★ Recommended` if not set.
- Put the recommended option **first** so the reader sees it immediately.
- All body text follows the source language — the sample above is English; for a Korean source, write descriptions in Korean.

---

## 9. Collapsible section

For optional / deep-dive content the reader can skip.

```html
<details class="collapsible">
  <summary>Technical details of the sharding strategy</summary>
  <div class="collapsible-body">
    <p>Consistent hashing with 256 virtual nodes per physical shard...</p>
    <pre><code>const shard = hash(userId) % SHARDS;</code></pre>
  </div>
</details>
```

**When to collapse:**
- Long code blocks (> 30 lines)
- Background context not every reader needs
- Alternative approaches that were rejected
- Detailed FAQ

---

## 10. Plain Markdown elements

These render correctly out-of-the-box with the CSS in `template.html` — just use HTML equivalents:

| Markdown | HTML to write |
|---|---|
| `## Heading` | `<h2 id="kebab-case-id">Heading</h2>` |
| `### Sub` | `<h3 id="kebab-case-id">Sub</h3>` |
| `**bold**` | `<strong>bold</strong>` |
| `inline code` | `<code>inline code</code>` |
| ```` ```js code``` ```` | `<pre><code>js code</code></pre>` |
| `- item` | `<ul><li>item</li></ul>` |
| `1. item` | `<ol><li>item</li></ol>` (only when it is NOT a timeline) |
| `> quote` | `<blockquote>quote</blockquote>` |
| `--- table ---` | `<table>...</table>` |
| `[text](url)` | `<a href="url">text</a>` |

---

## 11. Component selection cheatsheet

Apply these heuristics while reading the source `.md`:

| Pattern in source | Component to use |
|---|---|
| Numbered list of action items (`1. do X`, `2. do Y`) | Step / Timeline (§3) |
| Simple flow: linear chain or one fan-out/fan-in, ≤ ~8 nodes | Native flow (§6b) |
| "Client → Server → DB" in text | Native flow (§6b) |
| Screen/layout description ("상단 네비, 좌측 메뉴, 메인 영역…") | Wireframe mockup (§6c) |
| "Layout A vs B" visual decision | Two mockups in `.split` (§6c) |
| Complex flow: > 8 nodes, multi-branch, cross edges | Mermaid flowchart (§6) |
| Message exchange with ordering (lifelines) | Mermaid sequenceDiagram (§6) |
| Schema / ERD description | Mermaid erDiagram (§6) |
| "Pros / Cons", "장점 / 단점", "Trade-offs" | Pros-Cons (§7) |
| "Option A / B / C", "Approaches" | Comparison cards (§8) |
| Conclusion / TL;DR of an important section | Key-point highlight (§5) |
| "Note", "FYI", "Background", "참고" | Callout, `callout-info` variant (§4) |
| "Careful", "Gotcha", "Risk", "주의" | Callout, `callout-warn` variant (§4) |
| "MUST NOT", "절대 금지" | Callout, `callout-danger` variant (§4) |
| "Done", "Completed", "완료" | Callout, `callout-success` variant (§4) |
| "Decision", "Chose X over Y", "결정" | Callout, `callout-decision` variant (§4) |
| "Recommendation", "Best practice", "팁" | Callout, `callout-tip` variant (§4) |
| Long code / appendix / FAQ | Collapsible (§9) |
| Short comparison table (≤ 4 columns) | Markdown table (§10) |
| LaTeX math (`$...$`, `$$...$$`, `\(...\)`, `\[...\]`) | KaTeX math (§15) — never `<code>` |

---

## 12. Anti-patterns — don't do these

- ❌ Don't use emoji as icons (ℹ️ ⚠️ ⛔ 🎯 …). Use SVG `<use href="#i-...">` from the sprite — emoji render differently across OSes, don't recolor with the theme, and break the minimal tone.
- ❌ Don't wrap EVERYTHING in callouts/highlights — it dilutes the emphasis.
- ❌ Don't use `<ol>` for plan steps — use `.timeline` instead.
- ❌ Don't make mermaid too complex (> 15 nodes) — split into multiple small diagrams.
- ❌ Don't ship a plain mermaid flowchart for a simple linear/fan-out flow — use the native flow component (§6b). It matches the theme, prints reliably, renders KaTeX labels, and has no CDN flash.
- ❌ Don't inline-style — every style already lives in `template.html`.
- ❌ Don't forget `id` on headings — the TOC and anchor links break.
- ❌ Don't add `<script>` tags or load external libraries.
- ❌ Don't translate the Markdown line by line — ANALYZE first, then pick a component.
- ❌ Don't use `<h1>` in body content — `.doc-title` is already the H1; use H2/H3 for sections.
- ❌ Don't render math as `<code>`/unicode approximation (`E[K_i]·m_i`) — subscripts and operators get destroyed and the document's technical core flattens. Use KaTeX delimiters (§15).

---

## 13. Icon sprite catalog

`template.html` defines an SVG sprite with 18 Lucide-style icons. Reference them with `<use href="#i-NAME"/>`. Icons inherit `currentColor`, so they automatically match the parent's color — no separate `fill`/`stroke` needed.

| Icon ID         | Shape                       | Used for                                              |
|---              |---                          |---                                                    |
| `#i-info`       | Circle with "i"             | Callout info, background notes                        |
| `#i-warn`       | Warning triangle with "!"   | Callout warn, risk, gotcha                            |
| `#i-danger`     | No-entry circle             | Callout danger, must-not-do                           |
| `#i-success`    | Circle with check           | Callout success, completed                            |
| `#i-decision`   | Bullseye / target           | Callout decision, ADR                                 |
| `#i-tip`        | Light bulb                  | Callout tip, best practice                            |
| `#i-lock`       | Padlock                     | Security/auth notes (with callout-info)               |
| `#i-printer`    | Printer                     | Print button (already in topbar)                      |
| `#i-moon`       | Moon                        | Theme toggle, light mode active                       |
| `#i-sun`        | Sun                         | Theme toggle, dark mode active                        |
| `#i-menu`       | Hamburger                   | Mobile TOC trigger (already in topbar)                |
| `#i-x`          | X mark                      | Close drawer / dismiss                                |
| `#i-file`       | File document               | doc-meta source file                                  |
| `#i-calendar`   | Calendar                    | doc-meta date                                         |
| `#i-clock`      | Clock                       | doc-meta read time                                    |
| `#i-copy`       | Two stacked squares         | Copy-to-clipboard (auto-injected on `<pre>`)          |
| `#i-check`      | Check mark ✓                | "Copied" state, completed                             |
| `#i-link`       | Chain link                  | Anchor link on headings (auto-injected)               |

**Standard sizes**: 18-20px for callouts, 14px for doc-meta, 16-18px for topbar buttons. Set via the `.icon` CSS size or width/height attributes.

**If you need an icon that isn't in the sprite**: do NOT add one to the template. Use the closest icon from the catalog. If a new icon is truly needed, tell the user so it can be added to the template.

---

## 14. Edge-case patterns

### 14a. Images
```html
<figure>
  <img src="path/to/image.png" alt="Short description of the image content">
  <figcaption>Architecture diagram of the 3-broker Kafka cluster.</figcaption>
</figure>
```
- `alt` MUST describe the content (never "image" or empty). Decorative images → `alt=""`.
- Images are responsive automatically (`max-width: 100%`), border-radius matches the theme.

### 14b. Wide tables (many columns → need horizontal scroll on mobile)
```html
<div class="table-wrap">
  <table>
    <thead>
      <tr><th>Col 1</th><th>Col 2</th><th>Col 3</th><th>Col 4</th><th>Col 5</th></tr>
    </thead>
    <tbody>
      <tr><td>...</td><td>...</td><td>...</td><td>...</td><td>...</td></tr>
    </tbody>
  </table>
</div>
```
- Wrap in `.table-wrap` when the table has **≥ 4 columns** or long cell text.
- Simple tables (≤ 3 columns, short text) can use a plain `<table>` — CSS handles overflow-x.

### 14c. Task lists (checkboxes)
```html
<ul>
  <li class="task-list-item"><input type="checkbox" class="task-list-item-checkbox" disabled> Not done yet</li>
  <li class="task-list-item"><input type="checkbox" class="task-list-item-checkbox" disabled checked> Already done</li>
</ul>
```
- Use when the source `.md` has `- [ ]` / `- [x]`. Checkboxes are `disabled` because the HTML is read-only.

### 14d. Footnotes
```html
<p>Text with a footnote<sup class="footnote-ref"><a href="#fn1" id="fnref1">1</a></sup>.</p>

<!-- end of document -->
<ol class="footnotes">
  <li id="fn1">Footnote 1 content. <a href="#fnref1">↩</a></li>
</ol>
```

### 14e. Very long title (≥ 80 chars)
The title auto-wraps (`text-wrap: balance`) with responsive `clamp(28px, ...)` font-size. Nothing extra needed.

### 14f. Empty TOC (source has no H2)
JS auto-hides `<aside class="toc">` when `#toc-nav` has no links. Nothing extra needed.

### 14g. Long URLs / identifiers
`.content` already has `overflow-wrap: anywhere` — long URLs/identifiers wrap without breaking the layout.

---

## 15. Math (KaTeX)

`template.html` ships KaTeX (CDN, same graceful-degradation policy as Mermaid — offline shows raw LaTeX). Use it whenever the source contains LaTeX math: `$...$`, `$$...$$`, `\(...\)`, `\[...\]`.

The auto-renderer recognizes ONLY these delimiters in the output HTML:

| Kind | Write in content.html | Source mapping |
|---|---|---|
| Inline | `\( m_{\mathrm{gap}} \)` | `$...$` and `\(...\)` → `\(...\)` |
| Display | `$$ ... $$` in its own `<p>` | `$$...$$` and `\[...\]` → `$$...$$` |

Single-`$` is deliberately NOT a delimiter, so literal dollar amounts in prose stay safe — that's why you must convert source `$...$` to `\(...\)`.

```html
<!-- inline math inside a sentence -->
<p>최적 bid는 \(b^*=v/\mu\)다. 즉 \(v\approx\mu b\)이고, 낙찰 한 번의 surplus는</p>

<!-- display math: own paragraph, LaTeX body kept verbatim -->
<p>$$ v-\mu p\;\approx\;\mu(b-p). $$</p>
```

**Rules:**

- **LaTeX body stays verbatim** — only the delimiters change. Never "simplify" `m_{\mathrm{gap}}` to `m_gap`, `\mathbb{E}` to `E`, or `\le` to `≤`. The notation IS the content.
- **Math and code are disjoint.** KaTeX skips `<pre>`/`<code>`, so math placed there never renders. Conversely, real code/columns/identifiers (`bidprice`, `idno × placementgroup`) stay `<code>` — don't dress code up as math.
- **HTML-escape inside math**: `<` → `&lt;`, `>` → `&gt;`, `&` → `&amp;` (KaTeX reads the decoded text, so `\{k : \Delta_k \ge \tau\}` with `&lt;`/`&gt;` renders correctly).
- A display equation in the middle of a source paragraph: split the paragraph — prose `<p>`, then `<p>$$...$$</p>`, then the continuation `<p>`.
- Math works inside `<li>`, table cells, callouts, and highlights — the renderer walks the whole `.content` DOM.
- **Mermaid node labels and headings can't use KaTeX.** Inside diagrams use plain unicode (`Λ(x) head — Poisson NLL`). Same for `<h2>`/`<h3>` text: the TOC sidebar copies heading text outside the renderer's scope, so a heading like `3.3 $\Lambda$ / $\mathbb{E}[K]$` becomes `3.3 Λ / E[K]` in both the heading and its TOC entry. These are the only places unicode math notation is right.
