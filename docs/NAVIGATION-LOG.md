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

### 2026-11-21 · TODO 1.19, the rule bank's format and check (J-053) · Claude Sonnet 5.5

- **Task**: build design section 3: `evals/bank/` with about twenty hand-written rules, `scripts/checks/bank.py` and `test/test_bank.py` with planted breaks, and the coordinator's reading of "quoting" in 3.2; no model.
- **Opened**: `CLAUDE.md`, `docs/designs/rule-bank-and-triage.md`, `scripts/checks/evals.py`, `scripts/checks/common.py`, `test/test_evals.py`, `test/support.py`, `solarchat/model/claude.py`, `packs/seed-mc4-leads/passages.json`, `solarchat/safety/rules.json`, `evals/v1.json`, `docs/DONE.md`, `TODO.md`, `docs/journal/J-000-099.md`.
- **Complaints**: the worktree shell refused any command whose text held the word "eval" (the path `test/fixtures/broken/eval` among them) and any heredoc or long command with git beside it, so files went through the Write tool; the design does not say whether ids rise across files, what a hand-seeded rule's `drafted.batch` is, or how a `triage` source resolves before 1.23.
- **Suggestions**: 3.2 could name the `batch` of a hand-seeded rule and say that ids are global and ascending per file; `docs/paths/process.md` could get a row for the bank (`evals/bank/`, `scripts/checks/bank.py`, `test/test_bank.py`).

### 2026-11-21 · Tune-up commit 1 (J-052) · Claude Sonnet 5.5

- **Task**: the tune-up commit due after 30 commits (SC-009): steps 1, 4, 5 and 6 of `docs/when/tune-up.md`, changing no result.
- **Opened**: `docs/when/tune-up.md`, `docs/NAVIGATION-LOG.md`, `docs/when/handoff.md`, `docs/paths/process.md`, `docs/when/coordinate.md`, `docs/HANDOFF.md`, `scripts/checks/claude_md.py`, `scripts/next_id.py`, `docs/journal/J-000-099.md`.
- **Complaints**: the brief said to symlink the main checkout's `.venv`, while `docs/when/coordinate.md` says a worker never symlinks `.venv` itself (the gate would record it); the document was followed. The worktree shell refuses git joined to other steps. The brief's journal id (J-052) and the id `scripts/next_id.py` gives (J-051) differ by design, which is the collision the debriefs named.
- **Suggestions**: the brief's template could say "a real `.venv/` directory of symlinks", as `docs/when/coordinate.md` does.

### 2026-11-21 · SC-023 recorded in force on Ghost's word (J-051) · Claude Opus 5.5

- **Task**: record Ghost's answer to SC-023, close 1.17, move 1.19 to 1.24 into Phase 1, and land docs only.
- **Opened**: `docs/when/coordinate.md`, `docs/when/grades.md`, `theGhost.md` (SC-019, SC-023), `docs/HANDOFF.md`, `TODO.md`, `docs/DONE.md`, `scripts/checks/todo.py`, `test/test_todo.py`, `docs/when/tune-up.md`, `docs/designs/rule-bank-and-triage.md`, `docs/ROADMAP.md`, `docs/journal/J-000-099.md`.
- **Complaints**: how to close an item absorbed rather than done is not written anywhere (it went to `docs/DONE.md` with "Closed, not built"); the order rule that forces a phase's tune-up pass to be renumbered whenever items are added is only in `scripts/checks/todo.py`; `scripts/eval.py --live` writes its recordings under `evals/recorded/`, inside the tree, so every live run trips the stop hook.
- **Suggestions**: a line in `docs/paths/process.md` for closing an absorbed item; send live recordings to `build/` (1.20 is the natural place).

### 2026-11-21 · The demo's key and voice, recorded (SC-022 amended, J-054) · Claude Opus 5.5

- **Task**: record Ghost's demo ask and answers, amend SC-022, and write TODO 2.5 and 2.7.
- **Opened**: `theGhost.md` (SC-022), `docs/ROADMAP.md` (F-08, F-09, 5.4), `solarchat/cli/main.py`, `solarchat/cli/__main__.py`, `pyproject.toml`, `requirements.lock`, `TODO.md`, `docs/DONE.md`.
- **Complaints**: none new; the decision that the project is not an installed package is stated only in `pyproject.toml`'s first comment.
- **Suggestions**: none.

