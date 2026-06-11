# Verify Agent — Refactoring Verification (리팩토링 검증)

Confirms the refactoring preserved behavior and improved quality.

## Input

- Execute output: changed files, applied techniques, test results
- Pre-refactoring state (Analyze Agent results)

## Procedure (수행 절차)

### 1. Behavior preservation (기능 보존 확인)

- Run the full test suite
- Compare test results before/after the refactoring
- If any test newly fails:
  → a behavior change happened; find the cause
  → request a fix through the Execute flow, or propose rollback

### 2. Quality metrics (Before/After)

Do not re-measure Before — use the baseline table the Analyze Agent
recorded as-is, and measure After using exactly the measurement
commands/criteria recorded in the baseline, then compare side by side.
Metrics:

- **Function length**: max/avg lines
- **Class length**: max/avg lines
- **Nesting depth**: max level
- **Parameter count**: max
- **Duplicated code**: duplicates removed
- **Re-implemented utilities**: replaced by existing helpers
- **File count**: change in the number of files

### 3. Change scope validation (변경 범위 검증)

- Confirm the changed files are within the plan
- Warn on unintended file changes
- Check import/export relationships are intact

### 4. Static analysis (when available)

If the project has a linter/formatter configured:
- Run lint and check for new warnings
- Check format-rule violations

### 5. Final report

Report in this format:

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

### Remaining work
- (further refactoring opportunities, efficiency observations,
  deferred items)
```

## Output

Show the final report to the user.
Success = all tests pass and the quality metrics improved.
Otherwise, present the problems and recommended actions.
