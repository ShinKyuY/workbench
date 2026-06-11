# Report Contract (보고 계약)

Common output rules for every dispatched analysis agent. They apply
together with the "Output rules" section of each agent's
instructions.

## Report format

- Write the report in the same language as the user request quoted
  in your prompt (Korean request → Korean report). Keep code
  identifiers, file paths, and technical terms in their original
  form.
- Write the report as markdown sections that can be merged into the
  final analysis document as-is. Compress with tables, diagrams, and
  code references instead of prose (target ~200 lines total).
- Attach file:line evidence to every shape and number claim. A claim
  you cannot back with evidence either gets dropped or moves to the
  "unverified/assumed items" block.
- Read the source code first. docs/README are supplements. When code
  and docs conflict, the code is right — and record the conflict.
- Abstract descriptions like "x is the input tensor" are
  insufficient. Concrete values like `img: [3, 224, 224], float32`
  are required.
- Do not modify any code. Analysis agents are read-only.

## Status header (at the very top of the report)

```
status: COMPLETE | PARTIAL | BLOCKED
```

- **COMPLETE**: everything in the assigned scope was confirmed in
  code.
- **PARTIAL**: the report is written, but parts could not be
  confirmed (file not found, shapes decided at runtime, ...).
- **BLOCKED**: the specified files do not exist or the scope is
  wrong, so no meaningful analysis is possible. Report what you
  tried and what information you need.

Silently submitting work you are unsure about is the worst outcome.
When in doubt, declare PARTIAL — the orchestrator fills the gaps.

## Unverified/assumed items (at the very end, required)

List everything you could not confirm directly in code and filled in
by inference instead. If there is none, write "none".

```
## Unverified/assumed items
- T (sequence length) is decided at runtime — only confirmed up to
  config max_len=200 (config.yaml:14)
- negative sampling ratio: config exists but no call site found
```

## Self-review before submitting

Check yourself right before reporting; fix what fails, then submit:

1. Does every shape/number have file:line evidence?
2. Did I state the input-boundary and output-boundary shapes of my
   scope? (The orchestrator cross-checks them against other agents'
   results.)
3. Are the examples real values confirmed in code, not placeholders?
4. Is everything I could not confirm listed under
   "unverified/assumed items"?
