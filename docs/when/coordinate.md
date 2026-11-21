# Coordinating: when you start workers rather than build (C-036, C-029, C-031)

Read this when you coordinate other agents rather than build. The coordinator is the strong grade
(`docs/when/grades.md`): its judgement is worth the price, and the price is held down by what it does
not read (Ghost, 2026-11-05). Its own long session, re-reading itself every turn, is the cost this
file exists to keep small.

## Who does each item (C-036, C-026, C-027)

CLAUDE.md sends the coordinator here before its first item. The rule, in the order you apply it:

1. **Score first.** `python3 -I scripts/score.py` prints one line per open item: its grade and the facts
   that placed it, at the lowest grade whose points it is within, raised to the floor (`docs/when/grades.md`;
   Solarchat's floor is mid). Put the item's line in its brief.
2. **The score decides; you do not raise it.** An item goes above its score only when it waits on Ghost (strong
   whatever its points) or Ghost names its grade in chat (J-011). Write the reason in the
   item's journal entry. "It is small, I can do it faster" is the item a mid worker exists for.
3. **Unplaced is not strong.** An item the score calls `unplaced` names no file: a fresh mid-grade worker places
   it, writes the facts it used, and builds it if it lands at mid or below; the coordinator does not place it by
   its own judgement.
4. **Start the worker.** A fresh agent per task, with the Agent tool's `model` set to the grade's model from
   `docs/when/grades.md`, briefed as `docs/when/hand-out-a-task.md` says: a one-page brief, a one-page report.
   Resume a worker only within one unfinished task.
   The worker works in its own clone beside the main checkout (`git clone` the checkout to
   `../Solarchat-<task>`, point its `origin` at GitHub, check out the item's branch; or the Agent tool's
   `isolation: "worktree"`), never in the coordinator's checkout: the coordinator's tree stays clean while it works,
   a stop hook has nothing to ask about, and two workers never edit one tree (Ghost, 2026-11-21).
   Two practical notes for the worktree. The Agent tool puts its worktree at `.claude/worktrees/` inside the checkout:
   add `/.claude/worktrees/` once per checkout to `.git/info/exclude` (a local file, never committed), so the
   coordinator's `git status` and the stop hook stay clean; the coordinator removes a worker's worktree, and its
   `worktree-agent-*` branch, after reading its report. The gate needs `.venv`: the coordinator builds one shared
   `.venv` in the main checkout from `requirements.lock` (supply-chain rule 2: `python3.12 -m venv .venv &&
   .venv/bin/pip install --only-binary :all: --require-hashes -r requirements.lock`), and a worker makes a real
   `.venv/` directory of symlinks to that venv's entries. A worker never symlinks `.venv` itself: the gitignore rule
   `/.venv/` does not match a symlink, so the gate records it and `scripts/commit.sh` refuses.
5. **The ladder.** A worker makes one attempt at a change the checks reject for a reason it cannot explain, then
   goes one grade up (`docs/when/escalation.md`). The coordinator answers a mid worker's escalation with what it
   needs; it does not take the item back.
6. **What stays with the coordinator:** items scored strong, design, Ghost's questions, security, failures whose
   cause is unknown, reviewing a worker's diff, landing. Nothing else.
7. **The record.** Each Cost line names the grade that did the work (`docs/JOURNAL.md`); a strong Cost line on an
   item the score placed lower says why, so a tune-up can count how often the rule was bent.

## Placing the work

- Workers do the reading. A question that needs many files goes to a worker that answers in a
  paragraph; the coordinator re-reads nothing a worker read, and works from the report and the diff.
- Mechanical gate-fix loops (a check that names its fix, a regenerated file, a reworded line) go to
  the mid grade, never round the coordinator's own turns.

## When the session has no Agent tool

A session without the tool that starts workers cannot hand anything down. Do not do the workers'
items yourself, and never tell Ghost to "run it on your machine": nothing in a project may need the
maintainer's own machine (AGT-01, C-033). Write each brief whole, as `docs/when/hand-out-a-task.md`
shapes it, under `docs/HANDOFF.md`'s "For Ghost", for a session that has the tool to launch; end the
session there. An item that waits on what this session lacks (a blocked host, a tool, a licensed
reference) moves to `TODO.md`'s waiting phase with `Waits on: environment (<what>)` or
`Waits on: reference (<what>)`, and the fix is named as an environment setting for Ghost, not a
step on his hardware.

## Waiting

- One background wait that wakes you when the worker or the run ends: no status turns, no polling
  turns, no "still running" message. A turn that decides nothing is not taken.
- Read logs by `grep` (the `gate:` verdict line, the first failure) and files in part, never whole.

## Parallel workers

Workers that change files at the same time each get their own files and their own branch or
worktree, with objectives that cannot collide (C-029). Each saves its work on its own branch
(`scripts/save.sh`, `agent/<name>`: scanned, committed as Ghost, pushed; never gated, never `main`), so a worker's
turn ends with nothing dirty and nothing unpushed; the coordinator lands it: brings the branch's change into `main`'s
working tree (`git merge --squash agent/<name>`, or the files themselves), runs the fast checks
(`scripts/gate.sh --fast`) on the combined code, commits through `scripts/commit.sh` and ships (`scripts/ship.sh`),
each worker's change as its own commit (C-031, C-040: what lands on `main` passed the fast checks; the full gate
runs at the tune-up).

