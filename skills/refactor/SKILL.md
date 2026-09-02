---
name: refactor
description: >-
  Use when the goal is the structural quality of existing code —
  refactoring, cleanup, code smells, deduplication, or architecture
  review ("이 코드 좀 깔끔하게", "구조 개선해줘", "의존성이 꼬여있어").
  For improving the structure of working code, not fixing bugs or
  adding features.
---

# Refactor — Code Refactoring Skill (코드 리팩토링 스킬)

Refactoring means **improving internal structure while preserving external
behavior** (외부 동작을 보존하면서 내부 구조를 개선).
Every phase of this skill exists to honor that one sentence:
analysis makes the current state objective, planning slices the change into
small units, and verification proves behavior was preserved. Whatever else
gets skipped, never skip the **evidence of behavior preservation**.

## First decision: size routing (규모 라우팅)

Decide **first** whether to run the full pipeline. Too much process is a
cost in itself; too little leads to behavior-change accidents.

| Size | Example | Approach |
|------|---------|----------|
| **Small** (소규모) | 1–2 functions, part of one file | Run Phase 1 inline, quickly (skip Phase 2). Share the analysis summary + a 3–5 line plan, then execute → verify unless an approval gate below applies |
| **Medium** (중규모) | 1–3 files | Full pipeline, with subagents |
| **Large** (대규모) | Module/package level | Full pipeline + architecture review required. Shard Phase 1 into scoped agents (see "Dynamic fan-out"). Per-phase user agreement, propose splitting into multiple PRs |

If the request is review-only ("review the architecture", "구조 점검해줘"),
run Phase 1+2 and stop at the report. Execute only when the user asks.

## Pipeline overview (파이프라인 개요)

```
[1. Analyze] → [2. Architecture] → [3. Plan] → [4. Execute] → [5. Verify]
  defect signs    SOLID/coupling   refactoring   stepwise      tests +
  detect+measure  cohesion/layers  strategy      transforms    quality diff
```

- Phases 1 and 2 are independent → spawn **in parallel**; send both Agent
  calls **in a single message**, or they will not actually run concurrently
- Phase 3 depends on the 1+2 results → sequential
- Each Step in Phase 4 depends on the previous Step → sequential
- Phase 5's test run and quality measurement can run in parallel
- Agent count per phase is **not fixed** — scale it to the target size
  per "Dynamic fan-out" below

## Subagent execution protocol (subagent 실행 프로토콜)

Detailed procedures for each phase live in `agents/*.md`. When delegating
to a subagent, ignoring the rules below makes the subagent analyze the
wrong target or produce results that cannot be compared:

- **Subagents know nothing about this conversation.** The spawn prompt
  must include: (1) the absolute path of the agent file to read,
  (2) target file/directory paths, (3) the project's test command,
  (4) constraints and priorities the user mentioned, (5) the expected
  output format (the "Output format" section of each agent file),
  (6) the artifacts the agent file's "Input" section names, pasted in
  full — for Plan: the merged Checkpoint ① report and the scope and
  priorities the user agreed to; for Verify: the baseline table with
  its measurement commands, the union of affected files across all
  Steps, and each Step's Execute record. A pointer to the conversation
  is not enough; the subagent cannot see it.
- **Subagents cannot talk to the user.** Never let a judgment that needs
  user confirmation happen inside a subagent — the subagent only reports
  the condition, and the main conversation asks the user. Checkpoints ①–③
  and the Phase 4 approval gates all fall under this rule.
- Name spawned agents so the role is visible: `refactor-analyze`,
  `refactor-plan`, and so on — unlabeled `Plan` collides with the
  built-in Plan agent type.
- **Every subagent report ends with a status line**:
  `DONE | DONE_WITH_CONCERNS | NEEDS_CONTEXT | BLOCKED` plus one line of
  reason (the agent files request this; repeat it in the spawn prompt).
  Orchestrator handling — `DONE_WITH_CONCERNS`: read the concern before
  using the result; `NEEDS_CONTEXT`: supply what is missing and
  re-dispatch; `BLOCKED`: never re-dispatch unchanged — add context,
  split the work smaller, or raise it at the next checkpoint. Tell every
  subagent that escalating is acceptable — guessing instead of reporting
  NEEDS_CONTEXT produces confident-looking wrong analysis.
- **Treat subagent reports as claims, not evidence.** Anything cheap to
  re-check in the main conversation (a test command's exit status,
  `git diff --stat` against the planned scope), re-check before acting
  on the report.
- **If subagents are unavailable** (no nested agents, etc.), read the same
  agent file directly and perform the phases inline, sequentially. The
  pipeline's value is phase separation, not parallelism — keep the phases
  and their artifacts identical even when inline.

