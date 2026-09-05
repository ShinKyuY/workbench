# md2html — Component Catalog

This file is the **single source of truth** for the HTML snippets you (the AI) must use for `content.html`; `scripts/build.py` merges it into `template.html`.

**Rules:**
- Copy snippets verbatim, only replace the bracketed `{{...}}` placeholders.
- Never invent new CSS classes — every visual element MUST be one of these components or vanilla markdown HTML (`<h2>`, `<p>`, `<ul>`, etc.).
- All sample text in this catalog is illustrative — replace with real content from the source `.md`.
- **Language follows the source**: Korean source → Korean UI labels; any other language → English UI labels. See the label table below. Body content always stays in the source language.
- **Use SVG icons via the sprite, never emojis.** All icons reference IDs defined in `template.html`'s `<svg class="icon-sprite">`. Form: `<svg class="icon" viewBox="0 0 24 24" aria-hidden="true"><use href="#i-NAME"/></svg>`. See §13 for the full catalog of available icon IDs.

## Language label table

The HTML's `<html lang="...">` attribute MUST be `ko` for Korean sources and `en` for everything else. The "Recommended" badge label is set via the `--rec-label` CSS variable on `<html>`. Both come from `meta.json` (`LANG`, `REC_LABEL`).

```html
<!-- what build.py produces from meta.json LANG / REC_LABEL — do not write this yourself -->
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

These values go into `meta.json` (keys `TITLE`, `SUBTITLE`, `DOC_TYPE`, `SOURCE_FILE`, `DATE`, `READ_TIME`); `build.py` substitutes them into the header. Do not edit `template.html`.

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

## 6. SVG diagram (complex diagrams only)

**Simple flows do NOT belong here** — a linear chain or a single fan-out/fan-in with ≤ ~8 nodes uses the native flow component (§6b): it matches the theme and supports KaTeX in labels. Hand-draw an inline SVG only when the structure is more than §6b can express:
- "client calls server, server calls DB" (lifelines, ordered messages) → sequence (§6.2)
- "table A has an FK to table B" → ER (§6.3)
- "state machine / 상태 전이" → state (§6.4)
- deployment / boundaries / "inside the VPC" → architecture with groups (§6.5)
- dense flowcharts: > 8 nodes, two branch levels, or cross/back edges → flowchart (§6.1)
- "phases / roadmap / timeline" is **not** an SVG — use the Timeline (§3) or a Markdown table.

Every diagram is a `<figure class="diagram">` holding one `svg.dg` and a `<figcaption class="diagram-caption">`. The root tag is fixed, attribute order included:

```html
<svg class="dg" viewBox="0 0 {{W}} {{H}}" width="{{W}}" role="img" aria-label="{{one sentence, same claim as the caption}}">
```

`width` equals the viewBox W (max 880, typically 600–720); CSS shrinks it on narrow screens. Arrowheads come from the shared markers in `template.html` (see the marker table) — a diagram never contains `<defs>`, `<marker>`, `<style>`, `<script>`, `<foreignObject>`, `<image>`, `<use>`, or `<a>`. Color, stroke and font come only from the classes below: no `style`, `fill`, `stroke`, `color`, `font-*` attributes and no hex literals anywhere. `build.py` rejects all of these.

### Visual language

| Item | Value |
|---|---|
| Grid | 8px. Node centers (`cx`/`cy`), column/row pitches and widths are multiples of 8; node heights are the fixed values below (44 / 40 / 64), so a rect's `y` is `cy − height/2`. |
| Margin | ≥ 8px between any element (labels and marker tips included) and the viewBox edge. |
| Node | Default 120×44, `rx="8"`. Decision 160×64. State pill 120×40, `rx="20"`. Entity 176 wide. Widen in 8px steps (max 200) when a label needs it; the whole column takes that width. |
| Column pitch (LR) | 176 (120 node + 56 gap). Row pitch 80 (44 node + 36 gap). |
| Stroke | 1.5px everywhere. No shadows, no gradients, no fills on edges. |
| Edge | horizontal: right border → left border at the shared `cy`; vertical: bottom border → top border at the shared `cx`. Orthogonal edges are `<polyline>` with ≤ 2 bends, routed through gaps, never through a node. Crossings are allowed; no hop arcs. |
| Dashed edge (`dg-edge-dashed`) | asynchronous, optional, or return path. |
| Edge label | horizontal segment: centered at the midpoint, `y = line y − 8`. Vertical segment: `x = line x + 8`, `text-anchor="start"`, at the midpoint y. Polyline: on the longest segment. |
| Text | node label 13px, sub line 11px, edge label 12px; centered by default (`svg.dg text` sets `text-anchor: middle; dominant-baseline: central`). Entity rows and group titles are `text-anchor: start`. |

### Shape vocabulary

Every node is `<g class="dg-node dg-SHAPE">` with the shape element(s) first and one `<text class="dg-text">` last (start/end states carry no text). Coordinates below use node origin `(x, y)`, size `W×H`, center `(cx, cy)`.

| Class | Meaning | Markup |
|---|---|---|
| `dg-process` | service, step, component (default) | `<rect x="{x}" y="{y}" width="120" height="44" rx="8"/>` |
| `dg-decision` | branch (160×64) | `<polygon points="{cx},{y} {cx+80},{cy} {cx},{y+64} {cx-80},{cy}"/>` |
| `dg-datastore` | database, cache, bucket | `<path d="M{x} {y+6} V{y+H-6} A{W/2} 6 0 0 0 {x+W} {y+H-6} V{y+6}"/><ellipse cx="{cx}" cy="{y+6}" rx="{W/2}" ry="6"/>` — text at `cy+3` |
| `dg-queue` | queue, topic, event | `<polygon points="{x+12},{y} {x+W},{y} {x+W-12},{y+H} {x},{y+H}"/>` |
| `dg-actor` | user, external person (120×64 slot, edges attach at `cx±16`) | `<circle cx="{cx}" cy="{cy-16}" r="6"/><line x1="{cx}" y1="{cy-10}" x2="{cx}" y2="{cy+4}"/><line x1="{cx-10}" y1="{cy-4}" x2="{cx+10}" y2="{cy-4}"/><polyline points="{cx-8},{cy+14} {cx},{cy+4} {cx+8},{cy+14}"/>` — text at `cy+26` |
| `dg-external` | external system, boundary as a node (dashed) | same `<rect>` as `dg-process` |
| `dg-note` | annotation (folded corner) | `<polygon points="{x},{y} {x+W-10},{y} {x+W},{y+10} {x+W},{y+H} {x},{y+H}"/><polyline points="{x+W-10},{y} {x+W-10},{y+10} {x+W},{y+10}"/>` |
| `dg-state` | state (pill 120×40) | `<rect x="{x}" y="{y}" width="120" height="40" rx="20"/>` |
| `dg-state-start` | initial pseudo-state (edges leave at `cx+6`) | `<circle cx="{cx}" cy="{cy}" r="6"/>` |
| `dg-state-end` | final pseudo-state (edges arrive at `cx−8`) | `<circle cx="{cx}" cy="{cy}" r="8"/><circle cx="{cx}" cy="{cy}" r="4"/>` |
| `dg-entity` | table / class (176 wide, head 28, row 22) | `<rect … height="{28 + 22·rows}" rx="8"/><path class="dg-entity-head" d="M{x} {y+8} a8 8 0 0 1 8 -8 h160 a8 8 0 0 1 8 8 v20 H{x} z"/><text class="dg-entity-title" x="{cx}" y="{y+14}">…</text><text class="dg-entity-row" x="{x+10}" y="{y+28+11}">…</text>` |

Entity rows read `name␣␣type␣␣[PK|FK]` with short type names (`uuid`, `int`, `text`, `ts`); each further row is 22 lower.

Node text, one or two lines:

```html
<!-- one line -->
<text class="dg-text" x="{cx}" y="{cy}">Order Service</text>
<!-- two lines: main at cy−7, sub at cy+9 -->
<text class="dg-text" x="{cx}" y="{cy}"><tspan x="{cx}" dy="-7">Order Service</tspan><tspan class="dg-sub" x="{cx}" dy="16">Java 21</tspan></text>
```

Label budget per shape (13px main line; a CJK syllable counts 1em, anything else 0.6em): process / external / note / state / datastore `W − 16`; decision `0.7·W`; queue `W − 32`; entity `W − 20`; actor `112`. Edge labels ≤ 144px. Over budget → shorten the label or widen the node.

**Modifiers** (add to the `g.dg-node` class list): `dg-node-accent` (the one thing the section is about — max one per diagram), `dg-node-muted` (out of scope, removed), `dg-status-success` / `dg-status-warn` / `dg-status-danger` (only when the node *means* ok / at-risk / failed, and always with a `dg-sub` line that says so in words). Edges: `dg-edge-dashed`, `dg-edge-accent` (only toward the accent node, with `#dg-arrow-accent`), `dg-edge-muted` (with `#dg-arrow-muted`).

