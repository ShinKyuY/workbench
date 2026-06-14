---
name: define-goal
description: >-
  Use when the user wants to define, set, or clarify a goal, success
  criteria, or "definition of done", or to sharpen a vague ask
  ("make X faster", "목표 정의", "성공 기준", "되게 만들어줘") before
  starting work. Turns it into a concrete, verifiable objective —
  measurable or reviewable, with evidence and bounded scope; definition
  only, skip asks that already have a clear outcome.
---

# Define Goal — 목표 정의 스킬

Shape the user's intent into an objective an agent can pursue **honestly**
and **prove it finished** (정직하게 추구하고 끝났음을 증명할 수 있는 목표).
Prefer observable outcomes, explicit evidence, and bounded scope over
activity: a goal naming only *activity* ("keep improving", "되게 해줘")
gives no way to know it's done, so the agent stops too early or grinds
forever. Numbers are useful, but reviewable artifacts with a clear
rubric can be just as verifiable.

## Workflow

1. **Confirm a goal definition is needed.** Use this when the user asks to
   create / set / clarify a goal, or to turn an intention into a clear
   objective. If the work already has a verifiable outcome, just do it — a
   goal ceremony on a clear task is friction.

2. **Restate the goal concretely.** A usable goal names:
   - the specific **outcome** that will be true
   - the **artifact / system / repo / environment / behavior** involved
   - how completion is **verified**
   - what is **in scope vs. out (non-goals)**, when ambiguity matters
   - the **stop condition** for asking instead of grinding

3. **Make success observable — quantitative when it fits.** Good
   criteria are *Specific, Measurable or Reviewable, Achievable,
   Relevant*: a real number tied to a benchmark/baseline, a binary
   validator, or a rubric that two reviewers can apply the same way.
   Even "hazy" goals often quantify — "safe output" → "< 0.1% of 10k
   outputs flagged" — but subjective artifacts may be better verified by
   reviewed examples, acceptance notes, or an explicit quality checklist.
   Most need **several thresholds at once** (correctness *and* latency
   *and* no new failures). Draw from: pass/fail validators (tests,
   checks, evals, commands); quality thresholds (latency, error rate,
   accuracy, coverage, cost, memory…); artifact constraints (paths,
   modules, formats, environments, deadlines, blast radius); evidence
   counts (reproduced failures, reruns, reviewed examples, migrated
   records).

4. **Make it verifiable, not just numeric.**
   - **Inter-rater test** (상호평가): two reviewers reading the goal reach
     the **same** pass/fail verdict. Anything a checker relies on must be
     derivable from the goal text — unwritten becomes noise.
   - **Grade the outcome, not the path** (경로가 아닌 결과): pin down *what
     must be true*, not *which steps*. Step-by-step goals are brittle;
     agents find valid routes you didn't foresee. Constrain the path only
     when ordering is the requirement (migrations, compliance, safety).

5. **Guard against gaming** (스펙 해킹 방어). A goal is a proxy, and capable
   agents optimize the proxy — sometimes by cheating it.
   - Avoid "pass / win at all costs" phrasing; suggestive wording nudges
     toward gaming. State the honest outcome plainly.
   - "Tests pass" isn't automatically safe: an agent can rewrite assertions
     to `True`, weaken a check, or silence logs. Tie success to the
     *behavior* the tests prove, and keep the verifier out of the agent's
     edit scope ("existing `test_checkout` unchanged and green").
   - Research / ops goals: require the **answer be backed by citable
     evidence** (sources, logs, run IDs), not just asserted.

6. **Repair or clarify weak goals before finalizing.**
   - Rewrite a vague goal into an observable one when context makes it safe.
   - Reject pure activity goals ("make progress", "keep investigating",
     "되게 만들어줘") until sharpened.
   - Ask **one** question only when a safe rewrite would risk the wrong
     outcome — about the missing validator or scope, e.g. "Success by
     latency, cost, accuracy, or a user-visible behavior?", "Verify against
     local, staging, or prod?", "Minimum evidence before marking complete?"
     If no metric exists, propose the most honest binary validator and ask
     to confirm.

7. **Finalize to a `.md` file.** Write the objective as one concise
   statement — verification evidence and scope **inside** it, phrased as a
   prompt a fresh agent can act on. Save to the path the user gave, else
   `goal.md` by default; use the Frozen-goal block for large work.

## Goal Quality Bar (품질 바)

The finished objective should answer:

- What concrete thing will be **true** when done?
- What **evidence** proves it (could a second reviewer agree)?
- What quantitative, binary, or rubric-based **threshold** defines
  success?
- What **scope / non-goals** matter?
- What should make the agent **stop and ask** instead of grinding?
- Could the stated check be **gamed** without the real outcome?

## Examples (Good vs Weak)

**Good** — performance, tamper-resistant validator:

> Reduce checkout API p95 latency below 250 ms on the documented slow path
> with the smallest safe server-side change; verify with `npm run
> test:checkout` (unchanged) and the latency benchmark showing p95 under
> 250 ms across 3 consecutive runs.

**Good** — review work, scope-bounded + evidence:

> Resolve the change-requesting review comments on PR 123, touching only
> the affected auth files and tests; verify with the auth test command plus
> `gh pr view 123` showing no unresolved change-request threads.

**Good** — quality bar, inline SMART:

> The sentiment classifier should reach F1 ≥ 0.85 (Measurable, Specific) on
> a held-out set of 10,000 posts (Relevant), a 5% gain over baseline
> (Achievable).

**Weak** (rewrite before using):

> Make checkout faster.

> Keep investigating the PR comments.

> 코드 좀 깔끔하게 해줘.

## Frozen-goal block (선택: 목표 동결 템플릿)

For large / long-horizon work, freeze the target so the agent doesn't build
"something impressive but wrong":

```
Goal:       <the outcome that will be true>
Non-goals:  <what is explicitly out of scope>
Constraints:<perf / platform / determinism / files allowed to change>
Done when:  <checks + how to demo it: commands, thresholds, runs>
Stop & ask: <conditions that should pause for the user>
```

For multi-step work, slice "Done when" into one-loop milestones, each with
its own acceptance check + validation command, and **stop-and-fix**: if a
check fails, repair before moving on.

## Quantification Heuristics (작업 유형별)

- **Bugs**: reproduction first, fix second — a validator that *fails before,
  passes after*, kept unchanged by the fix.
- **Tests**: the exact command and pass condition; the test stays outside
  the agent's edit scope.
- **Performance**: metric, target threshold, measurement method, run count
  (e.g. "p95 < 250 ms across 3 runs").
- **Refactoring**: behavior parity — suite green before and after, public
  API unchanged unless in scope, plus the before/after quality metric.
- **Quality work**: an observable bar — reviewed examples, lint/typecheck/
  test pass, or a user-approved artifact.
- **Subjective artifacts**: a small review rubric, representative
  examples, and an explicit approval/evidence path.
- **Research**: the decision it must enable, sources in scope, evidence
  standard (claims tied to citable sources).
- **Operations**: healthy state, monitoring window, failure threshold,
  rollback/escalation trigger.
