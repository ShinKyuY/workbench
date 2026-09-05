---
name: analyze-ml-repo
description: >-
  Structural analysis of the code in an ML/AI model repository only —
  architecture, training/data pipelines, tensor shapes, read from
  source. Use whenever model training or inference code needs
  explaining, even without the word "analyze": "how does this model
  work?", "trace the data flow", "이 모델 어떻게 동작해?", "데이터가 어떻게
  흘러가?", or "코드 구조 분석해줘" on an ML repo. Not for anything that
  is not ML repo code: non-ML codebases, refactoring or bug fixing,
  explaining papers or ML theory without a repo, exploring datasets, or
  running training/inference.
---

# ML Repository Analyzer (ML 레포 구조 분석)

Analyzes an ML/AI model repository with the smallest workflow that fits
the request: answer narrow questions directly, or use specialized
subagents and produce a structured markdown document for broad analysis.

Write the document and chat summary in the conversation language;
section structure, code identifiers, and tensor-shape notation stay
the same.

Every shape or number claim carries file:line evidence and is
labeled confirmed, inferred, or unavailable. Read code first; docs
are supplements.

## Output mode routing (출력 방식 라우팅)

Route by how much reading the answer needs, not by matching phrases —
the same wording ("how does the model work?") can be either mode
depending on scope:

- **Quick answer**: the answer is one specific fact or a short chain
  confirmable by reading a few directly relevant files — a single
  shape, one function's behavior, one config value. Do Step 1
  reconnaissance, read those files, answer in chat with file:line
  evidence, and skip subagents/files unless the user asks for a
  document.
- **Document mode**: answering requires sweeping one or more pipeline
  areas (data, model, training, inference) — whole-repo structure,
  end-to-end workflow, architecture-depth "how does X work". Run the
  dispatch plan and save the final markdown document scoped to the
  dispatched roles.
- **Escalate, don't straddle**: when a quick answer grows past a few
  paragraphs or pulls in a second pipeline area, say you are
  switching to document mode, then build the dispatch plan.

---

## Step 1: Reconnaissance (정찰 — 직접 수행)

Before dispatching subagents, map the skeleton of the repo yourself.
This information is what lets you give each subagent a precise
search scope.

Do directly:
```
1. Map the project tree (`rg --files`, Glob, or equivalent):
   - **/*.py (main Python files)
   - **/config*.json, **/config*.yaml (config files)
   - **/*.md (docs)

2. Grep key patterns — framework-neutral so they match any repo:
   - "class.*Dataset" -> dataset file locations
   - "class.*Model\b|class.*Net\b|class.*Module\b|class.*Layer\b"
     -> model files
   - "def forward|def __call__|def call\b" -> forward pass locations
     (PyTorch `forward`, JAX/Flax `__call__`, TF/Keras `call`)
   - "def train|class.*Trainer|\.fit\(|value_and_grad" -> training loops
   - "__main__|def main\b" -> entry points

3. Identify the framework, then grep its specific idioms:
   - Check imports / dependency files to find the framework
     (torch / jax/flax / tensorflow/keras / transformers).
   - Read `references/framework-cues.md` and use the matching
     column's signatures for the rest of reconnaissance —
     hard-coded PyTorch patterns silently miss JAX/TF/HF repos.

4. Read config files:
   - Extract the model's key numbers (dims, layer counts,
     vocab sizes, ...)
   - Identify the architecture family
     (CNN/RNN/Transformer/GAN/Diffusion/MLP/recsys-ranking, ...)

5. Fix the analysis scope:
   - If the repo contains multiple independent model families or
     subprojects (monorepo), ask the user which part to analyze —
     a full monorepo analysis costs several times the time/tokens.
   - If the user cannot respond (background/headless run), pick the
     part the entry points and request context indicate is most
     central, and state the choice at the top of the final document
     as an explicit assumption.
```

Output of this step: the **target inventory** — the model families,
dataset pipelines, training entry points, and inference paths in
scope, each with its file list. Step 2 turns this into a dispatch
plan.

---

## Step 2: Build the dispatch plan (동적 투입 계획)

Not every analysis is needed every time, and one agent per role is
not always enough. Build the plan in two passes: pick the **roles**
from the request, then set the **instance count** per role from the
Step 1 target inventory.

### 2-1. Pick roles from the request

These rows apply in document mode; a quick answer never dispatches.