### Markers

| id | Use |
|---|---|
| `dg-arrow` | `marker-end` on every solid or dashed edge |
| `dg-arrow-accent` | `marker-end` with `.dg-edge-accent` |
| `dg-arrow-muted` | `marker-end` with `.dg-edge-muted` |
| `dg-arrow-open` | `marker-end` on sequence returns |
| `dg-crow-one` / `dg-crow-many` | ER relationship: `marker-start` on the "one" side, `marker-end` on the "many" side |
| `dg-dot` | `marker-start` on an edge that leaves a junction point rather than a node |

Written as `marker-end="url(#dg-arrow)"`. Every `.dg-edge` carries at least one `marker-*`.

### 6.1 Flowchart (LR / TD, branches, cross edges)

Layout (LR): columns at `x = 16 + 176·i`; a decision column is 160 wide (its polygon spans column x … x + 160) and keeps the 56 gap, so every column after it shifts by +40; rows at `cy = 40 + 80·j`. TD: swap axes, column pitch 160, row pitch 88. Decision "yes" continues in the main direction, "no" turns 90°. A back/cross edge is a dashed polyline routed through a free row channel (`y = cy + 40`) or column channel (`x = column x − 28`).

```html
<figure class="diagram">
  <svg class="dg" viewBox="0 0 720 240" width="720" role="img" aria-label="사용자 요청이 API Gateway와 인증 판정을 거쳐 Order Service에서 Postgres 저장과 이벤트 발행으로 이어지는 흐름">
    <g class="dg-node dg-actor">
      <circle cx="76" cy="104" r="6"/>
      <line x1="76" y1="110" x2="76" y2="124"/>
      <line x1="66" y1="116" x2="86" y2="116"/>
      <polyline points="68,134 76,124 84,134"/>
      <text class="dg-text" x="76" y="146">사용자</text>
    </g>
    <g class="dg-node dg-process">
      <rect x="192" y="98" width="120" height="44" rx="8"/>
      <text class="dg-text" x="252" y="120">API Gateway</text>
    </g>
    <g class="dg-node dg-decision">
      <polygon points="448,88 528,120 448,152 368,120"/>
      <text class="dg-text" x="448" y="120">인증 OK?</text>
    </g>
    <g class="dg-node dg-process dg-node-accent">
      <rect x="584" y="98" width="120" height="44" rx="8"/>
      <text class="dg-text" x="644" y="120">Order Service</text>
    </g>
    <g class="dg-node dg-datastore">
      <path d="M584 24 V56 A60 6 0 0 0 704 56 V24"/>
      <ellipse cx="644" cy="24" rx="60" ry="6"/>
      <text class="dg-text" x="644" y="43">Postgres</text>
    </g>
    <g class="dg-node dg-queue">
      <polygon points="596,178 704,178 692,222 584,222"/>
      <text class="dg-text" x="644" y="200">이벤트 버스</text>
    </g>
    <g class="dg-node dg-process dg-node-muted">
      <rect x="388" y="178" width="120" height="44" rx="8"/>
      <text class="dg-text" x="448" y="200">401 응답</text>
    </g>

    <line class="dg-edge" x1="92" y1="120" x2="192" y2="120" marker-end="url(#dg-arrow)"/>
    <text class="dg-edge-label" x="142" y="112">POST /order</text>
    <line class="dg-edge" x1="312" y1="120" x2="368" y2="120" marker-end="url(#dg-arrow)"/>
    <line class="dg-edge dg-edge-accent" x1="528" y1="120" x2="584" y2="120" marker-end="url(#dg-arrow-accent)"/>
    <text class="dg-edge-label" x="556" y="112">yes</text>
    <line class="dg-edge" x1="448" y1="152" x2="448" y2="178" marker-end="url(#dg-arrow)"/>
    <text class="dg-edge-label" x="456" y="165" text-anchor="start">no</text>
    <line class="dg-edge" x1="644" y1="98" x2="644" y2="62" marker-end="url(#dg-arrow)"/>
    <text class="dg-edge-label" x="652" y="80" text-anchor="start">INSERT</text>
    <line class="dg-edge dg-edge-dashed" x1="644" y1="142" x2="644" y2="178" marker-end="url(#dg-arrow)"/>
    <text class="dg-edge-label" x="652" y="160" text-anchor="start">publish</text>
    <polyline class="dg-edge dg-edge-dashed" points="388,200 76,200 76,158" marker-end="url(#dg-arrow)"/>
    <text class="dg-edge-label" x="232" y="192">401</text>
  </svg>
  <figcaption class="diagram-caption">주문 생성 흐름. 인증 실패는 401로 사용자에게 바로 돌아간다.</figcaption>
</figure>
```

