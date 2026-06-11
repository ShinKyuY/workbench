# Execute Agent — Refactoring Execution (리팩토링 실행)

Applies a planned refactoring Step safely. The main conversation
orchestrates Step by Step; this file is the procedure for performing
one Step — whether delegated to a per-Step subagent or performed
inline, the stages and artifacts are the same.

## Input

The Step to perform from the Plan Agent's output (technique, target,
change, risk)

## Core principle

**"Small, safe, reversible"** (작고, 안전하고, 되돌릴 수 있게)

Each transform:
- Applies exactly one refactoring technique
- Does not change external behavior
- Can be undone immediately on failure

## Pre-flight checks (required)

Rollback requires a clean starting point. Once, before the first Step,
the orchestrator (main conversation) performs:

1. Check `git status` — uncommitted changes mix the user's work with
   refactoring changes, making selective rollback impossible.
   Propose commit or stash first; start only after it's clean.
2. If not a git repository, create backup copies of the target files
   and tell the user where the backups are.
3. Re-confirm the tests are green in the current state.
   If the starting point is red, no failure can be attributed to the
   refactoring.

## Execution protocol

### For each Step:

```
1. Apply the transform
   - Perform only the planned single refactoring
   - Never mix refactoring with functional changes

2. Update references
   - Renames: update every reference, no exceptions
   - File moves: fix import paths in all consumers
   - Signature changes: check every call site

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

## Per-technique guides

### Extract Method
1. Identify the code block to extract
2. Create the new function, move the code
3. Call the new function from the original site
4. Set the needed parameters and return values
5. Check for variable scope conflicts

### Extract Class
1. Identify the responsibility (fields + methods) to split out
2. Create the new class
3. Move fields and methods one at a time (test each move)
4. Reference the new class from the original
5. Redirect external access points

### Move Method/Field
1. Copy to the target class
2. Adjust references
3. Test
4. Remove the original

### Replace Conditional with Guard Clauses
1. Convert from the outermost condition first
2. One condition at a time
3. Test after each conversion

### Rename
1. Decide the new name
2. Find all references (use Grep)
3. Change them all
4. Test

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
