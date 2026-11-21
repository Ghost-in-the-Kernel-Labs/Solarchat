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

### 2026-11-21 · More library sources and the safety rules' citations (SC-014) · Claude Sonnet 5.5

- **Task**: add the eight OSHA pages Ghost pasted and six eCFR regulations to `library/sources/`, add library ids to the safety rules' source titles (SR-03, SR-05, SR-06, SR-11, 1910.333, 1926.1408), check the California FACE solar page, and land it as one commit.
- **Opened**: `CLAUDE.md`, `library/README.md`, `theGhost.md` (SC-014), `scripts/checks/library.py`, `library/sources/osha-1926-k/source.json`, `solarchat/safety/rules.json`, `solarchat/leaf/contract.py` (`SafetyRuleSource`), `scripts/safety_rules_doc.py`, `docs/HANDOFF.md`, `docs/when/handoff.md`.
- **Complaints**: the worktree shell refuses any command that names git together with other steps, and refuses multi-step shell loops, so the downloads and the build ran from scripts in the scratchpad. cdph.ca.gov failed TLS verification through the proxy (not disabled) and the fetch tool answered 503, so the FACE page was not read. `SafetyRuleSource` is title plus url only, so a library id went into the title. `docs/paths/process.md` has no row for adding a rule's source.
- **Suggestions**: a routing row "a safety rule's sources" (`solarchat/safety/rules.json`, `scripts/safety_rules_doc.py`, `test/test_safety.py`); a script in `scripts/` for turning eCFR XML into `text.txt`, since each library task rewrites it.

### 2026-11-21 · The plan against Ghost's vision, proposed (J-031) · Claude Opus 5.5

- **Task**: draft SC-015 (warn and help), SC-016 (the safety rules' change log), F-16 (the engineer's QA) and the roadmap and TODO edits that follow from Ghost's email of 2026-11-21, verify a roadmap review against the repository, commit the safety audit, tidy stale HANDOFF and DONE lines; saved on a branch, not landed.
- **Opened**: `docs/paths/process.md`, the review and the audit (scratchpad), `theGhost.md` (header, SC-010 to SC-014), `docs/decisions.md`, `docs/ROADMAP.md`, `TODO.md`, `docs/DONE.md`, `docs/HANDOFF.md`, `docs/journal/J-000-099.md` (J-027 to J-030), `docs/JOURNAL.md`, `docs/CONTRACT.md`, `solarchat/leaf/contract.py` (`ReplyKind`), `solarchat/safety/rules.json`, the seed pack's `steps.json` and `failures.json`, `packs/TYPES.md`, `scripts/checks/todo.py`, `scripts/checks/ghost.py`, `docs/GLOSSARY.md`, `docs/SAFETY-AND-COMPLIANCE.md`, `scripts/save.sh`, `docs/when/handoff.md`.
- **Complaints**: process.md's roadmap row says how to add items before a tune-up pass but not how to add one before an open item in the middle of a phase; the chain's check reads only `N.M` numbers, so the review's "1.6a" would have passed unseen. `docs/` had no place for an audit or review report, so `docs/audits/` is new. The rule that the journal is append-only (Core C-010) and a brief asking to "fix J-030's reference" pull apart; a correction is a later entry, which the brief did not say. Still no routing row for the safety rules (the second time this is asked).
- **Suggestions**: one sentence in process.md's plan row: "an item placed before an open item takes the next free number and the open item moves behind it, as 2.3 moved to 1.6"; a routing row for the safety rules (`solarchat/safety/rules.json`, `docs/CONTRACT.md` HAD-04, `test/test_safety.py`); name `docs/audits/` in the roadmap's meta-architecture table if Ghost keeps it.

### 2026-11-21 · SC-015 and SC-016 in code, the engineer at the end, the `field` rename (J-032 to J-035) · Claude Opus 5.5

- **Task**: land Ghost's seven answers as three commits (decisions; the code for SC-015 and SC-016; the `field` rename), plus an extra docs commit when Ghost's further word arrived: the engineer comes in only at the end.
- **Opened**: `CLAUDE.md`, `docs/paths/process.md`, `theGhost.md` (SC-013, SC-015, SC-016), `docs/ROADMAP.md`, `TODO.md`, `docs/HANDOFF.md`, `docs/CONTRACT.md`, `docs/SAFETY-AND-COMPLIANCE.md`, `solarchat/leaf/contract.py`, `solarchat/safety/rules.py`, `solarchat/safety/rules.json`, `scripts/safety_rules_doc.py`, `scripts/checks/packs.py`, `scripts/checks/todo.py`, `test/test_safety.py`, `test/test_leaf.py`, `test/test_packs.py`, `docs/journal/J-000-099.md`.
- **Complaints**: the worktree shell refuses any call that names git beside other steps, even a heredoc or a loop in the same call, so every git command and every multi-step edit ran alone or from a script in the scratchpad. `scripts/checks/todo.py` forces items into number order and a tune-up pass last, so items 1.11 to 1.14 cannot rejoin Phase 1 without renumbering the pass; they stay in the waiting phase though nothing outside the repository holds them. `docs/paths/process.md` still has no row for the safety rules.
- **Suggestions**: a routing row "a safety rule" (`solarchat/safety/rules.json`, `solarchat/safety/rules.py`, `docs/CONTRACT.md` HAD-04, `test/test_safety.py`); let `todo.py` accept a `Waits on: none outside` kind so a chain item that merely follows another need not sit in Phase W; the engineer's review should read SR-03's words.

