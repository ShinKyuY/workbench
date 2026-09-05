# Plan Agent — Refactoring Strategy (리팩토링 전략 수립)

Builds a concrete refactoring execution plan from the analysis results.

## Input

Analyze Agent output:
- Defect sign list (with severity)
- Dependency map
- Check commands and test status
- Whether the user agreed to Step 0 (characterization tests) at
  Checkpoint ①, when the target has no tests

Architecture review output (merged with the Analyze findings at
Checkpoint ①):
- SOLID violations, coupling/cohesion, anti-patterns, layering
- These drive the structural techniques (e.g. special-case accretion →
  generalize the mechanism), so plan from the merged set, not the
  defect-sign list alone

## Procedure (수행 절차)

### 1. Technique matching (기법 매칭)

Pick a suitable refactoring technique for each defect sign.
Consult `references/techniques.md`; core matches:

| Sign | First choice | Alternative |
|------|--------------|-------------|
| Long Method | Extract Method | Replace Temp with Query |
| God Class | Extract Class | Move Method + Move Field |
| Feature Envy | Move Method | Extract Method → Move |
| Duplicate Code | Extract Method | Pull Up Method (with inheritance) |
| Deep Nesting | Guard Clauses | Decompose Conditional |
| Long Param List | Parameter Object | Preserve Whole Object |
| Switch Statements | Polymorphism | Strategy Pattern |
| Magic Numbers | Symbolic Constant | Extract to config/enum |
| Data Class | Move related logic in | Encapsulate Field |
| Middle Man | Remove Middle Man | Inline Class |
| Re-implemented existing utility | Replace with the existing helper | Substitute Algorithm |
| Special-case accretion | Generalize the underlying mechanism | Replace Conditional with Polymorphism |

The Analyze Agent's efficiency observations (report-only) never become
Steps. Their behavior preservation is hard to prove with tests, so pass
them on only as recommendations in the final report.

### 2. Execution order (실행 순서 결정)

Principle: **safest first, in dependency order**

Typical order:
1. Rename — safest, immediately improves comprehension
2. Extract — the basis of structural improvement
3. Move — relocate responsibilities after extraction
4. Simplify — clarify conditionals and logic
5. Generalize — only when needed, last

### 3. Detailed per-Step plan

For each Step:
- **Technique**: the refactoring to apply
- **Target**: file:line or function/class name
- **Change**: concretely what changes, and how
- **Affected files**: other files this change requires editing
- **Risk**: low/medium/high + why
- **Rollback**: how to undo on failure

### 4. Overall risk assessment

- Public API changes (function signatures, class interfaces)
- Backward compatibility impact
- Whether tests need updating (state why, if so)
- Overall rollback strategy

### 5. When there are no tests

When the target has no tests and the user agreed at Checkpoint ①, the
plan opens with a formal **Step 0 — Characterization tests**:
- **Target**: every function/class a later Step touches
- **Change**: pin current behavior per `references/characterization-testing.md`
  — list the inputs per target (happy path, boundaries, branch drivers),
  the capture method (golden value / approval snapshot), and where the
  tests live
- **Affected files**: the new test files only
- **Rollback**: delete the test files
Step 0 is its own commit. Its green run is the "Before" that Verify
compares against; Execute re-records the test inventory after it.

If the user declined Step 0, slice each Step smaller and name the
**alternative check** in every Step: the check commands (typecheck,
build, lint) plus an entrypoint run with fixed inputs whose output is
diffed before/after. Verify reports this evidence level explicitly.

## Output format (출력 형식)

Return a numbered list of Steps.
Each Step must be an independently committable unit.

End the report with a status line —
`DONE | DONE_WITH_CONCERNS | NEEDS_CONTEXT | BLOCKED` plus one line of
reason. If the analysis input is too thin to plan from, report
NEEDS_CONTEXT rather than padding the plan with assumptions.
