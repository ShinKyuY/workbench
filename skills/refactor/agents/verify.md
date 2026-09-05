# Verify Agent — Refactoring Verification (리팩토링 검증)

Confirms the refactoring preserved behavior and improved quality.

## Input

- Execute output: changed files, applied techniques, test results
- Pre-refactoring state (Analyze Agent results)
- Plan Agent output: the per-Step affected-files list (for step 3
  change-scope validation)

## Procedure (수행 절차)

### 1. Behavior preservation (기능 보존 확인)

- Run the full test suite
- Compare test results before/after the refactoring
- Characterization tests or approved snapshots from Step 0: re-run the
  same inputs and report that the diff against the golden values is
  zero
- No suite at all (user declined Step 0): run the alternative checks
  each Step named and report the evidence level as such
- If any test newly fails:
  → a behavior change happened; find the cause
  → report it to the orchestrator (main conversation) and recommend
    either a fix through the Execute flow or a rollback — the decision
    and any user confirmation happen there, not here

### 2. Quality metrics (Before/After)

Do not re-measure Before — use the baseline table the Analyze Agent
recorded as-is, and measure After using exactly the measurement
commands/criteria recorded in the baseline, then compare side by side.

### 3. Change scope validation (변경 범위 검증)

- Confirm the changed files are within the plan
- Warn on unintended file changes
- References intact: typecheck / build exit status from the baseline's
  commands, and a repository-wide search for every identifier the Steps
  renamed or moved (0 code hits)

### 4. Static analysis (when available)

If the project has a linter/formatter configured:
- Run the lint command recorded in the baseline and compare the warning
  count against it
- Check format-rule violations

### 5. Final report

Return this report to the orchestrator (main conversation), which
presents it to the user at Checkpoint ③. Format:

```
## Refactoring results

### Change summary
- Techniques applied: [list]
- Files changed: [list]

### Quality comparison
| Metric | Before | After | Δ |
|--------|--------|-------|---|
| Max function length | N | M | ΔK |
| Max nesting depth | N | M | ΔK |
| Duplicated code | N | M | ΔK |

### Test results
- Total: N passed / M failed
- vs. pre-refactoring: same/different
- Typecheck / build: exit status vs. baseline
- Lint warnings: N → M
- Evidence level: test suite / characterization tests / alternative
  checks only

### Remaining work
- (further refactoring opportunities, efficiency observations,
  deferred items)
```

End the report with a status line —
`DONE | DONE_WITH_CONCERNS | NEEDS_CONTEXT | BLOCKED` plus one line of
reason. Use DONE_WITH_CONCERNS when tests pass but a metric regressed or
a scope deviation was found, or when only alternative checks (no test
suite) back behavior preservation; BLOCKED when neither a test suite nor
the Step-level alternative checks could run.
