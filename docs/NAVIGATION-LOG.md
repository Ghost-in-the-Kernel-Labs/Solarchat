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

### 2026-11-21 · TODO 1.3 The safety rules, version 1 · Claude Opus 5.5

- **Task**: write the safety rules, version 1, as data in the `safety` module with a generated document, and make the pack check refuse a pack that names or overrides a rule.
- **Opened**: `docs/paths/process.md`, `docs/modules.json`, `solarchat/leaf/contract.py`, `solarchat/leaf/__init__.py`, `scripts/checks/packs.py`, `scripts/directive_map.py`, `test/test_packs.py`, `test/test_directive_map.py`, `test/test_leaf.py`, `test/support.py`, `test/fixtures/packs/good/`, `docs/ROADMAP.md`, `docs/CONTRACT.md`, `docs/GLOSSARY.md`, `theGhost.md` (SC-010), `docs/SAFETY-AND-COMPLIANCE.md`, `TODO.md`, `scripts/checks/readability.py`, `scripts/fast.sh`, `scripts/checks/common.py`, `scripts/checks/imports.py`, `test/test_modules.py`, `docs/when/handoff.md`, `docs/when/hand-out-a-task.md`, `docs/JOURNAL.md`, `docs/journal/J-000-099.md`.
- **Complaints**: no workpath row names the `safety` module or the pack check's safety half; the brief carried them. The contract's HAD-04 says the safety rules have "a check (TODO 1.3)" without saying what that check holds, so the loader's refusals were the agent's reading.
- **Suggestions**: a row in `docs/paths/process.md` (or a new `docs/paths/safety.md`) for "a safety rule: add or change one", starting at `solarchat/safety/rules.json`, `docs/SAFETY-RULES.md` and `scripts/safety_rules_doc.py`, tests `test/test_safety.py`.

