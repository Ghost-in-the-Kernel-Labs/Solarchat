# Navigation log: what agents found hard to find

Each new task goes to a fresh agent of the grade it is placed at (C-026, C-036; `docs/when/grades.md`). At the end of its task the agent
debriefs here: one entry, its complaints and suggestions about finding its way (routing rows,
documents, names, rules that were unclear), not about the task's code. "none" is an answer.

**The review is part of every tune-up** (steps 4 and 5 of `docs/when/tune-up.md`; C-024, C-025;
`scripts/commit.sh` says when one is due): read the entries for what agents who did not see each other converge on; wipe the entries
(git keeps them); check each item against the code and act on the valid ones; take an open question
to the ruling grade; record the review in the journal; set the line below to the commit the
review ran at (`git rev-parse --short HEAD`, not the tune-up's own, which does not exist yet). Each entry's **Opened** list, read against the routing row its task matched, is the measure
of whether a fresh agent found its way: files, in order; `CLAUDE.md` does not count.

Last review: 97e1a80 (2026-11-22, tune-up commit, J-076)

## Entries

An entry is `### <date> · <task> · <model>` and these lines:

- **Task**: what the agent was asked.
- **Opened**: the files it opened, in order.
- **Complaints**: what slowed or misled it.
- **Suggestions**: what it would change.

### 2026-11-22 · Tune-up commit 2 (J-076) · Claude Sonnet 5.5

- **Task**: the tune-up commit due after 25 commits (SC-009): steps 1, 4, 5 and 6 of `docs/when/tune-up.md`, changing no result.
- **Opened**: `CLAUDE.md`, `docs/when/tune-up.md`, `docs/NAVIGATION-LOG.md`, `docs/when/handoff.md`, `docs/paths/process.md`, `docs/HANDOFF.md`, `docs/JOURNAL.md`, `docs/journal/J-000-099.md`.
- **Complaints**: the brief named J-076 while `scripts/next_id.py` gave J-075 (by design, For Ghost 21); no document said what to do then, which this commit now says in `docs/when/handoff.md`. The Last review line of the previous commit (8746b10) is not the commit the brief names (a52f417).
- **Suggestions**: none.

### 2026-11-22 · The worker's-words step designed (1.10, J-075) · Claude Opus 5.5

- **Task**: design the rest of 1.10 and take Ghost's trigger decisions.
- **Opened**: `evals/v1.json`, `solarchat/safety/rules.json` (SR-07, SR-08, SR-14), `TODO.md` (1.10).
- **Complaints**: none.
- **Suggestions**: a script that runs the triggers over the frozen set's questions would make such a table one command.
