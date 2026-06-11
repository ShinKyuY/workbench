---
name: refactor
description: >
    Code refactoring and architecture review skill. Runs a subagent
    pipeline covering defect-sign analysis, architecture checks
    (SOLID/coupling/cohesion), refactoring planning, safe step-by-step
    execution, and verification. Use this skill whenever the user asks
    for refactoring, code cleanup, code improvement, removing code
    smells, deduplication, extracting functions/classes, reducing
    complexity, architecture review, structure checks, SOLID violations,
    dependency cleanup, layer separation, lowering coupling, raising
    cohesion, "God Class", "DRY violation", or says things like
    "clean this code up", "this code is messy", "improve the structure",
    "review the architecture", "tangled dependencies", "this function is
    too long" — including Korean phrasings such as "리팩토링",
    "코드 정리", "구조 개선해줘", "아키텍처 봐줘", "이 코드 좀 깔끔하게",
    "코드 지저분한데", "의존성이 꼬여있어", "너무 긴 함수". Trigger when
    the goal is structural quality improvement of existing code, not bug
    fixes or new features.
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
| **Small** (소규모) | 1–2 functions, part of one file | Run Phase 1 inline, quickly (skip Phase 2). Report the analysis summary + a 3–5 line plan at once, then execute → verify after confirmation |
| **Medium** (중규모) | 1–3 files | Full pipeline, with subagents |
| **Large** (대규모) | Module/package level | Full pipeline + architecture review required. Per-phase user agreement, propose splitting into multiple PRs |

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

## Subagent execution protocol (subagent 실행 프로토콜)

Detailed procedures for each phase live in `agents/*.md`. When delegating
to a subagent, ignoring the rules below makes the subagent analyze the
wrong target or produce results that cannot be compared:

- **Subagents know nothing about this conversation.** The spawn prompt
  must include: (1) the absolute path of the agent file to read,
  (2) target file/directory paths, (3) the project's test command,
  (4) constraints and priorities the user mentioned, (5) the expected
  output format (the "Output format" section of each agent file).
- **Subagents cannot talk to the user.** Never let a judgment that needs
  user confirmation happen inside a subagent — the subagent only reports
  the condition, and the main conversation asks the user. Checkpoints ①–③
  and the Phase 4 approval gates all fall under this rule.
- Name spawned agents so the role is visible: `refactor-analyze`,
  `refactor-plan`, and so on. Plan in particular collides with the
  built-in Plan agent type, so spawning it unlabeled invites confusion.
- **If subagents are unavailable** (no nested agents, etc.), read the same
  agent file directly and perform the phases inline, sequentially. The
  pipeline's value is phase separation, not parallelism — keep the phases
  and their artifacts identical even when inline.

## Safety precondition: pre-flight checks (시작 전 점검)

Refactoring is only safe while "we can roll back" holds. Verify before
starting Phase 4 (details in `agents/execute.md`):

1. **Git working tree state** — uncommitted changes mix the user's work
   with refactoring changes, making rollback impossible. Propose
   commit/stash first.
2. **Not a git repository** — create backup copies of the target files
   and tell the user before proceeding.
3. **No tests** — propose writing characterization tests first. If the
   user wants to proceed without tests, slice each Step smaller and add
   manual verification points.

---

## Phase 1: Analyze (분석)

> Goal: objectively understand the target's current state and record the
> **baseline metrics** used for the Phase 5 comparison.

Spawn the **Analyze subagent** (`agents/analyze.md`). It covers:

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
**in parallel** with Phase 1. It covers:

- SOLID principles check (SRP/OCP/LSP/ISP/DIP)
- Coupling & cohesion analysis, circular dependency check
- Architecture anti-pattern detection (Big Ball of Mud, God Object, ...)
- Layer separation check (presentation→DB direct access, ...)

The report follows the "Output format" section of
`agents/architecture.md`.

**Checkpoint ①**: merge the two result sets before reporting — findings
pointing at the same file:line or the same mechanism (e.g. Analyze's God
Class and Architecture's God Object) are combined into one, keeping the
more concrete evidence. Report the merged results to the user, agree on
scope and priorities, then move to Phase 3.

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

**Checkpoint ②**: report the plan and risks to the user and get
confirmation. For small sizes, checkpoints ① and ② may be combined.
However, **if a public API change is included, explicit approval is
mandatory regardless of size**.

---

## Phase 4: Execute (실행)

> Goal: apply the planned refactoring safely, one Step at a time.

The **main conversation orchestrates execution Step by Step**. The
approval gates (public API change, 5+ files changed in one Step,
intermediate commit proposals) can only live in the main conversation —
the only place that can talk to the user. Delegate each Step to a
per-Step subagent given `agents/execute.md`, or perform it inline;
between Steps, check the gate conditions.

Core principle — **small, safe, reversible**
(작고, 안전하고, 되돌릴 수 있게):

1. **Apply the transform** — one refactoring per Step. Never mix
   refactoring with functional changes; the moment they mix, the
   criterion "test failure = behavior change" collapses.
2. **Update references** — on rename/move/signature change, check every
   reference
3. **Run tests** — green → next Step; red → roll back immediately and
   retry in smaller units
4. **Checkpoint** — propose an intermediate commit after each successful
   Step

Per-technique execution guides and guardrails: see `agents/execute.md`.

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

Why checkpoints exist: the most common refactoring accident is "silently
changing behavior"; the second is "touching scope the user didn't want".
Confirmation is the cheapest insurance against both.
