---
name: define-goal
description: >-
  Use when the user wants to define or clarify a goal, success criteria,
  or a "definition of done", or to sharpen a vague ask ("make X faster",
  "목표 정의", "성공 기준", "되게 만들어줘") before starting work.
  Definition only — skip asks that already have a clear outcome.
---

# Define Goal — 목표 정의 스킬

Shape the user's intent into an objective an agent can pursue **honestly**
and **prove it finished** (정직하게 추구하고 끝났음을 증명할 수 있는 목표).
Prefer observable outcomes, explicit evidence, and bounded scope over
activity: a goal naming only *activity* ("keep improving", "되게 해줘")
gives no way to know it's done, so the agent stops too early or grinds
forever. Numbers are useful, but a reviewable artifact with a clear rubric
can be just as verifiable.

## Workflow

### 1. Gate — 목표 정의가 정말 필요한가

Apply this skill when the user asks to create/set/clarify a goal, or when
the ask is too vague to verify. If the work already has a verifiable
outcome, just do the work — goal ceremony on a clear task is friction.

### 2. Draft — 목표 문장에 다섯 요소를 담는다

A usable goal names:

- **Outcome** — the specific thing that will be true when done
- **Artifact** — the system / repo / environment / behavior involved
- **Verification** — how completion is proven: command, metric + threshold,
  or review rubric
- **Scope & non-goals** — what's in and out, when ambiguity matters
- **Stop condition** — when the agent should ask instead of grinding

### 3. Harden — 검증 가능하게 굳힌다

- **Baseline first (기준선).** A target without the current value can't be
  judged achievable. Put the baseline — or the exact way to measure it —
  next to the target ("p95 currently 480 ms → target < 250 ms").
- **Thresholds, usually several.** Real goals hold multiple conditions at
  once: correctness *and* latency *and* no new failures. Draw from:
  pass/fail validators (tests, checks, commands), quality metrics (latency,
  error rate, accuracy, coverage, cost), artifact constraints (paths,
  formats, environments, deadlines), evidence counts (reproduced failures,
  reruns, reviewed examples, migrated records).
- **Hard vs. negotiable (필수/조정 가능).** When conditions can conflict,
  mark which must hold and which may yield. If context doesn't settle the
  priority, spend a Repair question on it.
- **Inter-rater test (상호평가).** Two reviewers reading only the goal text
  reach the same pass/fail verdict. Anything the check relies on must be
  derivable from the text — unwritten expectations become noise.
- **Outcome, not path (경로가 아닌 결과).** Pin down what must be true, not
  which steps to take; agents find valid routes you didn't foresee.
  Constrain the path only when ordering is itself the requirement
  (migrations, compliance, safety).
- **Anti-gaming (스펙 해킹 방어).** A goal is a proxy, and capable agents
  optimize the proxy — sometimes by cheating it. Avoid "pass at all costs"
  phrasing. "Tests pass" alone is unsafe: assertions can be rewritten to
  `True`, checks weakened, logs silenced. Tie success to the *behavior* the
  tests prove and keep the verifier outside the agent's edit scope
  ("existing `test_checkout` unchanged and green"). For research / ops
  goals, require the answer be backed by citable evidence (sources, logs,
  run IDs), not just asserted.
- **Subjective work resists numbers — don't fake them.** For writing,
  design, "품질" asks: use a small rubric two reviewers can apply the same
  way, representative examples, or an explicit approval step instead of an
  arbitrary metric.

### 4. Repair — 약한 목표는 고치고, 물음은 최대 셋

Rewrite a vague goal into an observable one when context makes the rewrite
safe. Reject pure activity goals ("make progress", "keep investigating",
"되게 만들어줘") until sharpened. Ask at most **three** questions, and only when a safe
rewrite risks the wrong outcome — target the missing validator or scope:
"Success by latency, cost, or accuracy?", "Verify against local, staging,
or prod?", "Minimum evidence before marking complete?". If no metric
exists, propose the most honest binary validator and ask to confirm.

### 5. Deliver — 대화로 제시하고, 파일은 필요할 때만

