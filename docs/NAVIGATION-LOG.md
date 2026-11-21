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

Last review: 8746b10 (2026-11-21, tune-up commit, J-052)

## Entries

An entry is `### <date> · <task> · <model>` and these lines:

- **Task**: what the agent was asked.
- **Opened**: the files it opened, in order.
- **Complaints**: what slowed or misled it.
- **Suggestions**: what it would change.

### 2026-11-21 · Tune-up commit 1 (J-052) · Claude Sonnet 5.5

- **Task**: the tune-up commit due after 30 commits (SC-009): steps 1, 4, 5 and 6 of `docs/when/tune-up.md`, changing no result.
- **Opened**: `docs/when/tune-up.md`, `docs/NAVIGATION-LOG.md`, `docs/when/handoff.md`, `docs/paths/process.md`, `docs/when/coordinate.md`, `docs/HANDOFF.md`, `scripts/checks/claude_md.py`, `scripts/next_id.py`, `docs/journal/J-000-099.md`.
- **Complaints**: the brief said to symlink the main checkout's `.venv`, while `docs/when/coordinate.md` says a worker never symlinks `.venv` itself (the gate would record it); the document was followed. The worktree shell refuses git joined to other steps. The brief's journal id (J-052) and the id `scripts/next_id.py` gives (J-051) differ by design, which is the collision the debriefs named.
- **Suggestions**: the brief's template could say "a real `.venv/` directory of symlinks", as `docs/when/coordinate.md` does.