## Dynamic fan-out (동적 분할)

One subagent per phase is the default, not a fixed rule. Scale the count
to the target, with two failure modes in mind: a single agent skimming
50 files produces shallow findings everywhere, while a dozen shards
produce a merge problem worse than the analysis itself. The band below
keeps both out.

| Phase | Default | May become | When |
|-------|---------|------------|------|
| 1 Analyze | 1 agent | 2–5 scoped shards (hard cap 5) | Large target spanning 2+ module/directory boundaries, roughly 10+ files |
| 2 Architecture | 1 agent | 2–5 lens agents, whole view each (hard cap 5) | Large target; split by lens, never by scope |
| 3 Plan | 1 agent | never sharded | — |
| 4 Execute | 1 per Step, sequential | never parallel | — |
| 5 Verify | 1 agent | 2 (test run ∥ metrics) | slow test suite or large baseline table |

**Sharding Phase 1:**

- **Split along module/directory boundaries**, never by file count
  alone. Duplication and Feature Envy are visible only when related
  files share one scope — an arbitrary split hides exactly the signs
  Phase 1 exists to find. If the natural boundaries give more than 5
  scopes, group adjacent modules rather than raising the cap.
- Each shard gets the same `agents/analyze.md`, an explicit file list
  for its scope, and the same output format — uniform shape is what
  makes the merge possible (details in analyze.md "Scoped mode").
- **Exactly one shard runs the test suite**; say which one in its spawn
  prompt. The others only inventory test files in their scope.
  Concurrent suite runs collide (ports, fixtures, temp DBs) and measure
  the same thing N times.
- Spawn all shards **and** the Architecture agent in a single message,
  or they will not actually run concurrently.

**Model selection (when the environment supports it):** Analyze shards
follow a fixed checklist over a bounded scope and can run on a
faster/cheaper model. Keep Architecture and Plan on the session's main
model — they carry the judgment-heavy work.

**Merging shard reports (at Checkpoint ①):** before the normal
Analyze+Architecture merge, combine the shard baseline tables into one
(max of maxes, counts summed, averages recomputed weighted by lines) and
dedup signs across shards. Treat **similar signs reported by two or more
shards as a finding in itself** — cross-module duplication and
re-implemented utilities are invisible to any single shard and surface
only at this merge.

**Phase 2 splits by lens, never by scope:** circular dependencies,
layer violations, and coupling exist only in the whole-system view — a
module-scoped shard destroys the very signal it looks for. When a Large
target is too much for one agent, fan out into 2–5 **lens agents**
(hard cap 5), each given the **whole** target but a single concern:
dependencies / SOLID / anti-patterns / layering / extensibility
(definitions in architecture.md "Lens mode"). Hand each agent the
module inventory and entrypoints — Phase 2 reads import graphs, not
every line, so reading the same structure up to 5 times is acceptable.

**Why Phase 4 never parallelizes:** each green test run is the safety
gate for the next Step. Parallel Steps racing one working tree turn
"test failure = behavior change" into noise.

## Safety precondition: pre-flight checks (시작 전 점검)

Refactoring is only safe while "we can roll back" holds. Verify before
starting Phase 4:

1. **Git working tree state** — uncommitted changes mix the user's work
   with refactoring changes, making rollback impossible. Propose
   commit/stash first.
2. **Not a git repository** — create backup copies of the target files
   and tell the user before proceeding.
3. **No tests** — propose writing characterization tests first (how:
   `references/characterization-testing.md`, read when the target has no
   test coverage). If the user wants to proceed without tests, slice each
   Step smaller and add manual verification points.

---

## Phase 1: Analyze (분석)

> Goal: objectively understand the target's current state and record the
> **baseline metrics** used for the Phase 5 comparison.

Spawn the **Analyze subagent** (`agents/analyze.md`) — for Large
targets, 2–5 scoped shards of it (see "Dynamic fan-out"). It covers:

- **Defect sign detection** — size (Long Method/Large Class), structure
  (God Class, Feature Envy), duplication & derivable state,
  re-implementation of existing utilities, deep nesting, coupling
  (Shotgun Surgery, etc.), naming. Numeric thresholds (30 lines,
  300 lines, 4 parameters, ...) are heuristics, not absolute rules —
  judge by the language and project conventions.
- **Efficiency observations (report-only)** — repeated computation,
  repeated I/O, blocking work on hot paths, etc. Fixing these can change
  observable behavior, so they never become Steps; they are delivered
  only as recommendations in the final report.
- **Dependency mapping** — import/call relationships, blast radius
- **Test status** — existence; run them and confirm currently green.
  If there are no tests, always tell the user.