### 6.2 Sequence

Layout: lifeline pitch 240 (`x = 120 + 240·i`, 3 lifelines fit in 720; 4 lifelines → pitch 176). Header = process node 120×40 at `y = 8`, centered on the lifeline. `line.dg-lifeline` from `y = 48` to `H − 8`. Messages at `y = 88 + 40·k`. Activation = `rect.dg-activation` 8 wide centered on the lifeline, spanning its first to last message. Arrows run from the caller's lifeline (or activation edge) to the callee's activation edge; label centered above (`y − 8`). Return = dashed edge with `#dg-arrow-open`. Self message = polyline `x,y x+24,y x+24,y+16 x,y+16`.

```html
<figure class="diagram">
  <svg class="dg" viewBox="0 0 720 232" width="720" role="img" aria-label="클라이언트가 API에 주문을 요청하고 API가 DB에 저장한 뒤 201을 돌려주는 순서">
    <g class="dg-node dg-process">
      <rect x="60" y="8" width="120" height="40" rx="8"/>
      <text class="dg-text" x="120" y="28">클라이언트</text>
    </g>
    <g class="dg-node dg-process">
      <rect x="300" y="8" width="120" height="40" rx="8"/>
      <text class="dg-text" x="360" y="28">API</text>
    </g>
    <g class="dg-node dg-datastore">
      <path d="M540 14 V42 A60 6 0 0 0 660 42 V14"/>
      <ellipse cx="600" cy="14" rx="60" ry="6"/>
      <text class="dg-text" x="600" y="31">DB</text>
    </g>
    <line class="dg-lifeline" x1="120" y1="48" x2="120" y2="224"/>
    <line class="dg-lifeline" x1="360" y1="48" x2="360" y2="224"/>
    <line class="dg-lifeline" x1="600" y1="48" x2="600" y2="224"/>
    <rect class="dg-activation" x="356" y="88" width="8" height="120"/>
    <rect class="dg-activation" x="596" y="128" width="8" height="40"/>

    <line class="dg-edge" x1="120" y1="88" x2="356" y2="88" marker-end="url(#dg-arrow)"/>
    <text class="dg-edge-label" x="238" y="80">POST /orders</text>
    <line class="dg-edge" x1="364" y1="128" x2="596" y2="128" marker-end="url(#dg-arrow)"/>
    <text class="dg-edge-label" x="480" y="120">INSERT order</text>
    <line class="dg-edge dg-edge-dashed" x1="596" y1="168" x2="364" y2="168" marker-end="url(#dg-arrow-open)"/>
    <text class="dg-edge-label" x="480" y="160">ok</text>
    <line class="dg-edge dg-edge-dashed" x1="356" y1="208" x2="120" y2="208" marker-end="url(#dg-arrow-open)"/>
    <text class="dg-edge-label" x="238" y="200">201 Created</text>
  </svg>
  <figcaption class="diagram-caption">주문 생성 요청의 호출 순서. 점선은 응답이다.</figcaption>
</figure>
```

