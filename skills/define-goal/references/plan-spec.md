# Plan/Spec Writing Standard — 복잡한 목표의 계획 기준

The goal (`goal.md`) is the frozen success authority. The plan
(`plan.md`) is the living execution document the executor writes
**before implementing** and maintains at every milestone boundary. This
file is the standard the goal text should hold that plan to — when
defining a complex goal, point the executor here, or copy the template
below into the goal if the executor won't have access to this skill's
files.

## Why plan-first

A frozen goal alone tells the agent *what* must be true, but on long
work each step's *approach* gets re-derived from scratch — agents drift,
redo decisions, or silently switch approach mid-run. A referenced plan
pins those decisions between sessions while the goal stays the only
authority on success.

## Quality rules (품질 규칙)

1. **Zero context (맥락 제로 기준).** Write for a fresh agent that knows
   nothing about this work: exact file paths, exact commands with
   expected output, links to docs it would need. Test: if the plan's
   author vanished, could a new agent pick it up tomorrow and execute
   without asking anything the plan should have answered?
2. **No placeholders (자리표시자 금지).** These are plan failures, not
   entries: "TBD", "TODO", "나중에 구체화", "add appropriate error
   handling", "write tests for the above" without the actual cases,
   "similar to M2" (repeat the content — the reader may not read in
   order). Be concrete or leave it out.
3. **Milestone right-sizing (단위 크기).** The smallest unit that
   carries its own verification cycle and ends in an independently
   verifiable deliverable. Fold setup/scaffolding/config into the
   milestone whose deliverable needs them; split only where a reviewer
   could reject one milestone while approving its neighbor.
4. **Interfaces pinned (인터페이스 고정).** Record the names,
   signatures, formats, and contracts that later milestones depend on —
   exactly. Later work must match earlier work instead of re-deriving
   it; drift here is how months-long work quietly forks.
5. **Verification per milestone (단계별 검증).** Every milestone carries
   its command/check and expected result, traceable to the goal's "Done
   when". A milestone isn't done until its check passes — **stop-and-fix**
   before moving on.

## Template (템플릿)

```
# Plan — <goal one-liner> (goal: <path/to/goal.md>)

Decisions:
- <interface/contract decisions later milestones rely on — exact names,
  signatures, formats. Append as they are made.>

Milestones:
- [ ] M1 <independently verifiable deliverable>
      approach: <how, concretely>
      files: <exact paths>
      verify: `<command>` → <expected result>
- [ ] M2 ...

Status: <current milestone / last verified checkpoint / open questions>
```

Keep it short — a milestone table, decisions, and status. A plan nobody
rereads is ceremony.

## During execution (실행 중)

- At each milestone boundary: tick the checkbox, update Status, record
  new decisions and approach changes.
- **Goal frozen, plan living:** if a plan change would alter the goal's
  outcome, thresholds, or scope — that is not a plan update. Stop & ask
  the user.
