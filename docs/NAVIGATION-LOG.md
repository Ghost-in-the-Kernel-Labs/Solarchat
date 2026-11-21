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

Last review: 82fd905 (2026-11-21, tune-up commit, J-025)

## Entries

An entry is `### <date> · <task> · <model>` and these lines:

- **Task**: what the agent was asked.
- **Opened**: the files it opened, in order.
- **Complaints**: what slowed or misled it.
- **Suggestions**: what it would change.

### 2026-11-21 · Coordinating 0.4 to 1.3, two tune-ups, the demo plan · Claude Opus 5.5

- **Task**: coordinate Solarchat through TODO 0.4, Tune-up pass 0, 1.1 to 1.3 (three workers), SC-009 to SC-011, the manifesto's restoration and the first human maintainability pass; then hand off.
- **Opened**: `docs/HANDOFF.md`, `TODO.md`, `docs/paths/process.md`, `docs/CONTRACT.md`, `docs/modules.json`, `docs/when/tune-up.md`, `docs/when/hand-out-a-task.md`, `docs/when/coordinate.md`, `scripts/commit.sh`, `docs/GHOST-IN-THE-KERNEL.md`, and each worker's diff.
- **Complaints**: the session began on the wrong repository, its branch name already used and the repository's default branch a session branch (all fixed with Ghost). This session cannot delete a remote branch (403). A `--docs-only` landing cannot ship until the fast checks run (written into `docs/paths/process.md`, J-019). Three workers shared one checkout, so the coordinator could edit nothing while one ran.
- **Suggestions**: give each worker its own worktree, so the coordinator can keep landing while a worker builds; `scripts/save.sh` could print the remote's redirect once rather than on every push.

### 2026-11-21 · The coordinator's conditional in CLAUDE.md · Claude Opus 5.5

- **Task**: Ghost: few mid-grade workers are started; give CLAUDE.md a conditional that sends the coordinator, and
  only the coordinator, to the agent-assignment logic of the ghost (C-026, C-027, C-036).
- **Opened**: `docs/HANDOFF.md`, `docs/when/coordinate.md`, `docs/when/grades.md`, `scripts/checks/claude_md.py`,
  `docs/AGENT.md`.
- **Complaints**: the session opened with three Ghost projects side by side and its assigned branch in another
  one; "the handoff document" matched three files, and the agent read the wrong project's twice before Ghost named
  this one. Nothing in the repositories says which of several open projects a brief means.
- **Suggestions**: a line in each project's CLAUDE.md: when more than one Ghost project is open and the brief names
  none, ask which before reading. `scripts/score.py` calls five of 1.3 to 1.9 `unplaced`: their items name no
  file, so the score cannot place them and a coordinator is tempted to keep them; items that name their files.

### 2026-11-21 · Workers out of the checkout · Claude Opus 5.5

- **Task**: Ghost: run every worker in its own clone beside the main checkout, and record it in CLAUDE.md.
- **Opened**: `CLAUDE.md`, `docs/when/coordinate.md`.
- **Complaints**: a worker editing in the coordinator's checkout set off the stop hook's "uncommitted changes"
  while it ran; the coordinator could not commit without saving the worker's half-done tree.
- **Suggestions**: none beyond the rule itself, which answers the earlier debrief's worktree suggestion.

### 2026-11-21 · Page citations in the pack format (SC-012) · Claude Sonnet 5.5

- **Task**: add a source `kind` and page citations to the pack format: decision, contract, pack check, tests, demo pack; save on `agent/page-citations`.
- **Opened**: `docs/paths/process.md`, `scripts/save.sh`, `theGhost.md` (SC-010, SC-011), `docs/CONTRACT.md`, `scripts/checks/packs.py`, `test/test_packs.py`, the seed pack's manifest, steps and failures, `docs/HANDOFF.md`, `docs/JOURNAL.md`.
- **Complaints**: the pack check reads passages, flows and procedures, while the demo pack is steps and failures, so the demo pack's citations are not held by any check until TODO 1.4; the brief's "steps, failures" and the contract's passage types differ. No row in the process path says which of the decision, journal, index and directive-map commands run in which order for a new decision. The next journal id (J-026) is already taken on an unmerged branch.
- **Suggestions**: a routing row for the pack format naming `scripts/checks/packs.py`, its test and the fixtures; have `next_id.py` look at the `origin/agent/*` branches too.