### 6.3 ER

Layout: entities 176 wide on one row, `x = 8 + 264·i` (gap 88), `y = 8`. Relationship = horizontal `line.dg-edge` at `y = 60` between entity borders, `marker-start="url(#dg-crow-one)"` on the "one" side and `marker-end="url(#dg-crow-many)"` on the "many" side; verb label above the line. More than 3 entities → second row at `y = 8 + tallest + 48`, vertical relationships at the entity `cx`. Class diagrams use the same entity node (methods as rows).

```html
<figure class="diagram">
  <svg class="dg" viewBox="0 0 720 132" width="720" role="img" aria-label="users, orders, order_items 세 테이블과 일대다 관계">
    <g class="dg-node dg-entity">
      <rect x="8" y="8" width="176" height="94" rx="8"/>
      <path class="dg-entity-head" d="M8 16 a8 8 0 0 1 8 -8 h160 a8 8 0 0 1 8 8 v20 H8 z"/>
      <text class="dg-entity-title" x="96" y="22">users</text>
      <text class="dg-entity-row" x="18" y="47">id  uuid  PK</text>
      <text class="dg-entity-row" x="18" y="69">email  text</text>
      <text class="dg-entity-row" x="18" y="91">created_at  ts</text>
    </g>
    <g class="dg-node dg-entity">
      <rect x="272" y="8" width="176" height="116" rx="8"/>
      <path class="dg-entity-head" d="M272 16 a8 8 0 0 1 8 -8 h160 a8 8 0 0 1 8 8 v20 H272 z"/>
      <text class="dg-entity-title" x="360" y="22">orders</text>
      <text class="dg-entity-row" x="282" y="47">id  uuid  PK</text>
      <text class="dg-entity-row" x="282" y="69">user_id  uuid  FK</text>
      <text class="dg-entity-row" x="282" y="91">status  text</text>
      <text class="dg-entity-row" x="282" y="113">total  int</text>
    </g>
    <g class="dg-node dg-entity">
      <rect x="536" y="8" width="176" height="116" rx="8"/>
      <path class="dg-entity-head" d="M536 16 a8 8 0 0 1 8 -8 h160 a8 8 0 0 1 8 8 v20 H536 z"/>
      <text class="dg-entity-title" x="624" y="22">order_items</text>
      <text class="dg-entity-row" x="546" y="47">id  uuid  PK</text>
      <text class="dg-entity-row" x="546" y="69">order_id  uuid  FK</text>
      <text class="dg-entity-row" x="546" y="91">sku  text</text>
      <text class="dg-entity-row" x="546" y="113">qty  int</text>
    </g>
    <line class="dg-edge" x1="184" y1="60" x2="272" y2="60" marker-start="url(#dg-crow-one)" marker-end="url(#dg-crow-many)"/>
    <text class="dg-edge-label" x="228" y="52">주문</text>
    <line class="dg-edge" x1="448" y1="60" x2="536" y2="60" marker-start="url(#dg-crow-one)" marker-end="url(#dg-crow-many)"/>
    <text class="dg-edge-label" x="492" y="52">포함</text>
  </svg>
  <figcaption class="diagram-caption">주문 스키마. 사용자 1명이 주문 여러 건을, 주문 1건이 품목 여러 개를 가진다.</figcaption>
</figure>
```