### 2026-11-21 · SR-03 words as a warning (J-036) · Claude Sonnet 5.5

- **Task**: change SR-03's `words_shown` to Ghost's text, add its change entry with the fingerprint, journal it, regenerate the safety document, land.
- **Opened**: `CLAUDE.md`, `solarchat/safety/rules.py`, `solarchat/safety/rules.json`, `docs/NAVIGATION-LOG.md`, `docs/journal/J-000-099.md`, `scripts/next_id.py`.
- **Complaints**: the worktree shell refuses a heredoc or any multi-step call, so the edit script went in through the file tool; no routing row for a safety rule yet (an earlier entry says so).
- **Suggestions**: none.

### 2026-11-21 · Phase 1 reordered for automated Q&A (SC-018, J-037) · Claude Sonnet 5.5

- **Task**: reorder Phase 1 on Ghost's word (the evaluation set, a new answering door and automatic runner, the index, search and the safety rules in the answers before the walker, demo mode and the shell), open Phase 2 with the moved items, renumber, record SC-018 and J-037, and land it as a documentation commit.
- **Opened**: `CLAUDE.md`, `docs/paths/process.md`, `TODO.md`, `scripts/checks/todo.py`, `docs/ROADMAP.md`, `docs/HANDOFF.md`, `theGhost.md` (SC-010, SC-015, SC-017), `docs/DONE.md`, `docs/journal/J-000-099.md`, `docs/CONTRACT.md`, `docs/SAFETY-AND-COMPLIANCE.md`, `README.md`, `packs/TYPES.md`.
- **Complaints**: TODO.md has no Phase 2, so moving items "to the start of Phase 2" meant opening one with its own tune-up pass and leaving 2.5 to 2.7 in the roadmap only; the plan row of `docs/paths/process.md` says how to add items before a pass but not how to move items between phases; item numbers are cited in about fifteen documents with no list of them, so the move was found by grep; the worktree shell refuses a call that names git beside another step, and also a command that merely mentions `.gitignore`.
- **Suggestions**: let `docs/paths/process.md`'s plan row say that a reorder renumbers every citation and name the grep ("1.5" to "1.9", "2.1" to "2.9" as item references); a check that every `TODO N.M` citation in a current document names an item that exists in TODO.md, DONE.md or the roadmap.

### 2026-11-21 · The seed pack in the pack format (TODO 1.4, J-038) · Claude Sonnet 5.5

- **Task**: convert `packs/seed-mc4-leads/` from `steps.json` and `failures.json` to passages, flows and a procedure, keeping every sentence, stop, picture, alt text and cited page; re-point `test/test_safety.py` at the new files with the same firings; add a test that the pack passes its check and covers the three subjects; close 1.4.
- **Opened**: `CLAUDE.md`, `TODO.md`, `docs/CONTRACT.md` ("The pack format"), `scripts/checks/packs.py`, `test/fixtures/packs/good/`, the seed pack's four files, `test/test_safety.py`, `test/test_packs.py`, `test/test_leaf.py`, `docs/DONE.md`, `docs/HANDOFF.md`.
- **Complaints**: the format holds one picture and no title per step, no citations on a flow's checks and no causes on a flow, so the conversion needed a rule for each (the journal says which); the old checks' pictures carried no alt text, which only the new format requires; a new file must be `git add -N`ed before the fast loop sees it, and a removed one `git rm`ed; the worktree shell refuses a heredoc or a one-line script that it reads as touching git, so the edits ran from scripts in the scratchpad.
- **Suggestions**: let a flow's check carry its own `sources` (and a flow its `likely_causes`) if real packs need them, which would end the per-check passages; a test that every `image` a pack names has alt text in the pack's own data; a routing row for "a pack: convert or add one" starting at `docs/CONTRACT.md`, `scripts/checks/packs.py` and `test/test_packs.py`.

### 2026-11-21 · The evaluation set, version 1 (TODO 1.5, J-039) · Claude Sonnet 5.5

