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

### 2026-11-22 · TODO 1.10 slice 1, the session profile and three lowerings (J-077) · Claude Sonnet 5.5
- **Task**: build slice 1 of `docs/designs/session-profile.md`: the leaf's `Profile` and `lowered_for`, the loader, three lowerings, the door and the runner.
- **Opened**: `docs/designs/session-profile.md`, `solarchat/safety/rules.py`, `solarchat/answer/door.py`, `solarchat/leaf/contract.py`, `solarchat/safety/rules.json`, `scripts/eval.py`, `evals/known-failures.json`, `scripts/eval_core.py`, `scripts/eval_record.py`, `test/test_door.py`, `test/test_safety.py`, `test/test_eval.py`, `test/test_leaf.py`, `docs/modules.json`, `docs/JOURNAL.md`.
- **Complaints**: the brief named J-077, already taken on main; `scripts/next_id.py` gave J-077. The brief's "mns-09 now passes" cannot be told apart from "mns-09 always passed", since the stub never cites a passage and the door does not match the question yet.
- **Suggestions**: a brief that names a journal id should say "or the next free one". `scripts/checks` could say which tests pin `known-failures.json` entries (test/test_eval.py pins the set of cases).

### 2026-11-22 · TODO 1.10 slice 2, the two questions and the explanation (J-078) · Claude Sonnet 5.5
- **Task**: build slice 2 of `docs/designs/session-profile.md`: the questions, `--role` and `--signed-off`, the profile line to the answerer and the prompt's Depth paragraph, the lowered warn's first line.
- **Opened**: `docs/designs/session-profile.md`, `solarchat/project/chat.py`, `solarchat/cli/main.py`, `solarchat/model/claude.py`, `solarchat/answer/door.py`, `solarchat/leaf/contract.py`, `test/test_cli.py`, `test/test_speech.py`, `test/test_claude.py`, `test/test_safety_lowerings.py`.
- **Complaints**: the brief said to build the answerer with the profile in `choose_answerer`, but the questions come after a missing-key exit and the answerer is built first; and `docs/modules.json` (outside the working set) keeps chat.py from the door's `lowered_for_profile` and the model's word tables.
- **Suggestions**: a brief that touches the chat should say what the existing tests that script stdin through `main` must do (here: add `--role new --signed-off none`).