### 6.4 State machine

Layout: pills 120×40 on column pitch 176 (`x = 8 + 176·i`), row pitch 80 (`cy = 32 + 80·j`). Start dot in column 0 at `cx = 68`. Snake to a second row when more than 4 states. Transition label = the event, on the edge. Several terminal states may share one end node reached by polylines. Self transition = polyline loop above the pill: `cx−16,y cx−16,y−16 cx+16,y−16 cx+16,y`.

```html
<figure class="diagram">
  <svg class="dg" viewBox="0 0 664 208" width="664" role="img" aria-label="주문 상태가 생성됨, 결제 대기, 결제 완료, 완료 순으로 바뀌고 결제 대기에서 시간 초과 시 취소되는 상태 머신">
    <g class="dg-node dg-state-start"><circle cx="68" cy="32" r="6"/></g>
    <g class="dg-node dg-state">
      <rect x="184" y="12" width="120" height="40" rx="20"/>
      <text class="dg-text" x="244" y="32">생성됨</text>
    </g>
    <g class="dg-node dg-state">
      <rect x="360" y="12" width="120" height="40" rx="20"/>
      <text class="dg-text" x="420" y="32">결제 대기</text>
    </g>
    <g class="dg-node dg-state">
      <rect x="536" y="12" width="120" height="40" rx="20"/>
      <text class="dg-text" x="596" y="32">결제 완료</text>
    </g>
    <g class="dg-node dg-state dg-node-muted">
      <rect x="360" y="92" width="120" height="40" rx="20"/>
      <text class="dg-text" x="420" y="112">취소됨</text>
    </g>
    <g class="dg-node dg-state">
      <rect x="536" y="92" width="120" height="40" rx="20"/>
      <text class="dg-text" x="596" y="112">완료</text>
    </g>
    <g class="dg-node dg-state-end"><circle cx="508" cy="192" r="8"/><circle cx="508" cy="192" r="4"/></g>

    <line class="dg-edge" x1="74" y1="32" x2="184" y2="32" marker-end="url(#dg-arrow)"/>
    <text class="dg-edge-label" x="129" y="24">주문 생성</text>
    <line class="dg-edge" x1="304" y1="32" x2="360" y2="32" marker-end="url(#dg-arrow)"/>
    <text class="dg-edge-label" x="332" y="24">결제 요청</text>
    <line class="dg-edge" x1="480" y1="32" x2="536" y2="32" marker-end="url(#dg-arrow)"/>
    <text class="dg-edge-label" x="508" y="24">승인</text>
    <line class="dg-edge dg-edge-dashed" x1="420" y1="52" x2="420" y2="92" marker-end="url(#dg-arrow)"/>
    <text class="dg-edge-label" x="428" y="72" text-anchor="start">시간 초과</text>
    <line class="dg-edge" x1="596" y1="52" x2="596" y2="92" marker-end="url(#dg-arrow)"/>
    <text class="dg-edge-label" x="604" y="72" text-anchor="start">출고</text>
    <polyline class="dg-edge" points="420,132 420,192 500,192" marker-end="url(#dg-arrow)"/>
    <polyline class="dg-edge" points="596,132 596,192 516,192" marker-end="url(#dg-arrow)"/>
  </svg>
  <figcaption class="diagram-caption">주문 상태 전이. 취소와 완료는 모두 종료 상태다.</figcaption>
</figure>
```

