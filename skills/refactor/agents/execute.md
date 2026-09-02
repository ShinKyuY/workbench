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

3. Run tests
   - Run the project's test command
   - Green → next Step
   - Red → roll back immediately, analyze the cause, retry in
     smaller units

4. Record results
   - Files changed
   - Technique applied
   - Test results
```

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