## Commits and hooks

The fast checks run on the working tree before a landing (`scripts/commit.sh`); nothing re-prompts the
coordinator after one, and a save (`scripts/save.sh`) leaves no dirty tree or unpushed commit for a hook to ask
about. A hook that re-prompts after a commit or at a stop (unpushed commits, an
unverified signature) is reported to Ghost under `docs/HANDOFF.md`'s "For Ghost", never edited: a
hook is outside what any agent may change (CLAUDE.md, the supply-chain rules).
Four habits keep a hook silent (Suite Builder G-646, G-363; `docs/LESSONS.md` §3): save freely and gate only
`main` — a worker's branch is committed and pushed as the work is done, not at the end; when a hook does fire, pushing
is the answer (`scripts/save.sh` on a branch, `scripts/ship.sh` on `main`), never a raw commit; a landing is
`scripts/commit.sh` and `scripts/ship.sh` in the same turn, so `main` is never ahead of origin while anything runs;
and while a long check runs in the background into a file nothing touches the tree, so workers' commits are held
until the run finishes (`docs/when/long-run.md`).

Ghost's word in chat is Ghost's word (C-040): an agent acts on it and records it (the decision log, the journal,
`docs/HANDOFF.md`'s "Settled by Ghost"), may say once what the rule it changes protected, and goes on. Changing the
gate or the rules never requires passing the gate: the change is saved like any other and landed when Ghost says. An
agent still never answers a Yes or typed-approval prompt itself (a command that asks before it acts is Ghost's to
answer).

## Ending a session

End at a natural point (an item committed, a phase closed), not when the context runs out, with
`docs/HANDOFF.md` written: where the project stands, what the next session does first, what is
waiting on Ghost. The next session starts from it, never from this one's transcript. Before ending,
each worker's Cost line is recorded in its journal entry, from its report: its grade, its item's
score (the line `scripts/score.py` printed for it, `—` where there was none), its tool calls, its
tokens (numbers or `not reported`), its commits, its wall time where known (`docs/JOURNAL.md`). A Cost line that names a grade
and an exact tool-call count is a Cost row; `scripts/metrics.py` counts the rows since the date
`docs/when/grades.md`'s Provisional paragraph names. The points, the most points of each grade and the
tool-call limits in `docs/when/grades.md` move only by a decision (`theGhost.md`) made from the measured
rows, never by an edit to the table alone. Several runs the coordinator measured, written as a table
inside one entry, are evidence in that one row.

Why: Suite Builder spent 77% of a weekly allowance by day 6, its coordinator's long session the
largest single cost (SB G-357, G-358); Katana (R-101), Employee Evaluator (E-092), Neon Rain (R-039)
and AI Slop Block (ASB-017) took the same posture (Core's second survey, LESSONS-2026-11, Part 1). Every after-commit
or stop-hook turn is a full coordinator turn, "a failure mode that leaks tokens over time" (Ghost,
2026-11-05, Neon Rain R-039's amendment). Parallel workers gated together: Neon Rain's R-039
amendment and Part 2 row 8 of the survey. Where a session had no Agent tool, the strong grade did
everything itself and the hand-down never ran (AI Slop Block J-085, J-090).