- **Task**: build the frozen evaluation set for the seed pack (`evals/v1.json`, its hash, the check `scripts/checks/evals.py` with tests), against the leaf's reply kinds and the safety rules, move 1.5 to DONE, and land it.
- **Opened**: `TODO.md`, `docs/CONTRACT.md` (HAD-03, HAD-04), `theGhost.md` (SC-015, SC-018), `solarchat/leaf/contract.py`, `solarchat/safety/rules.json`, `solarchat/safety/rules.py`, the seed pack's `passages.json`, `flows.json` and `procedures.json`, `scripts/checks/packs.py`, `test/test_packs.py`, `docs/ROADMAP.md`, `docs/DONE.md`, `docs/HANDOFF.md`, `docs/JOURNAL.md`.
- **Complaints**: no routing row for "the evaluation set" or "a check on a data file"; the roadmap, TODO and decisions name no place for the set or its hash, so the brief's `evals/v1.json` was the only guide; the worktree shell refuses a call that mixes git with other steps, and some heredocs, so files went in through the file tool and a script; the readability check's limits were found only by running the whole fast loop.
- **Suggestions**: a routing row "an evaluation case or a check on a data file" starting at `evals/`, `scripts/checks/evals.py` and `test/test_evals.py`; say in `docs/paths/process.md` where a frozen file's hash lives (here `evals/v1.sha256`); a rule's triggers should be listed beside its words in `docs/SAFETY-RULES.md` so a case writer need not open `rules.json`.

### 2026-11-21 · The design of the answering door and the runner (TODO 1.6, SC-019, J-040) · Claude Opus 5.5

- **Task**: write the strong-grade design of TODO 1.6 (the door's signature and module, the answerer interface, the runner's scoring, exit codes, record and model mode, the day-one stub, the feed to the review packet) and land it as a design document and a proposed decision, with no code.
- **Opened**: `docs/paths/process.md`, `TODO.md`, `docs/ROADMAP.md`, `theGhost.md` (SC-002, SC-003, SC-010, SC-012, SC-015, SC-016, SC-018, C-023, C-033), `docs/CONTRACT.md`, `solarchat/leaf/contract.py`, `solarchat/safety/rules.py`, `solarchat/safety/rules.json`, `docs/modules.json`, `test/test_modules.py`, the seed pack's files, `scripts/checks/packs.py`, `scripts/commit.sh`, `scripts/ship.sh`, `scripts/fast.sh`, `docs/JOURNAL.md`, `docs/journal/J-000-099.md`, `docs/HANDOFF.md`, `docs/NAVIGATION-LOG.md`, `docs/GLOSSARY.md`, `scripts/checks/ghost.py`, `scripts/checks/pointers.py`.
- **Complaints**: the project had no home for a design document, so one was proposed (`docs/designs/`); the brief said to check out `main` in the worktree, but `main` is checked out by another worktree, so the work stayed on the worktree's branch reset to origin/main (`scripts/ship.sh` pushes HEAD, so this works); the modules map's `about` line names `answer` as the model-client module in passing, a design choice hidden in a description; the pack check, the only pack reader, lives in `scripts/`, which `solarchat/` may not import, so the door needs its own loader.
- **Suggestions**: a routing row for "a design before a build" naming `docs/designs/`, `theGhost.md` and `TODO.md`; move the model-client remark out of `docs/modules.json`'s `about` into a decision.

### 2026-11-21 · Two over-firing triggers removed (TODO 1.13 part, J-041) · Claude Sonnet 5.5
- **Task**: remove SR-10's trigger `add a panel in series` and SR-02's trigger `crimp` on Ghost's word, log each (SC-016), update the over-firing pin, and land it; nothing else changed.
- **Opened**: `docs/paths/process.md`, `solarchat/safety/rules.json`, `solarchat/safety/rules.py`, `test/test_evals.py`, `scripts/checks/evals.py`, `test/test_safety.py`, `TODO.md`, `docs/JOURNAL.md`, `docs/journal/J-000-099.md`, `docs/NAVIGATION-LOG.md`.
- **Complaints**: `load_rules` refuses a rule whose last entry has no matching fingerprint, so the fingerprint cannot be had from `load_rules` before the entry exists (it has to be taken from `rule_from_entry` on the raw JSON); the worktree shell refuses a git call that is joined to other commands, and some heredocs, so each had to be its own call; no routing row for "a safety rule's trigger".
- **Suggestions**: a routing row "a safety rule's trigger or words" naming `solarchat/safety/rules.json`, `solarchat/safety/rules.py`, `test/test_safety.py`, `test/test_evals.py` and `scripts/safety_rules_doc.py`; a small script that adds a change entry and sets its fingerprint; SR-10's `applies_when` still says "or a step adds panels in series", for Ghost to reword.
### 2026-11-21 · Ghost's answers to SC-019, and the meter sign-off (SC-019 in force, SC-020, J-042) · Claude Opus 5.5

