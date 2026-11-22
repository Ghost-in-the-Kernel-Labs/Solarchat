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

### 2026-11-22 · TODO 1.10, the worker's-words step (J-079) · Claude Sonnet 5.5
- **Task**: build `docs/designs/worker-words.md` section 5: the door's words step, emergencies on the worker's words only, the warn fallback, three trigger changes, the evaluation.
- **Opened**: `CLAUDE.md`, `docs/designs/worker-words.md`, `solarchat/answer/door.py`, `solarchat/safety/rules.py`, `solarchat/safety/rules.json`, `test/test_door.py`, `scripts/eval.py`, `test/test_eval.py`, `test/test_eval_live.py`, `test/fixtures/evals/known-failures.json`.
- **Complaints**: the design's trigger table was checked against questions but not against the seed pack's passages: SR-07's new triggers fire on `step-02`. The tiny fixture's known-failures file and several eval tests assumed the stub stops nothing; no document said which tests pin that, so each was found by running them (a script listing them would help).
- **Suggestions**: a design that adds triggers should run them over the pack's passages as well as the frozen questions; `scripts/checks` could list the tests that pin the stub's scores.