| Request type | Roles to dispatch |
|--------------|--------------------|
| "Analyze the whole structure" (전체 구조 분석) | all 5 |
| "What are the data shapes?" (데이터 형상) | structure-scout + data-pipeline |
| "How does the model work?" (모델 동작) | structure-scout + model-architecture |
| "How is it trained?" (학습 방법) | structure-scout + training-workflow |
| "Summarize the workflow" (워크플로우 정리) | structure-scout + data-pipeline + training-workflow + inference-analyst |
| "Analyze this one file" (단일 파일) | none — do it directly, no subagents |

- Always perform the Step 1 reconnaissance yourself, in every case.
  structure-scout is separate from reconnaissance — it is the agent
  that writes the structure/entry-point sections of the final
  document.
- If earlier analysis results already exist in the conversation,
  skip those parts and analyze only what is new.

### 2-2. Scale instances to the target inventory

The unit of dispatch is **role × target**, not just role. One plan
row = one agent with its own file list.

- Default: 1 instance per role, covering all of that role's targets.
- Fan out when a role has **2+ independent targets** — independent
  means analyzing one tells you nothing about the other (separate
  model families, unrelated dataset pipelines, disjoint training
  entry points). E.g. models `interformer` + `wukong` in scope →
  2 model-architecture instances, 6 agents total, within the default
  budget and justified by the two families.
- structure-scout fans out the same way for monorepo subprojects.

Agent budget (예산) — these are full readers, not cheap verifiers:
- Default budget **8 agents** per analysis; exceed it only when
  independent targets force it, and say why in the plan.
- Hard cap **14 agents** — never exceed it. Past the cap, never drop
  a target silently: either **group related targets** under one
  instance (one agent covers two small models) and record the
  grouping in the final document's assumptions, or — when the
  overflow is large — go back to the user through the available
  question mechanism to narrow the scope.

---

## Step 3: Dispatch specialist subagents in parallel (병렬 투입)

Dispatch the Step 2 plan **concurrently** — one agent per plan row.
Give each agent the concrete file paths of its own row's target.

Agent definitions live in `agents/`.

| # | Agent | File | subagent_type | Role |
|---|-------|------|---------------|------|
| 1 | structure-scout | `agents/structure-scout.md` | general-purpose | project structure, entry points, execution flow |
| 2 | data-pipeline | `agents/data-pipeline.md` | general-purpose | data pipeline, shape transitions |
| 3 | model-architecture | `agents/model-architecture.md` | general-purpose | model structure, forward pass, core blocks |
| 4 | training-workflow | `agents/training-workflow.md` | general-purpose | training loop, loss, optimizer |
| 5 | inference-analyst | `agents/inference-analyst.md` | general-purpose | inference, output schema, serving |

What goes into each agent's prompt:
1. The instructions from the agent file
2. The **concrete file paths of its target** (from the plan row) —
   for fanned-out instances, also one line on what the *other*
   instances cover, so the agent does not wander out of scope
3. The **config summary from Step 1 reconnaissance** — the key
   numbers (dims, layer counts, vocab sizes, ...) you already read.
   Pass it so agents (structure-scout especially) build on it
   instead of re-reading every config from scratch.
4. The identified framework and, for non-PyTorch repos, the relevant
   `references/framework-cues.md` column, so agents grep the right
   idioms.
5. The diagram/table rules from `references/diagram-rules.md`
6. The report contract from `references/report-contract.md`
   (report format, status header, unverified-items block,
   self-review)
7. For shape-heavy agents (model-architecture, data-pipeline), the
   tactics in `references/shape-tracing.md`.
8. The user's original request, quoted verbatim — the report
   contract keys the report language off it.

Subagent execution protocol (실행 프로토콜):
- **Subagents know nothing about this conversation.** The prompt
  carries everything above; items 5, 6 and 8 go to every agent.
- Parallel dispatch only works when all Agent calls are sent
  **in a single message**.
- Name spawned agents so the role is visible: `ml-structure-scout`,
  `ml-data-pipeline`, and so on. Fanned-out instances carry their
  target: `ml-model-arch-interformer`.
- **Subagents cannot talk to the user.** Any judgment that needs
  user confirmation is only *reported* by the subagent; the main
  conversation asks the user.

A large plan (≥5 rows) may also run as a Workflow script when that
tool exists — same prompts, same report contract; plain parallel
Agent calls stay the default.

**Fallback — no Agent dispatch tool available** (nested subagents,
some platforms): read the agent files chosen in Step 2 plus the
`references/` files above, and perform each agent's procedure
yourself, sequentially. The quality bar (file:line evidence,
unverified-items tracking, Step 4 verification, Step 5 mechanical
check) applies unchanged.

---

## Step 4: Synthesize and verify (결과 종합과 검증)

When all subagent results are back:

1. **Check status first**: look at each report's `status` and its
   "unverified/assumed items" block.
   - PARTIAL → read the unverified spots yourself and fill them in.
   - BLOCKED → fix the cause (wrong paths, missing context) and
     re-dispatch. Never retry with the same prompt unchanged.
2. **Sample-verify — do not trust the report**: from each report,
   pick 2–3 key shape/number claims and open the cited file:line to
   check the code really says what the report claims. Citation
   existence and Mermaid syntax are checked mechanically in Step 5
   by `scripts/verify_report.py` — spend the manual samples on
   meaning, not existence. If even one sample is wrong, distrust the
   rest of that agent's claims and widen the verification.
3. **Cross-check boundaries**: confirm that the seams between agents
   agree. On mismatch, open the code yourself, decide which side is
   right, and fix it.

   | Boundary | What to check |
   |----------|---------------|
   | data-pipeline batch output ↔ model forward input | keys, shapes, dtypes |
   | model forward output ↔ loss input | shapes |
   | training checkpoint structure ↔ inference load code | saved/loaded keys |

4. **Merge fanned-out instances**: when a role ran as multiple
   instances (one per model/dataset), merge them into that role's
   single document section — write shared mechanics once, keep
   per-target differences, and add the comparison table across
   targets (required with 2+ models).

---

## Step 5: Assemble the final markdown document (문서 조립)

### 5-1. Assemble the markdown document

Assemble the subagent results into the structure below. Diagrams
follow the rules in `references/diagram-rules.md` (Mermaid/markdown
tables), and every section links the relevant source file paths.
Translate the section titles into the conversation language; the
section order stays fixed.

The full template applies to whole-repo analyses. For a partial
dispatch (only some roles ran), keep the End-to-end workflow section
plus the sections owned by the dispatched roles, renumber them, and
open the document with one line stating what is and is not covered.

```markdown
# [Project] Analysis

## End-to-end workflow
(Top-level system diagram — data prep -> training -> inference ->
output. Owned by structure-scout. The inference-only sub-pipeline
belongs in section 4, owned by inference-analyst — do not duplicate
the whole-system flow there.)
### Project structure and entry points
(Directory map, CLI commands and the Job/Runner each invokes,
hyperparameter catalog by category. Owned by structure-scout.)

## 1. Data pipeline
### 1-1. Raw data schema
### 1-2. Preprocessing pipeline
### 1-3. Dataset -> Collate shapes
### 1-4. Concrete data examples (raw rows, batch tensors)

## 2. Model architecture
### 2-1. Constructor parameter table (actual config values; owned by model-architecture)
### 2-2. Forward pass shape trace (line by line)
### 2-3. Core block analysis (with visualizations)

## 3. Training workflow
### 3-1. Loss function (formula + shapes)
### 3-2. Training setup (optimizer, scheduler, precision)
### 3-3. Distributed training setup
### 3-4. Checkpoint structure
### 3-5. Evaluation (metrics, cadence)
### 3-6. CLI run examples

## 4. Inference & outputs
(Inference-only sub-pipeline diagram lives here, owned by
inference-analyst — not the whole-system flow.)
### 4-1. Inference input/output shapes
### 4-2. Output schema
### 4-3. Serving optimizations

## 5. Key comparison table
(when there are multiple models)
```

### 5-2. Save and report

1. Save the assembled document as a `.md` file. Default path when
   the user did not specify one:
   - Analyzing the repo you are working in (CWD inside the target
     repo): `./analysis/<topic>.md`, creating the directory if
     missing. It is the user's own tree; mention in the summary that
     the file is untracked so they can commit or gitignore it.
   - Analyzing another tree (a clone, a dependency, a path the user
     pointed at): save under the CWD, never inside the analyzed
     repo — analysis is read-only and must not leave files in
     someone else's tree. Write into the analyzed repo (e.g. its
     `docs/`) only when the user asks.
2. Mechanically verify the saved document:
   `python3 <skill-dir>/scripts/verify_report.py <doc.md> --repo
   <analyzed-repo-root>`. It checks every file:line citation against
   that tree only (file exists, line within file length; a bare
   basename that matches several files is reported as ambiguous with
   the candidates) and lints Mermaid blocks (direction stated, bracket
   labels quoted, subgraph/end balanced). A failure that names
   same-basename candidates is a missing path prefix — fix the cited
   path; every other failure is fixed by reopening the code, never by
   deleting evidence. Re-run until it prints `result: OK`.
3. In chat, present only the key summary (end-to-end workflow plus a
   few main findings) and the `.md` file path. Do not paste the full
   document back into the chat.
4. Create additional formats only when the user explicitly asks.
