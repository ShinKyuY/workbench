---
name: handoff
description: >-
  Create/update HANDOFF.md so the next agent can take over from a cold
  start. Use on any work-continuity request — "handoff", "continue in
  the next session", "인수인계", "다음 세션에서 이어서", "여기까지
  정리해줘" — or when ending a session with background jobs running,
  nearing the context limit, or delegating to another agent. Not for
  reading an existing HANDOFF.md, commit messages, or meeting notes.
---

# Handoff Document Generation (인수인계 문서 생성)

Write a structured HANDOFF.md so the next agent can **reach the same
point within 30 seconds**. Length is not the goal. The three things that
matter most: **verified state, repro steps, next actions**.

Write the handoff document in the language of the conversation
(Korean session → Korean document); the template structure stays the
same.

## Procedure (작성 절차)

### 1. Check existing docs and gather context

Collect the following in parallel first:
- Check the working directory for `HANDOFF.md` or `HANDOFF-*.md`;
  Read it if present.
- `git status`, `git diff --stat`, `git log --oneline -5` for the
  objective change state (skip if not a git repo).

### 2. Analyze the session

Extract from the conversation history:
- Distinguish **what was actually verified** from **code written but
  never run** — the most important split.
- The user's decisions/feedback/rejected directions.
- Approaches that were tried and failed, and why.
- Work that keeps running after the session ends (submitted jobs,
  background processes, deployments, ...). Do not guess IDs — confirm
  the actual values from logs/submission records; when something was
  cancelled and resubmitted, make sure it is the last valid ID.
- Next steps and their priority.
- Undecided items that need the user.

### 3. Write the document

Use the template below. Mark empty sections `_(none)_` explicitly
rather than deleting them — so the next agent never wonders "not
recorded, or really none?".

Additional rules:
- **Repro commands: only ones actually run** — run them and check the
  output before writing them down. Mark commands you could not run with
  `(unverified)` — an unverified command turns the next agent's first
  30 seconds into debugging.
- **Decision-log bar**: record only decisions/failures that would change
  the next agent's behavior. Minor progress notes are already covered by
  the verification table and changed files — a bloated log buries the
  decisions that matter.
- **No secrets**: never write tokens/passwords/credentials in plain
  text. Point to file paths or ENV variable names instead — handoff
  documents live long and get copied to unknown places.

```markdown
# Handoff — {task title}

**Last updated**: {YYYY-MM-DD HH:MM}
**Working directory**: {absolute path}
**Branch**: {git branch, if applicable}

## Next steps

1. {first thing to do — concrete verb}
2. {then}
3. {then}

## Running work

Work that keeps running after the session ends. If none, `_(none)_`.

| Task | Identifier | Status check | When done |
|------|------------|--------------|-----------|
| {e.g. training job} | {job ID / PID} | {e.g. mlx job status {ID}} | {e.g. run eval on the checkpoint} |

## Open questions

Items the next agent must not decide alone. Check with the user first.

- {question 1}
- {question 2}

## Goal

{What we are ultimately trying to achieve. 1–2 sentences.}

## Verification status

| Item | Status | How verified |
|------|--------|--------------|
| {feature/module} | ✅ verified working | {e.g. pytest tests/foo.py passes} |
| {feature/module} | ⚠️ code written, not run | - |
| {feature/module} | ❌ failing | {error summary} |

## Repro commands

Commands the next agent needs to reach the same point from a cold start.

```bash
# Environment setup
{e.g. uv sync, npm install, ...}

# Check the results so far
{e.g. pytest tests/, npm run build, ...}

# Reproduce the failure (if any)
{e.g. python -m foo --debug}
```

## Changed files

Pasting the `git status` / `git diff --stat` output verbatim is
recommended (manual lists drift).

```
{git status output or change summary}
```

## Decision · attempt log (append-only)

History preservation area. Each new session adds entries at the top;
previous entries are never deleted.

### {YYYY-MM-DD} — {short title}
- **Choice**: {adopted approach}
- **Why**: {why this was picked}
- **Alternatives**: {considered and dropped + why}

### {YYYY-MM-DD} — {failed attempt title}
- **Tried**: {what was attempted}
- **Result**: {why it failed}
- **Lesson**: {so the next agent does not repeat it}

## Cautions

{Pitfalls, environment constraints, irreversible actions, user
preferences, ...}

## References

_(only when related design docs/plans/other handoffs exist — otherwise
omit the section entirely)_

- {path — one line on what it is}
```

### 4. Save and announce

- Default path: `HANDOFF.md` at the working directory root.
- With multiple independent workstreams in parallel, split into
  `HANDOFF-<topic>.md` (e.g. `HANDOFF-auth.md`).
- In a git repo, ask the user about adding it to `.gitignore` — the
  default is **do not commit** (it is session state, not a code asset).
  Recommend committing only on explicit request.
- After saving, tell the user the absolute path.

## Update logic (업데이트 로직)

When a HANDOFF.md already exists, sections are handled differently.

**Overwrite (reflect the current state)**
- Next steps
- Running work
- Open questions
- Goal
- Verification status
- Repro commands
- Changed files
- Cautions
- The header's last-updated / branch

**Append-only (history accumulates)**
- Decision · attempt log — add the newest entry at the top. Never
  delete or modify previous entries.

**Custom sections (outside the template)**
- Sections added by previous sessions (measurement tables, domain
  summaries, reference material, ...) stay as-is while still valid;
  update only what needs updating.
- Remove only when invalidated, and leave a one-line note in the
  decision log that it was removed.

## Length guide (분량 가이드)

A long handoff gets skipped by the next agent. Target **200 lines
total**. Beyond that, consider splitting the decision log into a
separate file (`HANDOFF-history.md`).

## When triggered, confirm (트리거되었을 때 확인할 것)

- Whether the user means "everything" or "one specific task" — with
  multiple parallel tasks, confirm which one to hand off.
- If a HANDOFF.md exists but covers unrelated work, create a new file
  (`HANDOFF-<topic>.md`).
- If progress is in an awkward half-done state, record it honestly as
  "not run" in the verification table — preventing the next agent from
  building on a broken foundation is the core value of a handoff.