### 2026-11-22 · TODO 1.10, the worker's-words step, finished (J-079) · Claude Sonnet 5.5
- **Task**: finish `docs/designs/worker-words.md` after a restart cut the first worker off: save its tree, merge main (J-078 stays main's, this entry is J-079), build Ghost's decisions A ("broken" for SR-07) and B (`reads`, data), the pins, the bank-run test, the record, the docs.
- **Opened**: `CLAUDE.md`, `docs/designs/worker-words.md`, `docs/designs/session-profile.md`, the diff against 7d56f9b, `solarchat/answer/door.py`, `solarchat/safety/rules.py`, `solarchat/safety/rules.json`, `solarchat/leaf/contract.py`, `test/test_safety.py`, `test/test_door.py`, `test/test_door_words.py`, `test/test_bank_run.py`, `test/test_eval.py`.
- **Complaints**: the brief named three SR-07 pins, but the new triggers ("broken", "is cracked", "smells burnt") also move six other entries of the seed pack's text-level firings (fail-01, fail-08, fail-13) that no brief listed; `test_door.py` used SR-07 as its example of a passage-fired stop in five tests, which a words-only SR-07 ends, so SR-06 stands in for it. Stale text outside the working set: `scripts/bank_run.py` line 168 ("Until TODO 1.10 the door ...") and README line 67 ("known-failures.json names the cases that fail until 1.10").
- **Suggestions**: a brief that changes what a rule reads should list every test that plants that rule in a passage (`grep "trigger_of('SR-07')"`); `scripts/checks` could list the pins of the text-level firings.

### 2026-11-23 · Seed pack battery-wiring passages (J-080) · Claude Sonnet 5.5
- **Task**: add battery-wiring passages to the seed pack from Victron's installation chapter, version 0.3-draft, the SR-11 test, the offline record.
- **Opened**: `CLAUDE.md`, `packs/seed-mc4-leads/manifest.json`, `packs/seed-mc4-leads/passages.json`, `docs/CONTRACT.md` (pack format), `solarchat/safety/rules.json` (SR-11), `test/test_door_words.py`, `test/test_door.py`, `scripts/eval.py`, `docs/HANDOFF.md`, `docs/when/handoff.md`.
- **Complaints**: the brief's source id S9 was taken; four tests pin the seed pack's size and firings by number (test_door, test_pack_load, test_safety twice), which the brief's working set did not list at first; the manual's PDF is not linked from the HTML chapter (found on the product page).
- **Suggestions**: the brief should say "the next free source id"; a pack's size could be read from the pack in those tests instead of pinned. Living documents not changed: `docs/HANDOFF.md` (the unknown-page counts are unchanged), `README.md`, `docs/SAFETY-AND-COMPLIANCE.md`, `docs/ROADMAP.md`.

### 2026-11-23 · Add the citation cap to the system prompt (J-081) · Claude Sonnet 5.5

- **Task**: one sentence in `SYSTEM_PROMPT`'s Citing paragraph telling the model the three-passage cap, with a test.
- **Opened**: `solarchat/model/claude.py`, `test/test_claude.py`, `scripts/checks/bank.py`, `docs/when/handoff.md`, `docs/journal/J-000-099.md`, `docs/journal/INDEX.md`.
- **Complaints**: none.
- **Suggestions**: none.

### 2026-11-23 · TODO 2.11, Windows setup script (J-082) · Claude Sonnet 5.5
- **Task**: `setup.cmd`, `solarchat --has-key`, the launcher's fallback to setup, `.gitattributes`, tests, docs.
- **Opened**: `CLAUDE.md`, `docs/when/handoff.md`, `bin/solarchat.cmd`, `bin/solarchat`, `solarchat/project/keys.py`, `solarchat/cli/main.py`, `solarchat/model/key.py`, `test/test_key.py`, `test/support.py`, `README.md`, `docs/DEMO.md`, `TODO.md`, `docs/DONE.md`.
- **Complaints**: the brief said `git ls-files --eol` should show i/crlf; with `eol=crlf` it shows i/lf w/crlf (the index normalises), so the check wording is off. Living documents not changed: `docs/HANDOFF.md`, `docs/SAFETY-AND-COMPLIANCE.md`, `docs/ROADMAP.md`, `docs/CONTRACT.md`.
- **Suggestions**: none.

### 2026-11-23 · colorama into the lock for Windows (J-083, SC-025) · Claude Sonnet 5.5
- **Task**: regenerate `requirements.lock` universally, review colorama 0.4.6 by every layer of `docs/DEPENDENCY-REVIEW.md`, record it.
- **Opened**: `docs/when/dependency-update.md`, `docs/DEPENDENCY-REVIEW.md`, `docs/SUPPLY-CHAIN.md`, `docs/when/handoff.md`, `stacks/python/README.md`, `requirements.in`, `requirements.lock`, `scripts/review_scan.py`, `docs/REVIEWED-VERSIONS.md`, `theGhost.md`, `docs/journal/J-000-099.md`, `docs/NAVIGATION-LOG.md`.
- **Complaints**: the stack README's fetch command is for an update (an old and a new wheel); for a new package `review_scan.py --unpack` needs an old archive, so I unpacked each archive against an empty zip, and nothing says so. `pip download --no-binary :all:` for the sdist runs a build backend (it failed asking for hatchling); fetching the sdist URL from the JSON API by `curl` is the safe way, also unwritten. A worker has no Agent tool, so the two agent layers cannot run from a worker and this brief hit that wall (as J-045 did).
- **Suggestions**: add to `stacks/python/README.md`'s "Dependency updates" row the new-package case (an empty zip as the old side) and the sdist fetch by URL; put in `docs/when/hand-out-a-task.md` that a dependency brief's two agent layers belong to the coordinator.

### 2026-11-23 · Profile answers: typos and "all" (J-084, SC-020) · Claude Sonnet 5.5
- **Task**: read typos, run-together words and "all" in the role and sign-off answers; say how to correct the profile.
- **Opened**: `CLAUDE.md`, `docs/when/handoff.md`, `solarchat/project/chat.py`, `test/test_profile_chat.py`, `test/test_speech.py`, `docs/DEMO.md`, `docs/journal/J-000-099.md`.
- **Complaints**: `# Decision: SC-020` appears twice in chat.py, so a search for it finds the wrong one first. `test/test_speech.py` also compares the spoken lines and was not named in the brief.
- **Suggestions**: none.

### 2026-11-23 · TODO 2.12, the profile changes mid-conversation (J-085, SC-026) · Claude Sonnet 5.5
- **Task**: build `docs/designs/profile-takeover.md` section 7 items 1, 2 and 4: the schema field, prompt paragraph, `ProfileChange`, `converse`'s steps, tests, SC-026, DEMO scenario 5.
- **Opened**: `CLAUDE.md`, `docs/designs/profile-takeover.md`, `solarchat/model/claude.py`, `solarchat/project/chat.py`, `solarchat/answer/door.py`, `solarchat/leaf/contract.py`, `test/test_profile_chat.py`, `test/test_claude.py`, `test/test_cli.py`, `theGhost.md`, `docs/DONE.md`, `docs/DEMO.md`, `docs/when/handoff.md`, `docs/journal/J-000-099.md`.
- **Complaints**: the brief names TODO 2.12 but `TODO.md` has no such item, so I wrote it straight to `docs/DONE.md` as told. The design says `parse_reply` validates the proposal; `parse_reply` returns the dict and checks only the reply's shape, so I put the check in `proposal_from`. Living documents not changed: `README.md`, `docs/HANDOFF.md`, `docs/SAFETY-AND-COMPLIANCE.md`, `docs/ROADMAP.md`, `docs/CONTRACT.md`.
- **Suggestions**: none.