### 6.5 Architecture / deployment (groups)

Layout: nodes on the flowchart grid; a `g.dg-group` wraps the nodes that share a boundary with a dashed rect padded 16 around them plus 24 extra at the top for the title (`text.dg-group-title` at `x + 12`, `y + 16`). Groups never overlap; group gap 32. Nodes inside a group are children of the `g.dg-group`, after its `rect` and title. Edges that cross a boundary are the point of the drawing — label them.

```html
<figure class="diagram">
  <svg class="dg" viewBox="0 0 648 296" width="648" role="img" aria-label="사용자가 VPC 안의 ALB와 API 서버를 거쳐 RDS와 이벤트 큐에 닿고 API 서버가 외부 결제 PG를 호출하는 배치">
    <g class="dg-node dg-actor">
      <circle cx="68" cy="84" r="6"/>
      <line x1="68" y1="90" x2="68" y2="104"/>
      <line x1="58" y1="96" x2="78" y2="96"/>
      <polyline points="60,114 68,104 76,114"/>
      <text class="dg-text" x="68" y="126">사용자</text>
    </g>
    <g class="dg-group">
      <rect x="144" y="40" width="488" height="178" rx="8"/>
      <text class="dg-group-title" x="156" y="56">VPC ap-northeast-2</text>
      <g class="dg-node dg-process">
        <rect x="160" y="78" width="120" height="44" rx="8"/>
        <text class="dg-text" x="220" y="100">ALB</text>
      </g>
      <g class="dg-node dg-process dg-node-accent">
        <rect x="328" y="78" width="120" height="44" rx="8"/>
        <text class="dg-text" x="388" y="100">API 서버</text>
      </g>
      <g class="dg-node dg-datastore">
        <path d="M496 84 V116 A60 6 0 0 0 616 116 V84"/>
        <ellipse cx="556" cy="84" rx="60" ry="6"/>
        <text class="dg-text" x="556" y="103">RDS</text>
      </g>
      <g class="dg-node dg-queue">
        <polygon points="508,158 616,158 604,202 496,202"/>
        <text class="dg-text" x="556" y="180">이벤트 큐</text>
      </g>
    </g>
    <g class="dg-node dg-external">
      <rect x="328" y="238" width="120" height="44" rx="8"/>
      <text class="dg-text" x="388" y="260">결제 PG</text>
    </g>

    <line class="dg-edge" x1="84" y1="100" x2="160" y2="100" marker-end="url(#dg-arrow)"/>
    <text class="dg-edge-label" x="122" y="92">HTTPS</text>
    <line class="dg-edge" x1="280" y1="100" x2="328" y2="100" marker-end="url(#dg-arrow)"/>
    <line class="dg-edge" x1="448" y1="100" x2="496" y2="100" marker-end="url(#dg-arrow)"/>
    <text class="dg-edge-label" x="472" y="92">SQL</text>
    <polyline class="dg-edge dg-edge-dashed" points="448,110 472,110 472,180 496,180" marker-end="url(#dg-arrow)"/>
    <text class="dg-edge-label" x="480" y="145" text-anchor="start">publish</text>
    <line class="dg-edge" x1="388" y1="122" x2="388" y2="238" marker-end="url(#dg-arrow)"/>
    <text class="dg-edge-label" x="396" y="180" text-anchor="start">결제 승인</text>
  </svg>
  <figcaption class="diagram-caption">배치도. 결제 승인만 VPC 경계를 넘어 외부 PG로 나간다.</figcaption>
</figure>
```