- **Baseline metrics** — function length, nesting depth, parameter count,
  duplication count, etc. Phase 5 compares against this table; without
  numbers recorded here, "it improved" cannot be proven.

The report follows the "Output format" section of `agents/analyze.md`.
For small-size inline handling, summarize only the key signs, test
status, and baseline metrics.

---

## Phase 2: Architecture Review (아키텍처 리뷰)

> Goal: diagnose structural problems at the module/system level, above
> the code level.

Spawn the **Architecture subagent** (`agents/architecture.md`),
**in parallel** with Phase 1 — for Large targets, optionally 2–5 lens
agents (see "Dynamic fan-out"). It covers:

- SOLID principles check (SRP/OCP/LSP/ISP/DIP)
- Coupling & cohesion analysis, circular dependency check
- Architecture anti-pattern detection (Big Ball of Mud, God Object, ...)
- Layer separation check (presentation→DB direct access, ...)

The report follows the "Output format" section of
`agents/architecture.md`.

**Checkpoint ①**: if Phase 1 ran sharded or Phase 2 ran lens-split,
first merge each phase's reports into one (baseline tables and
cross-shard dedup — see "Dynamic fan-out"). Then merge the two result
sets before reporting — findings
pointing at the same file:line or the same mechanism (e.g. Analyze's God
Class and Architecture's God Object) are combined into one, keeping the
more concrete evidence.

Before reporting, **sample-verify each report**: open 2–3 of its cited
file:line claims and compare against the code. If even one is wrong,
distrust that agent's remaining claims — widen the check or re-dispatch
that scope. Carry every report's "Unverified/assumed items" block into
the merged report as-is. Report the merged results to the user, agree
on scope and priorities with those gaps in view, then move to Phase 3.

---

## Phase 3: Plan (계획)

> Goal: decide which refactoring techniques to apply, in what order.

Spawn the **Plan subagent** (`agents/plan.md`). It covers:

- **Technique matching** — pick techniques per defect sign. Full catalog
  in `references/techniques.md`; core matching table in `agents/plan.md`.
- **Execution order** — safest first: Rename → Extract → Move →
  Simplify → Generalize (only when needed, last).
- **Risk assessment** — files changed per Step, public API changes,
  rollback method.

Each Step must be an **independently committable unit**. If one Step
fails, the previous Steps must remain valid — that is what makes
per-step rollback work.

**Checkpoint ②**: report the plan and risks to the user before Phase 4.
For small sizes, checkpoints ① and ② may be combined. Explicit approval
is mandatory when a public API change is included, one Step touches 5+
files, tests are missing or red, or the user asked for review/approval
before execution. For large work, prefer confirmation before Phase 4
even when none of those gates apply.

---

## Phase 4: Execute (실행)

> Goal: apply the planned refactoring safely, one Step at a time.

The **main conversation orchestrates execution Step by Step**. The
approval gates (public API change, 5+ files changed in one Step,
intermediate commit proposals) can only live in the main conversation —
the only place that can talk to the user. Delegate each Step to a
per-Step subagent given `agents/execute.md`, or perform it inline;
between Steps, check the gate conditions.

When delegating a Step, paste the **full Step text** from the plan
(technique, target, change, affected files, risk, rollback) into the spawn
prompt — the subagent cannot see the plan, and a pointer forces it to
re-derive one. After the subagent reports green, verify before the
checkpoint commit: `git diff --stat` must match the Step's
affected-files list, and the test command must have actually run.

Each Step applies one technique, runs the tests, and on green proposes
an intermediate commit. Red means roll back and retry in smaller units.
Procedure, per-technique note, and guardrails: `agents/execute.md`.

---

## Phase 5: Verify (검증)

> Goal: confirm with **evidence** that quality improved while behavior
> was preserved.

Spawn the **Verify subagent** (`agents/verify.md`). It covers:

- **Behavior preservation** — run the full test suite, compare results
  before/after the refactoring. Any newly failing test is not
  refactoring but a behavior change → find the cause, then fix or roll
  back.
- **Quality metrics comparison** — Phase 1's baseline table side by side
  with After
- **Change scope validation** — confirm no files outside the plan were
  changed

**Checkpoint ③**: report the final summary (change summary, Before/After
table, test results, remaining work) to the user. Format: see
`agents/verify.md`.

---

## User checkpoint summary (사용자 확인 포인트 요약)

| Checkpoint | When | Skippable? |
|------------|------|------------|
| ① Analysis + review results | After Phase 2 | May combine with ② for small sizes |
| ② Execution plan | After Phase 3 | Never when a public API changes |
| ③ Final results | After Phase 5 | No — always report |

Checkpoints are the cheapest insurance against the two most common
refactoring accidents: silently changing behavior, and touching scope
the user didn't want.
