# Characterization Testing (특성화 테스트)

Read this when the refactoring target **has no tests** and the pipeline
proposes writing them first (SKILL.md pre-flight, plan.md "When there
are no tests"). A characterization test does not assert what the code
*should* do — it pins what the code *currently* does, so any behavior
change introduced by a refactoring shows up as a diff. It is the safety
net that lets "test failure = behavior change" hold on untested code.

Distinct from a normal unit test: you are not judging correctness. Even
buggy behavior gets pinned as-is — reproducing today's output is the
whole point. Fixing the bug is a separate, functional change, never part
of the refactoring.

## 1. Capture current output as the golden value (골든 값 캡처)

Run the target on representative inputs and record whatever it produces
— return value, printed output, written file, emitted events, final
state. That recorded output becomes the expected value, regardless of
whether it looks correct.

| Output shape | How to pin |
|--------------|------------|
| Return value / data structure | Serialize (JSON, repr, ...) and store as the expected value |
| Console / log output | Capture stdout/stderr, compare as text |
| File / DB writes | Snapshot the produced artifact, diff after |
| Side effects (calls, events) | Record the call sequence with a spy/mock |

For a first pass, let the test print the actual output, copy it into the
assertion, and re-run to confirm it now passes. This is legitimate here
precisely because the goal is to reproduce, not to specify.

## 2. Select boundary and representative inputs (경계·대표 입력 선정)

Coverage of *inputs*, not lines, is what makes the net catch changes.
Prioritize:

- **Happy path** — the common, expected input
- **Boundaries** — empty, zero, one element, max size, off-by-one edges
- **Special values** — null/None, negative, unicode, whitespace
- **Branch drivers** — one input per major conditional branch, so each
  path the refactoring might touch is exercised
- **Known-weird cases** — inputs that trigger odd-but-real behavior; pin
  them so a refactoring cannot silently "fix" (i.e. change) them

If reading the branches to pick inputs is impractical, use a coverage
tool to confirm the chosen inputs actually reach the code being changed.

## 3. Approval-test pattern (승인 테스트 패턴)

For large or awkward-to-assert outputs, store the golden value in a file
committed alongside the test (an "approved" snapshot) rather than inline:

1. Run the code, write actual output to a `.received` file
2. Compare against the committed `.approved` file
3. First run: no approved file exists → review the received output once,
   then rename it to `.approved` to accept it
4. Later runs: any diff fails the test and shows exactly what changed

This scales to outputs too big to eyeball in an assertion, and the diff
on failure points straight at the behavior that moved. Most languages
have a library for it (ApprovalTests, jest/vitest snapshots, syrupy,
insta, ...); a hand-rolled file compare works too.

## 4. Re-run identical inputs after refactoring (동일 입력 재실행 diff)

The net only works if After is measured exactly like Before:

- Run the **same** inputs through the refactored code
- Compare against the **same** golden values / approved snapshots
- **Any** diff = a behavior change → not refactoring. Find the cause,
  then fix or roll back (this is the Phase 5 behavior-preservation gate).
- Zero diff = behavior preserved; the structural change is safe

Keep these tests through the refactoring; they are the evidence Phase 5
reports. Once the refactoring is done and behavior is confirmed
preserved, decide separately whether to keep them as permanent
regression tests or discard the throwaway scaffolding.

## Handling non-determinism (비결정성 처리)

If the output varies across runs (timestamps, random ids, ordering,
hash-seeded maps), the raw diff is useless. Neutralize the varying parts
before comparison — inject a fixed clock/seed, sort collections, or mask
the volatile fields with a placeholder. Mask the minimum necessary;
over-masking hides the very changes the test exists to catch.