- **Task**: record Ghost's answers to the ten questions of the answering-door design (documentation only), put SC-019 in force, add the `answer` and `model` modules to the map, move the safety rules matched on the worker's words into Phase 1 as 1.10, record the meter sign-off as SC-020, and mark HANDOFF 17 answered.
- **Opened**: `CLAUDE.md`, `docs/paths/process.md`, `docs/designs/answering-door.md`, `theGhost.md` (SC-018, SC-019), `docs/HANDOFF.md`, `TODO.md`, `docs/ROADMAP.md`, `docs/DONE.md`, `docs/modules.json`, `test/test_modules.py`, `scripts/checks/todo.py`, `docs/journal/J-000-099.md`, `docs/NAVIGATION-LOG.md`, `evals/v1.json` (the cases named), `scripts/ship.sh`.
- **Complaints**: the worktree shell refuses a command that joins git with other steps, so commands went one at a time; the numbers 1.11 to 1.14 are taken by done and waiting items, so a new item after 1.9 forces the tune-up pass to 1.15, a gap a reader will ask about; the instruction "update references in current documents only" has no list of which documents are current, so history (journal, DONE, this log) was left as written and the rest edited by search.
- **Suggestions**: `docs/paths/process.md` could say where a renumbering's old-to-new map goes (the journal entry, as SC-018's did) and that the waiting phase's numbers constrain a new item's; a check that a design's "awaiting Ghost" line is gone when its decision is in force.

### 2026-11-21 · SC-020 widened to a session profile (J-043) · Claude Opus 5.5

- **Task**: rewrite SC-020 from the meter sign-off to Ghost's session profile, carry it into TODO 1.10, the roadmap, HANDOFF and the design's note, as a documentation-only commit before TODO 1.6's code.
- **Opened**: `theGhost.md` (SC-020), `TODO.md` (1.10), `docs/ROADMAP.md`, `docs/HANDOFF.md`, `docs/designs/answering-door.md`, `docs/journal/J-000-099.md`, `docs/NAVIGATION-LOG.md`.
- **Complaints**: the direction arrived mid-task, after commit 1 had landed, so a landed decision is edited in place; no rule says whether a day-old decision is rewritten or superseded.
- **Suggestions**: `theGhost.md`'s header could say when to rewrite an in-force decision on the maintainer's word and when to supersede it.
### 2026-11-21 · SR-10's applies_when reworded (TODO 1.13 part, J-044) · Claude Opus 5.5
- **Task**: remove "or a step adds panels in series" from SR-10's `applies_when` on Ghost's word, log it (SC-016), regenerate the safety-rules document, and land it; nothing else changed.
- **Opened**: `CLAUDE.md`, `solarchat/safety/rules.json`, `solarchat/safety/rules.py`, `scripts/safety_rules_doc.py`, `docs/journal/J-000-099.md`, `docs/NAVIGATION-LOG.md`.
- **Complaints**: the worktree shell refuses git joined to other steps, so git ran one command per call; `applies_when` is outside the fingerprint, so SC-016's entry carries an unchanged fingerprint, which the task wording left to check.
- **Suggestions**: a small script that adds a change entry and sets its fingerprint; a routing row for "a safety rule's wording".

### 2026-11-21 · The Anthropic SDK as a dependency (SC-021, J-045) · Claude Sonnet 5.5

- **Task**: add `anthropic` as a runtime dependency on Ghost's word, compile the lock, review the new packages, install from the lock, smoke-check, and land it as one commit.
- **Opened**: `CLAUDE.md`, `docs/SUPPLY-CHAIN.md` ("The rules, verbatim"), `docs/when/dependency-update.md`, `docs/DEPENDENCY-REVIEW.md`, `requirements.in`, `requirements.lock`, `docs/REVIEWED-VERSIONS.md`, `stacks/python/README.md`, `docs/modules.json`, `scripts/review_scan.py`, `scripts/checks/dependency_review.py`, `scripts/next_id.py`, `theGhost.md` (SC-019, SC-020), `docs/journal/J-000-099.md`, `docs/when/handoff.md`.
- **Complaints**: `docs/DEPENDENCY-REVIEW.md` has no step for a new package's scan (the scan wants an old and a new archive; an empty wheel stood in for the old side); the record's table allows only SAFE, UNSAFE or UNSURE and CLEAN or CONCERN, so a layer that has not run has no honest cell; the worker had no tool to start the patch reviewer or the reputation checker; the worktree shell refuses a command that mixes git with other steps and heredocs that write scripts.
- **Suggestions**: say in `docs/DEPENDENCY-REVIEW.md` how to scan a new package (an empty wheel as the old side, or a `--new-only` flag on `scripts/review_scan.py`); let the record carry `NOT RUN` for a layer, refused by the fast loop only when the row is meant to be final; name in `docs/when/dependency-update.md` who runs the two agents when a worker cannot.
