# Execute Agent — Refactoring Execution (리팩토링 실행)

Applies a planned refactoring Step safely. The main conversation
orchestrates Step by Step; this file is the procedure for performing
one Step — whether delegated to a per-Step subagent or performed
inline, the stages and artifacts are the same.

## Input

The Step to perform, pasted in full from the Plan Agent's output
(technique, target, change, affected files, risk, rollback)

## Core principle

**"Small, safe, reversible"** (작고, 안전하고, 되돌릴 수 있게)

Each transform:
- Applies exactly one refactoring technique
- Does not change external behavior
- Can be undone immediately on failure

## Execution protocol

### For each Step:

```
1. Apply the transform
   - Perform only the planned single refactoring
   - Never mix refactoring with functional changes

2. Update references (renames, moves, signature changes)
   - Search the whole repository for the old identifier (`rg` or the
     available text-search tool). Code references must be 0; hits in
     strings, config, or docs are judged one by one and recorded

3. Run the check commands
   - Run the project's test command, and typecheck / build when the
     project has them (they catch broken references in files the
     tests never import)
   - Green → next Step
   - Red → roll back immediately, analyze the cause, retry in
     smaller units
   - No test suite (user declined Step 0): run the alternative check
     named in the Step — check commands plus the fixed-input entrypoint
     run — and diff its output against the pre-Step run

4. Record results
   - Files changed
   - Technique applied
   - Check results (tests, typecheck/build, old-identifier search)
```

### Step 0 — characterization tests

When the Step is Step 0, read `references/characterization-testing.md`
first. Capture golden values on the inputs the plan lists, confirm the
new tests pass on the untouched code, commit them, and re-record the
test inventory (command, passed/failed counts) so later Steps and
Verify compare against a baseline that includes them.

## Per-technique note

Follow standard Fowler mechanics. One skill-specific rule: when a
technique moves several parts (Extract Class fields/methods, nested
conditions to guard clauses), move one part at a time and run the tests
between moves.

## Guardrails (안전장치)

- Re-confirm tests are green before changing anything
- When any of the following occurs, **stop and report to the
  orchestrator (main conversation)**. Subagents cannot talk to the
  user; the main conversation obtains user confirmation and relays the
  decision:
  - A Step turns out to need 5+ file changes
  - A public API signature change becomes necessary
  - A transform differs from the plan or is uncertain (skip and report)

## Output

After each Step:
- Files changed
- Technique applied
- Test result (pass/fail)
- On failure: cause and response
- Status line: `DONE | DONE_WITH_CONCERNS | NEEDS_CONTEXT | BLOCKED`
  plus one line of reason. Stopping with BLOCKED is always acceptable —
  a half-applied transform reported as DONE is the worst outcome,
  because the orchestrator commits it as "safe".
