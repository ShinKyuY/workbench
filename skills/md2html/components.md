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

Use for important asides. Pick the variant that matches semantic meaning.

### 4a. Info — context, background, FYI
```html
<aside class="callout callout-info">
  <svg class="callout-icon" viewBox="0 0 24 24" aria-hidden="true"><use href="#i-info"/></svg>
  <div class="callout-body">
    <p class="callout-title">Context</p>
    <p>The current system polls every 5 minutes, adding ~3 minutes of end-to-end delay.</p>
  </div>
</aside>
```

### 4b. Warning — gotcha, edge case, risk
```html
<aside class="callout callout-warn">
  <svg class="callout-icon" viewBox="0 0 24 24" aria-hidden="true"><use href="#i-warn"/></svg>
  <div class="callout-body">
    <p class="callout-title">Heads up</p>
    <p>This migration locks the <code>orders</code> table for ~30s in production.</p>
  </div>
</aside>
```

### 4c. Danger — blocker, breaking change, must-not-do
```html
<aside class="callout callout-danger">
  <svg class="callout-icon" viewBox="0 0 24 24" aria-hidden="true"><use href="#i-danger"/></svg>
  <div class="callout-body">
    <p class="callout-title">Do not do this</p>
    <p>Never drop the column before the old deploy has fully rolled out.</p>
  </div>
</aside>
```

### 4d. Success — confirmation, what's already done
```html
<aside class="callout callout-success">
  <svg class="callout-icon" viewBox="0 0 24 24" aria-hidden="true"><use href="#i-success"/></svg>
  <div class="callout-body">
    <p class="callout-title">Done</p>
    <p>The new API passed a 10k RPS load test, p99 = 80ms.</p>
  </div>
</aside>
```

### 4e. Decision — recorded decision / ADR
```html
<aside class="callout callout-decision">
  <svg class="callout-icon" viewBox="0 0 24 24" aria-hidden="true"><use href="#i-decision"/></svg>
  <div class="callout-body">
    <p class="callout-title">Decision</p>
    <p>Chose Postgres over MongoDB because the payment flow needs ACID transactions.</p>
  </div>
</aside>
```

### 4f. Tip — recommendation, best practice
```html
<aside class="callout callout-tip">
  <svg class="callout-icon" viewBox="0 0 24 24" aria-hidden="true"><use href="#i-tip"/></svg>
  <div class="callout-body">
    <p class="callout-title">Tip</p>
    <p>Cache this query for 5 minutes to cut DB load by 80%.</p>
  </div>
</aside>
```

### 4g. Security — using lock icon for auth/security notes
```html
<aside class="callout callout-info">
  <svg class="callout-icon" viewBox="0 0 24 24" aria-hidden="true"><use href="#i-lock"/></svg>
  <div class="callout-body">
    <p class="callout-title">Security</p>
    <p>The webhook runs inside the VPC and never crosses the public internet.</p>
  </div>
</aside>
```

---

## 5. Key-point highlight

For the single most important insight/conclusion of a section.

```html
<!-- EN -->
<div class="highlight">
  <span class="highlight-label">Key point</span>
  <p>Bottom line: moving from polling to webhooks cuts latency from 3 minutes to &lt;5s and saves 60% of API calls.</p>
</div>

<!-- KO -->
<div class="highlight">
  <span class="highlight-label">핵심</span>
  <p>결론: 폴링을 웹훅으로 바꾸면 지연이 3분에서 5초 미만으로 줄고 API 호출이 60% 감소한다.</p>
</div>
```

- Use sparingly (≤ 1 per major section). If everything is highlighted, nothing is.
- The `highlight-label` text comes from the language label table above.

---

## 6. Mermaid diagram

Detect these patterns in the source `.md` and convert them:
- "flow / 흐름 / step A → step B → step C" → `flowchart LR` or `flowchart TD`
- "client calls server, server calls DB" → `sequenceDiagram`
- "table A has an FK to table B" → `erDiagram`
- "state machine / 상태 전이" → `stateDiagram-v2`
- "phases / roadmap / timeline" → `gantt`

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

**Convert architecture description to mermaid:**
> "The client calls the API Gateway. The gateway verifies the JWT, then routes to the Order Service. The Order Service writes to Postgres and publishes an event to Kafka."

Becomes:
```
flowchart LR
  Client --> Gateway
  Gateway -->|verify JWT| Order[Order Service]
  Order --> DB[(Postgres)]
  Order --> Kafka[/Kafka/]
```

---

## 7. Pros / Cons table

For trade-off discussions ("Trade-offs of X…" / "X의 장단점…").

```html
<!-- EN -->
<div class="proscons">
  <div class="proscons-col pros">
    <h4>✓ Pros</h4>
    <ul>
      <li>Fast to ship, no schema change required.</li>
      <li>Backward compatible with existing clients.</li>
    </ul>
  </div>
  <div class="proscons-col cons">
    <h4>✕ Cons</h4>
    <ul>
      <li>Adds complexity to the routing layer.</li>
      <li>Two code paths to maintain for one quarter.</li>
    </ul>
  </div>
</div>

<!-- KO -->
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

- The `<h4>` text follows the language label table.

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
| Architecture description: A calls B calls C | Mermaid flowchart (§6) |
| "Client → Server → DB" in text | Mermaid sequence/flow (§6) |
| Schema / ERD description | Mermaid erDiagram (§6) |
| "Pros / Cons", "장점 / 단점", "Trade-offs" | Pros-Cons (§7) |
| "Option A / B / C", "Approaches" | Comparison cards (§8) |
| Conclusion / TL;DR of an important section | Key-point highlight (§5) |
| "Note", "FYI", "Background", "참고" | Callout info (§4a) |
| "Careful", "Gotcha", "Risk", "주의" | Callout warn (§4b) |
| "MUST NOT", "절대 금지" | Callout danger (§4c) |
| "Done", "Completed", "완료" | Callout success (§4d) |
| "Decision", "Chose X over Y", "결정" | Callout decision (§4e) |
| "Recommendation", "Best practice", "팁" | Callout tip (§4f) |
| Long code / appendix / FAQ | Collapsible (§9) |
| Short comparison table (≤ 4 columns) | Markdown table (§10) |

---

## 12. Anti-patterns — don't do these

- ❌ Don't use emoji as icons (ℹ️ ⚠️ ⛔ 🎯 …). Use SVG `<use href="#i-...">` from the sprite — emoji render differently across OSes, don't recolor with the theme, and break the minimal tone.
- ❌ Don't wrap EVERYTHING in callouts/highlights — it dilutes the emphasis.
- ❌ Don't use `<ol>` for plan steps — use `.timeline` instead.
- ❌ Don't make mermaid too complex (> 15 nodes) — split into multiple small diagrams.
- ❌ Don't inline-style — every style already lives in `template.html`.
- ❌ Don't forget `id` on headings — the TOC and anchor links break.
- ❌ Don't add `<script>` tags or load external libraries.
- ❌ Don't translate the Markdown line by line — ANALYZE first, then pick a component.
- ❌ Don't use `<h1>` in body content — `.doc-title` is already the H1; use H2/H3 for sections.

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
