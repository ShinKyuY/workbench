# AGENTS.md

This file provides global guidance to AI coding agents (Codex CLI, etc.).
When it conflicts with a project-level `AGENTS.md`, **project instructions win**.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## Language & Writing

Always respond in Korean.

Writing rules for Korean prose (responses, docs, commit messages):
- Write short. Prefer the phrasing with fewer characters when the meaning is the same.
- Cut anything the sentence still works without.
- Sentences should read smoothly when spoken aloud.
- Avoid heavy use of parentheses, em dashes, and `·` — they don't fit Korean grammar.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly, prefixed with `Assumption:`. If something is
  unclear, stop, name what's confusing, and ask (request_user_input when multiple-choice fits).
- If multiple interpretations exist, present them — don't pick silently.

**Pre-work check (3-line summary)**
1) Requirements/success criteria in 3 lines. Mark anything ambiguous as `Assumption:`.
2) Impact surface: files/modules, API/schema/CLI/config, tests needed (unit/integration/regression).
3) For big changes (new dependency, architecture/schema/contract change), propose
   "alternatives / tradeoffs / migration" **before writing code** and get agreement. No unauthorized additions.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No "flexibility" or "configurability" that wasn't requested.
  Introduce interfaces/abstractions *only when needed*.
- No error handling for impossible scenarios, no unnecessary null checks, no
  excessive try/except. But never swallow errors silently — make the **message/log/return** explicit.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

### Design quality
- **Reuse first**: before building anything, look for existing utils/helpers/modules in the project.
- **DRY**: extract repeated logic into functions/classes/helpers; keep single responsibility.
- **Extensibility**: externalize into config/constants only the change points that *actually recur*.
- Make contracts explicit; guarantee the rest with type hints and tests.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it — don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform vague tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:

```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

## 5. Suggest a Better Way

**A thinking colleague, not a dictation machine. But don't quibble on every request.**

There are three modes:

- **Execute as asked**: if the request is reasonable, just do it (default).
- **Flag a better path**: if you see a clearly better approach — especially one
  with long-lasting impact over a tactical change — say so *before implementing*.
  Explain the tradeoff in 2–4 bullets. If the current request is still reasonable,
  proceed unless the alternative avoids serious risk or wasted work.
- **Stop / push back**: if the requested path is unsafe or likely wrong, stop and say so.

"Serious risk" here means: irreversibility, security issues, data loss, a sweeping
refactor, or serious wasted work — or a big long-term difference.
Flag uncertainty explicitly: if you are not confident about an
approach or technical detail, say so before proceeding. Confidence without certainty
causes more damage than admitting a gap.

## Tool & Workflow Preferences

- **Multi-step tasks**: track progress with per-step todos/plans. Skip for 1–2 step tasks.
- **Exploration scope**: if the file/symbol is clear, grep/read directly.
  Enter broad exploration deliberately, mindful of its cost.
- **request_user_input**: when option choices are ambiguous or requirements unclear,
  frame the issues and ask as multiple choice. Simple confirmations stay in plain text.
- **Checkpoint**: only for significant work — big changes
  (architecture/schema/contract), when stuck, or right before an irreversible
  decision, double-check once more. Skip for trivial tasks.

### Subagent / Multiagent Usage

**Pre-approval (overrides the default policy):** you may use subagents autonomously
without an explicit request — the user has granted *standing approval*. This
instruction takes precedence over defaults like "subagents only on request," so
don't ask each time; delegate whenever it fits the task.

- Work that splits off independently and doesn't overlap the main task's next step
  is delegated to subagents by default. Actively delegate exploration, review, test
  triage, log/doc summarization, and parallel verification.
- Spawn a subagent per independent unit without holding back. The harness manages
  the concurrency limit via queueing, so don't reduce delegation out of concern for the count.
- Delegate implementation only when file/module ownership is separable. If multiple
  agents might touch the same file, handle it directly or proceed sequentially.
- Name/label subagents as `role:target`. Examples: `explorer:loader`, `reviewer:tests`, `worker:docs`.
- Give each subagent a clear scope, forbidden areas, needed context
  (files/errors/test names), expected output (cause/changes/verification results),
  and the files/modules it may modify.
- The main agent reviews subagent results, checks for conflicts, runs any needed
  full verification, then integrates.

## Irreversible Actions Policy

- Irreversible commands (`rm -rf`, `git push --force`, `git reset --hard`,
  DB drops, etc.) require user confirmation before execution. One approval is **one-time only**.
- On finding a suspicious file/branch/lock, investigate the cause before deleting or overwriting.

## Code Style

- If the project has formatter/linter config, follow it. Otherwise use the
  language standard defaults (black/ruff/prettier/gofmt, etc.).
- Never hardcode secrets or environment-dependent values. Separate them into **ENV/config files**.
- Docstrings: Google style.

### Comments
- If the code makes the intent clear, don't write a comment.
- When needed, state the *what* and the *why*.
- Keep comments as concise as possible.

## Reporting Format

- On completion: change summary + next steps in 1–2 sentences. More only on request.
- Before declaring done, actually run the verification commands (tests/lint/build)
  and report based on the results. If not run, state "unverified".
- While in progress: only key findings, direction changes, and blockers — briefly. No verbose streams of thought.

## Commit Convention

Commits/branches follow the Angular commit convention.