Present the objective as one concise statement — verification evidence and
scope **inside** it, phrased as a prompt a fresh agent can act on. Write it
to a file only when the user gave a path or asked for a file, or when the
work is large / long-horizon — then use the frozen-goal block (default
`goal.md`). If the goal is complex enough to span sessions or modules,
also bake in the plan-first requirement (see "Plan for complex goals").

## Quality Bar — 최종 점검

Reread the finished objective against the five Draft elements, then ask
two more: would a second reviewer reach the same pass/fail verdict from
the text alone, and could the stated check be gamed without the real
outcome happening?

## Examples — Weak → Strong

**Performance** (baseline + tamper-resistant validator):

> Weak: "Make checkout faster."
>
> Strong: "Reduce checkout API p95 latency from the current 480 ms to below
> 250 ms on the documented slow path with the smallest safe server-side
> change; verify with `npm run test:checkout` (unchanged) and the latency
> benchmark showing p95 < 250 ms across 3 consecutive runs."

**Review work** (scope-bounded + evidence):

> Weak: "Keep investigating the PR comments."
>
> Strong: "Resolve the change-requesting review comments on PR 123,
> touching only the affected auth files and tests; verify with the auth
> test command plus `gh pr view 123` showing no unresolved change-request
> threads."

**Refactoring** (behavior parity):

> Weak: "코드 좀 깔끔하게 해줘."
>
> Strong: "`src/order/` 모듈을 동작 변화 없이 정리한다. 기존 테스트가 전후
> 모두 green(`pytest tests/order -q`, 테스트 파일 무변경), public API
> 시그니처 유지, 중복 로직 3곳 통합. 공개 인터페이스를 바꿔야만 가능한
> 정리는 진행 전에 질문."

## Frozen-goal block (목표 동결 템플릿)

For large / long-horizon work, freeze the target so the agent doesn't
build "something impressive but wrong":

```
Goal:       <the outcome that will be true>
Non-goals:  <what is explicitly out of scope>
Constraints:<perf / platform / determinism / files allowed to change>
Baseline:   <current measured value, or how to measure it>
Done when:  <checks + how to demo it: commands, thresholds, runs>
Stop & ask: <conditions that should pause for the user>
Plan:       <complex goals only: `plan.md` the executor writes before
             implementing and references per milestone>
```

For multi-step work, slice "Done when" into one-loop milestones, each with
its own acceptance check + validation command, and **stop-and-fix**: if a
check fails, repair before moving on.

## Plan for complex goals (복잡한 목표는 계획을 먼저)

When the work is expected to span multiple sessions, touch several
modules or systems, or carry unknowns that need investigation — signals
readable *before* any plan exists — bake a plan-first requirement into
the goal: the executor **writes `plan.md` before
implementing**, **checks it covers every "Done when" item**, and
**updates it at each milestone boundary**. The goal stays frozen; the
plan is the living document — a plan change that would alter the goal's
outcome, thresholds, or scope is a Stop & ask, not a plan update.
Interface and contract decisions live pinned in the plan's `Decisions:`
section.

Read [references/plan.md](references/plan.md) when defining a complex
goal — the full standard (zero-context, no placeholders, milestone
sizing, pinned interfaces, verification per milestone, template). Point
the executor to it, or copy its template into the goal if the executor
can't reach this skill's files.

Small goals: inline milestones in the frozen-goal block are enough — a
plan file for a one-loop fix is friction, not safety. When it's unclear
which side the goal falls on, start with inline milestones and have the
goal say to promote them to `plan.md` if the work crosses into a second
session.

## Quantification Heuristics (작업 유형별 검증 힌트)

- **Bugs**: reproduction first, fix second — a validator that *fails
  before, passes after*, kept unchanged by the fix.
- **Tests**: the exact command and pass condition; tests stay outside the
  agent's edit scope.
- **Performance**: metric, baseline, target threshold, measurement method,
  run count (e.g. "p95 < 250 ms across 3 runs").
- **Refactoring**: behavior parity — suite green before and after, public
  API unchanged unless in scope, plus a before/after quality metric.
- **Subjective artifacts**: a small review rubric, representative examples,
  and an explicit approval/evidence path.
- **Research**: the decision it must enable, sources in scope, evidence
  standard (claims tied to citable sources).
- **Operations**: healthy state, monitoring window, failure threshold,
  rollback/escalation trigger.
