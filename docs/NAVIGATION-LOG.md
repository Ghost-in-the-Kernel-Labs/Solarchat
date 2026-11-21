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
### 2026-11-21 · TODO 1.3 The safety rules, version 1 · Claude Opus 5.5

- **Task**: write the safety rules, version 1, as data in the `safety` module with a generated document, and make the pack check refuse a pack that names or overrides a rule.
- **Opened**: `docs/paths/process.md`, `docs/modules.json`, `solarchat/leaf/contract.py`, `solarchat/leaf/__init__.py`, `scripts/checks/packs.py`, `scripts/directive_map.py`, `test/test_packs.py`, `test/test_directive_map.py`, `test/test_leaf.py`, `test/support.py`, `test/fixtures/packs/good/`, `docs/ROADMAP.md`, `docs/CONTRACT.md`, `docs/GLOSSARY.md`, `theGhost.md` (SC-010), `docs/SAFETY-AND-COMPLIANCE.md`, `TODO.md`, `scripts/checks/readability.py`, `scripts/fast.sh`, `scripts/checks/common.py`, `scripts/checks/imports.py`, `test/test_modules.py`, `docs/when/handoff.md`, `docs/when/hand-out-a-task.md`, `docs/JOURNAL.md`, `docs/journal/J-000-099.md`.
- **Complaints**: no workpath row names the `safety` module or the pack check's safety half; the brief carried them. The contract's HAD-04 says the safety rules have "a check (TODO 1.3)" without saying what that check holds, so the loader's refusals were the agent's reading.
- **Suggestions**: a row in `docs/paths/process.md` (or a new `docs/paths/safety.md`) for "a safety rule: add or change one", starting at `solarchat/safety/rules.json`, `docs/SAFETY-RULES.md` and `scripts/safety_rules_doc.py`, tests `test/test_safety.py`.


### 2026-11-21 · Landing the safety rules (TODO 1.3) on page citations · Claude Opus 5.5

- **Task**: land `agent/safety-rules-1-3` (da684a2) on `main` past the coordinator section and SC-012: renumber its journal entry to J-027, bring its two planted-break packs to the page-citation format, keep both sides of every doc, record that Ghost has not read `docs/SAFETY-RULES.md` and the five points stay open.
- **Opened**: `CLAUDE.md`, `docs/when/coordinate.md`, `scripts/commit.sh`, `scripts/ship.sh`, `docs/HANDOFF.md`, `TODO.md`, `docs/DONE.md`, the six conflicted files, `scripts/checks/packs.py`, `test/test_packs.py`, the good fixture pack.
- **Complaints**: `docs/AGENT.md`'s two measured figures conflict on every landing that adds source; they are regenerated by `scripts/metrics.py --write`, so the conflict is only a nuisance. The brief's list of generated files did not name `docs/journal/INDEX.md`; `scripts/journal_index.py` writes it.
- **Suggestions**: `next_id.py` should look at `origin/agent/*` branches (the same collision the page-citations debrief named); the two safety fixtures could be built from `good/` by a helper so a format change does not touch them.

### 2026-11-21 · Worktree notes in the coordinator section · Claude Sonnet 5.5

- **Task**: add the two practical worktree notes (the exclude line, the shared `.venv` of symlinks) to `docs/when/coordinate.md` step 4, and say "clone or worktree" in CLAUDE.md.
- **Opened**: `CLAUDE.md`, `docs/when/coordinate.md`, `docs/paths/process.md`, `docs/when/handoff.md`, `scripts/commit.sh`, `scripts/ship.sh`.
- **Complaints**: a worktree-isolated agent's shell refuses git commands chained with `&&`; each git command had to be its own call.
- **Suggestions**: none.

### 2026-11-21 · The approval change (SC-013) · Claude Sonnet 5.5

