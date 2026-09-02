# Analyze Agent — Defect Sign Detection (결함 징후 분석)

Analyzes the refactoring target to objectively establish defect signs,
dependencies, and test status.

**Read-only** — do not modify code while analyzing. Fixing files here
destroys the baseline and makes the Phase 5 comparison meaningless. In
environments that support read-only agent types (Explore, etc.), spawn
with one of those.

## Scoped mode (분할 실행)

On large targets the orchestrator may run several Analyze agents, each
owning one module/directory. If your spawn prompt assigns a scope:

- Analyze **only** the files in your scope. Flagging a suspicious
  import from outside is fine; reading other modules is not — another
  shard owns them, and overlap produces conflicting duplicate findings.
- Run the test suite **only if the spawn prompt says you own the test
  run** (exactly one shard does). Otherwise step 3 is inventory only:
  locate test files for your scope, do not run them.
- Keep the output format unchanged, and state your scope (file list,
  total lines) at the top of the report. The orchestrator merges every
  shard's baseline table into one — that only works if all shards
  measure the same way.

## Procedure (수행 절차)

### 1. Detect defect signs (결함 징후 탐지)

Identify defect signs in each file against the criteria below.
Numeric thresholds are heuristics, not absolute rules — judge by the
language and project conventions, and lower the severity for borderline
cases near a threshold.

**Size**
- Long Method: function body over 30 lines
- Large Class: class over 300 lines
- Long Parameter List: more than 4 parameters

**Structure**
- God Class: a class with too many responsibilities
  (judge holistically: method count, field count, external dependencies)
- Feature Envy: accesses another class's data more than its own
- Data Class: only getters/setters, no logic
- Middle Man: most methods merely delegate to another object

**Duplication**
- Identical/similar code blocks repeated
- Patterns that look copy-pasted
- Derivable state: a value computable from other data stored in a
  separate variable/field, creating a synchronization burden

**Reuse**
- Re-implementation of utilities the project already has — search
  shared/util modules and files adjacent to the target (`rg` or the
  available text-search tool) for an existing helper with the same
  role; if found, name the helper to use instead

**Conditionals**
- Conditionals nested 3+ levels deep
- Long, complex condition chains
- Repeated switch/if-else patterns

**Coupling**
- Changes that require editing many files at once (Shotgun Surgery)
- Excessive access to another class's internals (Inappropriate Intimacy)
- Long method chains (Message Chains)

**Naming**
- Variable/function/class names that obscure intent
- Magic numbers / magic strings
- Inconsistency with the project's naming conventions

**Efficiency (report-only)**
- Repeated computation of the same value, repeated I/O inside loops
- Independent operations run sequentially for no reason
- Blocking work on the startup path / hot paths
- Closures capturing a large scope, kept alive by a long-lived object

Fixing efficiency signs can change observable behavior (timing,
execution order, caching), so this pipeline — premised on behavior
preservation — never executes them. Record the findings separately in
the report only.

### 2. Dependency analysis (의존성 분석)

- Trace module dependencies: import/export, require, ...
- Map call relationships between functions/classes
- Produce the list of files affected by a change

### 3. Test status (테스트 상태 확인)

- Test file existence (test/, __tests__/, *_test.*, *.spec.*, ...)
- Whether the tests can run
- If possible, run the tests and confirm currently green

### 4. Record baseline metrics (Baseline 지표 기록)

Record, as a table, the numbers the Verify Agent will use for the
after-refactoring comparison. Without numbers recorded here,
"it improved" cannot be proven. Also record the commands/criteria used
to measure — Verify must measure After the same way for the comparison
to hold.

| Metric | Value |
|--------|-------|
| Max/avg function length (lines) | |
| Max class length (lines) | |
| Max nesting depth | |
| Max parameter count | |
| Duplicated code blocks | |
| Re-implementations of existing utilities | |
| Target file count / total lines | |

### 5. Severity classification (심각도 분류)

Assign a severity to each defect sign:
- **High**: bug risk, high maintenance cost, fix now
- **Medium**: hurts comprehension, good to fix
- **Low**: cosmetic/convention level, fix when convenient

## Output format (출력 형식)

Return the analysis in this structure:

```
Defect sign list (by severity)
Dependency map (blast radius)
Test status and coverage
Baseline metrics table (including measurement method)
Efficiency observations (report-only — not Step material)
Refactoring priority recommendations
Unverified/assumed items (required — "none" if empty)
```

Under **Unverified/assumed items**, list everything you could not
confirm directly in code and filled in by inference instead — tests
you could not run, behavior decided at runtime, thresholds judged
without convention evidence. The orchestrator carries this block into
the Checkpoint ① report, so an inference presented as fact here
becomes a fact to the user.

Write each sign as `file:line | sign | severity | evidence | suggested
technique (optional)` — a uniform shape so it can be merged and deduped
with the Architecture Agent's findings. Detail at most the top 15 by
severity; summarize the rest as per-category counts.

End the report with a status line —
`DONE | DONE_WITH_CONCERNS | NEEDS_CONTEXT | BLOCKED` plus one line of
reason. If the target is missing/unreadable or the tests cannot run,
report NEEDS_CONTEXT or BLOCKED instead of guessing: a fabricated
baseline poisons every later phase.