### Source has a mermaid block? Map it

| Mermaid block in the source | Draw as |
|---|---|
| `flowchart` (simple, ≤ ~8 nodes) | Native flow (§6b) |
| `flowchart` (dense) | §6.1 |
| `sequenceDiagram` | §6.2 |
| `erDiagram`, `classDiagram` | §6.3 |
| `stateDiagram-v2` | §6.4 |
| architecture prose | §6.5 |
| `gantt`, `timeline`, `journey` | Timeline (§3) or a Markdown table |
| `pie` | Markdown table |

Rebuild from the same nodes and edges; never paste the mermaid source into the output.

### Authoring procedure

1. List nodes: name, shape, 1–2 line label. Pick the one accent node (or none).
2. Assign each node a column and row on the recipe's grid; keep the main path on one row (LR) or column (TD).
3. Write the coordinate table: x, y, W, H, cx, cy per node. viewBox W/H = extents + 8.
4. List edges as (from, to, label, solid/dashed, marker); compute endpoints on node borders; polylines only where a straight line would cross a node.
5. Place labels per the visual-language table; check each against its budget.
6. Write the `aria-label` (one sentence, the same claim as the caption) and the `<figcaption>`; wrap in `<figure class="diagram">`.
7. Run `build.py --render-check`; on `data-dg-overflow` / `data-dg-clipped` failures fix coordinates, not the checker.

