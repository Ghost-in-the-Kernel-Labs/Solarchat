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

Last review: d9b72fd (2026-11-21, tune-up commit, J-016)

## Entries

An entry is `### <date> · <task> · <model>` and these lines:

- **Task**: what the agent was asked.
- **Opened**: the files it opened, in order.
- **Complaints**: what slowed or misled it.
- **Suggestions**: what it would change.

### 2026-11-20 · TODO 1.4 the seed pack, first draft (demo) · Claude Opus 5.5

- **Task**: draft the seed pack under `packs/seed-mc4-leads/` to the provisional layout, from public sources read in the session; mid-task, a brief change (SC-007) allowed web pictures under `images/third-party/`.
- **Opened**: `docs/ROADMAP.md`, `theGhost.md` (SC-005), `docs/journal/J-000-099.md` (J-010, J-011), `docs/SUPPLY-CHAIN.md` (rule 6), `docs/when/handoff.md`, `docs/NAVIGATION-LOG.md`, `scripts/fast.sh`.
- **Complaints**: the mid-task change allowed pictures "under ordinary copyright", which `CLAUDE.md`'s three rules (C-033) forbid in the repository, and the change was not yet on the branch to read; I kept to openly licensed pictures. Several public-body sources sat behind bot checks (403, 503), so the strongest government guidance on mismatched connectors could not be read.
- **Suggestions**: write SC-007 so it states its relation to C-033 before a worker gets it; give the provisional layout a field for a photo's alt text.
