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

Last review: 7ef5101 (2026-11-21, Tune-up pass 0, J-019)

## Entries

An entry is `### <date> · <task> · <model>` and these lines:

- **Task**: what the agent was asked.
- **Opened**: the files it opened, in order.
- **Complaints**: what slowed or misled it.
- **Suggestions**: what it would change.

### 2026-11-21 · TODO 1.1, the words · Claude Sonnet 5.5
- **Task**: add six glossary rows (pack, passage, flow, mode, admitted, safety rule).
- **Opened**: docs/GLOSSARY.md, docs/paths/process.md (grep for the row), test/test_glossary.py, docs/ROADMAP.md, theGhost.md (SC-005, SC-002 by awk), docs/CONTRACT.md, packs/seed-mc4-leads/manifest.json, TODO.md, docs/DONE.md, docs/journal/J-000-099.md, docs/NAVIGATION-LOG.md, docs/when/handoff.md.
- **Complaints**: none
- **Suggestions**: none