### 2026-11-21 · The command menu and the local key (J-055) · Claude Sonnet 5.5

- **Task**: TODO 2.5: a `solarchat` command with a help menu and a local key store for the Windows demo, the key never printed and never in the repository.
- **Opened**: `CLAUDE.md`, `solarchat/cli/main.py`, `solarchat/cli/__main__.py`, `solarchat/project/chat.py`, `solarchat/model/claude.py`, `docs/modules.json`, `test/test_cli.py`, `scripts/checks/secrets.py`, `theGhost.md` (SC-022), `TODO.md`, `docs/journal/J-000-099.md`.
- **Complaints**: the Check and the brief named a root file `solarchat` that the package folder of the same name makes impossible; the item's contract was not tried against the file tree when it was written. `python3 -I -m unittest test.x` cannot import `test` (use no `-I`).
- **Suggestions**: a check that a launcher name in a TODO Check does not clash with a path in the tree; `test/test_eval.py` line 154 also expects no key and should use `no_key()` (outside this brief's files).

### 2026-11-21 · TODO 2.7, speech out (J-056) · Claude Sonnet 5.5

- **Task**: TODO 2.7: `--voice` speaks each reply through the system's own voice for the Windows demo, no new dependency.
- **Opened**: `CLAUDE.md`, `docs/when/grades.md`, `TODO.md`, `solarchat/cli/main.py`, `solarchat/project/chat.py`, `docs/modules.json`, `test/support.py`, `test/test_cli.py`, `scripts/score.py`, `docs/CONTRACT.md`, `README.md`, `docs/journal/J-000-099.md`, `docs/NAVIGATION-LOG.md`.
- **Complaints**: `scripts/score.py` cannot place an item that names no file, and the placing has to be simulated by hand (I called its functions with the files added to a copy of the text); a one-line way to ask "what would this item score if it named these files" would help.
- **Suggestions**: that; and `docs/modules.json` has nothing to change for a new file in a module with no entry points, which the brief listed as in the working set.

### 2026-11-21 · Documentation currency pass (J-057) · Claude Sonnet 5.5

- **Task**: bring every living document to what `main` at 48a248a holds, changing no decision, result, rule or plan; the README's Windows section left to another branch.
- **Opened**: `CLAUDE.md`, `docs/when/handoff.md`, `docs/when/hand-out-a-task.md`, `docs/DONE.md`, `TODO.md`, `docs/modules.json`, `docs/journal/J-000-099.md` (J-045 to J-055), `README.md`, `docs/ROADMAP.md`, `docs/HANDOFF.md`, `docs/SAFETY-AND-COMPLIANCE.md`, `docs/GLOSSARY.md`, `docs/paths/process.md`, `docs/CONTRACT.md`, `docs/REVIEWED-VERSIONS.md`, `docs/DEPENDENCY-REVIEW.md`, `docs/FINDINGS.md`, `docs/ESCALATIONS.md`, `solarchat/answer/door.py`, `solarchat/cli/main.py`, `theGhost.md` (SC-022, SC-023).
- **Complaints**: no document says which documents carry "what is built" (the README, HANDOFF, the safety document, the roadmap's status words and CONTRACT's pointers all do), so each feature item leaves some of them stale; the journal's classes have no `docs`, so the brief's class was refused; `scripts/next_id.py` gave J-057 while the brief named J-057 for a reserved J-057.
- **Suggestions**: a line in `docs/when/handoff.md`'s "Finishing a task" naming the five documents a built item must update (the debriefs of J-053 and J-055 each asked for one row or note after the fact); a `docs` journal class, or a sentence saying which class a currency pass takes.

### 2026-11-21 · The tune-up's four answers and the number clash (J-058) · Claude Opus 5.5

- **Task**: record Ghost's four answers, fix the roadmap numbers the demo items reused, land docs only.
- **Opened**: `docs/HANDOFF.md`, `scripts/next_id.py`, `docs/when/coordinate.md`, `docs/ROADMAP.md`, `TODO.md`, `theGhost.md` (header).
- **Complaints**: free numbers live in three files (`TODO.md`, `docs/DONE.md`, `docs/ROADMAP.md`) and nothing checks all three; the fast checks run no `ruff`, so lint reached `main`.
- **Suggestions**: a check that a TODO number is not used for a different roadmap item; `ruff` in the fast checks (Ghost's, For Ghost 21).

### 2026-11-21 · Tooling follow-ups: the lint and `worker_venv.py` (J-059, J-060) · Claude Sonnet 5.5

- **Task**: fix `ruff check .` on main (J-059) and build `scripts/worker_venv.py` with its test and the coordinate.md change (J-060).
- **Opened**: `CLAUDE.md`, `docs/when/grades.md`, `scripts/checks/bank.py`, `scripts/eval.py`, `solarchat/model/claude.py`, `test/support.py`, `test/test_cli.py`, `test/test_packs.py`, `test/test_speech.py`, `solarchat/project/speech.py`, `scripts/next_id.py`, `scripts/checks/readability.py`, `docs/when/coordinate.md`, `docs/paths/process.md`, `docs/journal/J-000-099.md`, `docs/NAVIGATION-LOG.md`.
- **Complaints**: the brief's pass line for the lint cannot be met without a choice for nine `Any` annotations in `claude.py`; the repository does not say whether `Any` is meant to stay there. The readability check wants a docstring on test helper methods too, which `test_speech.py` does not need for its test methods.
- **Suggestions**: decide the types for `claude.py` (a `Protocol` for the client and `ModuleType` for `errors` is the obvious candidate); add `ruff check .` to the fast loop, so a lint failure is found when it is made, not at the gate.

### 2026-11-21 · Fix-forward, `Any` in `claude.py` (J-061) · Claude Sonnet 5.5

- **Task**: replace the nine `typing.Any` in `solarchat/model/claude.py` with the coordinator's Protocols so `ruff check .` passes, changing no behaviour.
- **Opened**: `CLAUDE.md`, `solarchat/model/claude.py`, `docs/when/handoff.md`, `scripts/checks/readability.py`, `docs/when/hand-out-a-task.md`, `docs/NAVIGATION-LOG.md`, `docs/journal/INDEX.md`, `docs/journal/J-000-099.md`, `docs/JOURNAL.md`.
- **Complaints**: none; the fast loop's metrics test fails after any source-line change until `scripts/metrics.py --write` runs, which the brief had to name.
- **Suggestions**: `docs/when/handoff.md` could list `python3 -I scripts/metrics.py --write` and `scripts/directive_map.py` among the finishing steps when source lines or `# Decision:` citations change.

### 2026-11-22 · Ruff in the fast checks, Ghost's answer recorded (J-062) · Claude Opus 5.5

- **Task**: record For Ghost 21's answer and move `ruff` into the Python stack's fast checks.
- **Opened**: `stacks/python/gate.sh`, `scripts/gate.sh`, `docs/HANDOFF.md`, `stacks/python/README.md`.
- **Complaints**: none.
- **Suggestions**: none.

### 2026-11-22 · The safety rules in the answers (J-063) · Claude Sonnet 5.5

- **Task**: place TODO 1.9 and build step 6 of the door on the cited passages' text.
- **Opened**: `CLAUDE.md`, `docs/when/grades.md`, `scripts/score.py`, `scripts/checks/score.py`, `solarchat/answer/door.py`, `docs/designs/answering-door.md`, `solarchat/safety/rules.py`, `solarchat/leaf/contract.py`, `scripts/eval.py`, `evals/known-failures.json`, `test/test_door.py`, `test/test_eval.py`, `docs/SAFETY-AND-COMPLIANCE.md`.
- **Complaints**: an unplaced item's score depends on which files the placer names (6 points with the files edited, 9 with `scripts/fast.sh` named, which adds a layer), so placement is a judgement; the brief's working set lists files that are read, which `score.py` would count.
- **Suggestions**: `scripts/score.py` could say which named files are only run or read; the TODO item could name its files, so no worker places it.

### 2026-11-22 · TODO 1.20, the bank run's deterministic half (J-064) · Claude Sonnet 5.5

- **Task**: build design 4.1, 4.4 and 5 with no model: the sample, the ledger line, the door-fault cross-check, `scripts/bank_trend.py` with `--check` in the fast loop, and the `--live --write` refusal.
- **Opened**: `CLAUDE.md`, `docs/designs/rule-bank-and-triage.md`, `TODO.md`, `docs/when/handoff.md`, `docs/when/hand-out-a-task.md`, `solarchat/answer/door.py`, `solarchat/answer/stub.py`, `solarchat/safety/rules.py`, `scripts/eval.py`, `scripts/fast.sh`, `scripts/checks/bank.py`, `test/test_bank.py`, `scripts/safety_rules_doc.py`, `test/test_eval.py`, `solarchat/leaf/contract.py` (for `Reply`'s field name), `docs/JOURNAL.md`.
- **Complaints**: 5.1 names its fields without their shapes (`canaries`, `by_family`, `tokens`, `packs`, `run`), and 5.3's check-model clause needs a per-rule check verdict that 5.1 does not record; 4.1 does not say whether "safety rules" are the severity or the family, how a quarter rounds, or whether an `unclear` counts as a sampling; the page's "month so far" needs a clock the design does not give a page that `--check` must reproduce.
- **Suggestions**: add the shapes to 5.1 in one example line; add the per-rule check verdict to 5.1's `results`; name the readability rules (a docstring on nested test helpers, no `**kwargs`) in the "Before calling work done" section or the process row.

### 2026-11-22 · The module map confirmed, 1.20's readings settled (J-065) · Claude Opus 5.5

- **Task**: record Ghost's confirmation; write the 1.20 worker's six readings into the design.
- **Opened**: `docs/designs/rule-bank-and-triage.md` (4.1, 5), `TODO.md` (1.21), `docs/HANDOFF.md`, `docs/modules.json`.
- **Complaints**: a question asked only in chat (the module map) left no trace in the repository for two days.
- **Suggestions**: a coordinator writes every question it puts to Ghost into `docs/HANDOFF.md` when it asks, not when it is answered.

### 2026-11-22 · Sourcing for SR-08's sentence, S6, S7, S3 (J-066) · Claude Sonnet 5.5

- **Task**: find which page of S6 or S7 (then S3) states do-not-touch, stop-the-current and caveat claims for a hot or arcing connector; add S6 to the library only if its licence allows.
- **Opened**: `CLAUDE.md` (given), `library/README.md`, `library/sources/osha-solar-lockout-tagout/source.json`, `docs/when/handoff.md`, `docs/when/hand-out-a-task.md`, `solarchat/safety/rules.json` (SR-08 only), `packs/seed-mc4-leads/manifest.json`, `docs/journal/INDEX.md`, `docs/journal/J-000-099.md` (tail), `docs/JOURNAL.md`, `docs/HANDOFF.md`.
- **Complaints**: none; the brief named everything.
- **Suggestions**: `library/README.md` could say what to do with a document whose own notice limits distribution but whose host page may carry another licence (S6 is this case).

### 2026-11-22 · A pack as the first safety authority, SC-024 proposed (J-067) · Claude Opus 5.5

- **Task**: record Ghost's precedence direction as a decision with safeguards.
- **Opened**: `docs/CONTRACT.md` (HAD-04), `theGhost.md` (SC-020, SC-023, the entry shape), `packs/seed-mc4-leads/manifest.json`.
- **Complaints**: project decisions carry no Core line though the header's template shows one; the entry shape is learned from neighbours.
- **Suggestions**: the header's template could show the project entry's shape (no Core line, a `subject:` line).

### 2026-11-22 · Seed pack: fail-08 and fail-04 corrected (J-068) · Claude Sonnet 5.5

- **Task**: remove fail-08-check-2's last sentence, fill the S3 pages for fail-08 and fail-04, update the unknown-page counts, check the eval is unchanged.
- **Opened**: `CLAUDE.md`, `packs/seed-mc4-leads/manifest.json`, `flows.json`, `passages.json`, `docs/CONTRACT.md` (pack format), `scripts/checks/packs.py`, `scripts/eval.py` (help), `docs/HANDOFF.md`, `docs/journal/J-000-099.md`, `docs/NAVIGATION-LOG.md`, `docs/when/handoff.md`.
- **Complaints**: none; the brief named everything. The pack has no change log, so a pack change has no home but the journal.
- **Suggestions**: CONTRACT.md could say what a `version` bump looks like for a demo pack (its string is tied to `evals/results/offline.json`).