**Rules:**
- Nodes are neutral by default. Exactly one element per diagram may carry the accent; the only identity channel besides that is shape and label. Never cycle categorical colors across nodes.
- Text wears text color. Never the accent, a status color, or a series color.
- Status colors are reserved for nodes that mean ok / at-risk / failed, and always travel with the word.
- Labels are one to three words or up to ~10 Hangul syllables. Sentences go in the `<figcaption>`.
- Every edge has an arrowhead (or, in ER, a cardinality marker) and, when the meaning is not obvious, a label. An unlabeled arrow reads as "related somehow".
- Write `&lt;` and `&amp;` inside SVG text — a raw `<` or `&` breaks the XML and the build.
- Class list (complete): `dg`, `dg-node`, `dg-process`, `dg-decision`, `dg-datastore`, `dg-queue`, `dg-actor`, `dg-external`, `dg-note`, `dg-state`, `dg-state-start`, `dg-state-end`, `dg-entity`, `dg-entity-head`, `dg-entity-title`, `dg-entity-row`, `dg-node-accent`, `dg-node-muted`, `dg-status-success`, `dg-status-warn`, `dg-status-danger`, `dg-text`, `dg-sub`, `dg-edge`, `dg-edge-dashed`, `dg-edge-accent`, `dg-edge-muted`, `dg-edge-label`, `dg-group`, `dg-group-title`, `dg-lifeline`, `dg-activation`. Nothing else.

---

## 6b. Native flow diagram (the default for simple flows)

For linear chains and single fan-out/fan-in flows (≤ ~8 nodes) — the majority of flows in real documents. Pure theme-styled HTML/CSS: light/dark aware, print-safe, no CDN, and **labels can contain KaTeX** (`\(\Lambda(x)\)`), which SVG diagrams can't do.

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
- Needs more than one `.flow-row` level of branching, back-edges, or > ~8 nodes? It's not a simple flow — use an SVG diagram (§6).

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

A section made only of these elements is **not hand-written**: paste its source Markdown between `<!-- MD -->` and `<!-- /MD -->` in `content.html` and `build.py` converts it (SKILL.md Step 3). The HTML equivalents below are for the few places where plain elements sit *inside* a component (a list in a callout, a table in a collapsible):

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
| Complex flow: > 8 nodes, multi-branch, cross edges | SVG flowchart (§6) |
| Message exchange with ordering (lifelines) | SVG sequence (§6) |
| Schema / ERD description | SVG ER (§6) |
| State machine / 상태 전이 | SVG state (§6) |
| Deployment / boundaries ("inside the VPC") | SVG architecture (§6) |
| Roadmap / gantt / phases | Timeline (§3) |
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
- ❌ Don't ship an SVG diagram for a simple linear/fan-out flow — use the native flow component (§6b). It matches the theme, prints reliably, and renders KaTeX labels.
- ❌ Don't exceed ~15 nodes per SVG diagram — split into multiple small diagrams.
- ❌ Don't use color instead of a label — a status color without the word, or an accent without a reason.
- ❌ Don't give every node the accent — one per diagram.
- ❌ Don't color diagram text with accent, status, or series colors — text wears text color.
- ❌ Don't cycle categorical colors across nodes — nodes are neutral; the only identity channel is the shape and the label.
- ❌ Don't draw an edge without an arrowhead, or leave a meaningful edge unlabeled.
- ❌ Don't put sentences in nodes — the `<figcaption>` holds them.
- ❌ Don't add `<defs>`, `style`, `fill`, `stroke` attributes or hex colors inside a diagram — every color comes from a `dg-*` class.
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
Wrap the body in one `<h2 id="content">` (see SKILL.md Edge cases) so the TOC has one entry, or omit `--toc` and pass `--no-toc` to `build.py` — it strips the sidebar and the mobile trigger. `build.py` rejects an empty `toc.html`; the JS auto-hide of `<aside class="toc">` only applies in the manual fallback (no `python3`).

### 14g. Long URLs / identifiers
`.content` already has `overflow-wrap: anywhere` — long URLs/identifiers wrap without breaking the layout.

---

## 15. Math (KaTeX)

`template.html` ships KaTeX (CDN; offline shows raw LaTeX). Use it whenever the source contains LaTeX math: `$...$`, `$$...$$`, `\(...\)`, `\[...\]`.

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
- **SVG diagram labels and headings can't use KaTeX.** Inside diagrams use plain unicode (`Λ(x) head — Poisson NLL`). Same for `<h2>`/`<h3>` text: the TOC sidebar copies heading text outside the renderer's scope, so a heading like `3.3 $\Lambda$ / $\mathbb{E}[K]$` becomes `3.3 Λ / E[K]` in both the heading and its TOC entry. These are the only places unicode math notation is right.