- **Task**: replace the pack admission record with a `library` or `demo` status: decision, contract, pack check, leaf, fixtures, tests, seed pack, docs.
- **Opened**: `docs/paths/process.md`, `scripts/commit.sh`, `scripts/ship.sh`, `theGhost.md` (SC-005, SC-010, SC-012), `scripts/checks/packs.py`, `solarchat/leaf/contract.py`, `scripts/directive_map.py`, `docs/CONTRACT.md`, `test/test_packs.py`, `test/test_leaf.py`, the fixtures, `docs/HANDOFF.md`, `docs/journal/J-000-099.md`.
- **Complaints**: no routing row for the pack format or the leaf's contract, so the files to open came from the brief; the glossary, `docs/modules.json` and `packs/TYPES.md` also carried the word "admitted" and are in no list; `docs/DONE.md` keeps "admitted" in a finished item's check, left as history.
- **Suggestions**: a routing row "the pack format: change a manifest field" starting at `docs/CONTRACT.md`, `scripts/checks/packs.py`, `test/test_packs.py` and the fixtures; `is_demo` fails open on a bad status (the pack check refuses it first), so the walker should refuse a status it does not know.

### 2026-11-21 · The leaf refuses a status it does not know (SC-013, HAD-06) · Claude Opus 5.5

- **Task**: replace `is_demo` with the fail-closed `may_answer(manifest, demo_mode)` in the leaf, so the walker (TODO 1.6) refuses any pack whose status is not `library` or `demo`; tests, docs, the TODO item and the contract's HAD-06 follow.
- **Opened**: `CLAUDE.md`, `solarchat/leaf/contract.py`, `test/test_leaf.py`, `docs/CONTRACT.md`, `docs/modules.json`, `docs/SAFETY-AND-COMPLIANCE.md`, `docs/DIRECTIVE-MAP.md`, `theGhost.md`, `TODO.md`, `packs/TYPES.md`, `docs/when/handoff.md`.
- **Complaints**: none; `docs/modules.json` and `packs/TYPES.md` name no function, so neither changed. History entries (J-028, earlier debriefs) still say `is_demo` and were left as written.
- **Suggestions**: none.

### 2026-11-21 · The reference library (SC-014) · Claude Sonnet 5.5

- **Task**: pull six public or CC BY source documents into `library/sources/` with licence evidence, text and hashes, add `scripts/checks/library.py` and its tests, record SC-014; the seventh (OSHA solar pages) was refused by its host.
- **Opened**: `docs/paths/process.md`, `theGhost.md` (SC-012, SC-013), `scripts/checks/packs.py`, `scripts/checks/common.py`, `test/test_packs.py`, `test/support.py`, `scripts/fast.sh`, `docs/NAVIGATION-LOG.md`, `docs/HANDOFF.md`, `docs/journal/J-000-099.md`.
- **Complaints**: no routing row for a new check's wiring; "wire it into the fast loop" turned out to mean a unittest file, which is only learned by reading `fast.sh`. A new file must be `git add -N`ed before the fast loop sees it, which is easy to miss. The worktree shell refuses compound git commands and heredocs that `cd` elsewhere.
- **Suggestions**: a routing row for the library (added to `docs/paths/process.md`); a one-line note in `docs/when/coordinate.md` that downloads may sit in the scratchpad.

### 2026-11-21 · The safety rules' triggers and wording (J-030) · Claude Opus 5.5

- **Task**: apply the audit's per-rule trigger and wording proposals to SR-01 to SR-14, define whole-word matching under HAD-04 with `rules_fired`, pin what the demo pack fires, resolve SR-03's mark.
- **Opened**: `CLAUDE.md`, `docs/paths/process.md`, the audit, `solarchat/safety/rules.json`, `solarchat/safety/rules.py`, `docs/CONTRACT.md` (HAD-04), `docs/modules.json`, `TODO.md` (1.7), `test/test_safety.py`, `scripts/safety_rules_doc.py`, `solarchat/leaf/contract.py`, the seed pack's `steps.json` and `failures.json`, `docs/HANDOFF.md`, `docs/journal/J-000-099.md`.
- **Complaints**: no routing row for the safety rules; the leaf's "a rule has triggers" conflicts with the audit's "drop SR-01's triggers"; the worktree shell refuses heredocs and chained git commands, and `docs/` has no place for a decision of Ghost's that is not a numbered decision.
- **Suggestions**: a routing row "the safety rules: a trigger or a rule's words" (`solarchat/safety/rules.json`, `docs/CONTRACT.md` HAD-04, `test/test_safety.py`); decide whether a rule may have no triggers (SR-01 always applies).
