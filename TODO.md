# TODO: the open items, in order

The roadmap as a chain: items are done in this order, never out of it, and an item that cannot be
done as written stops the chain and goes to Ghost (C-016). Each item's plan is its step in
`docs/ROADMAP.md` §6, by the same number; its check is copied here. A done item moves to
`docs/DONE.md` with its number kept. `test/test_todo.py` holds this file: headings in numeric order
under their phase, the first open item has a check, every phase ends with a tune-up pass (a reopened phase
of at most three new items with a tune-up commit, `docs/when/tune-up.md`), and
nothing is both here and done or done twice. An item that waits on something outside the repository (Ghost's choice
or approval, counsel, another project) carries a `Waits on:` line naming it in words, or one of the two kinds with a
shape for what a session lacks, `Waits on: environment (<host or tool>)` or `Waits on: reference (<what>)`
(`scripts/checks/todo.py`), and moves to the last phase, headed `## Phase W: waiting on Ghost`, keeping its number and adding a `Moved: from Phase N` line; a phase
whose every item waits takes its tune-up pass with it (the pass's `Waits on:` names those items), and the waiting
phase needs no pass of its own. When what it waits on arrives, Ghost moves the item back into the chain. An open
question a later item depends on is copied into that item's text, so the item reads whole where it stands.

## Phase 0: founding

## Phase 1: the pack and the oracle

### 1.4 The seed pack

Check: one pack in the repository passes 1.2's check; its manifest names a source whose licence allows redistribution, and the licence text or its link is recorded; it covers connecting a panel, polarity, and a panel that shows no output.

### 1.5 The evaluation set, version 1

Check: at least thirty in-scope questions each naming the passage that answers it; fifteen out-of-scope questions marked refuse; questions in the pack's field that its passages do not cover, marked "I do not know"; ten safety cases marked stop or emergency; warn cases marked warn (the rule's words shown, then the walk continues); must-not-stop cases (step-12's safe method, fail-04's polarity fix, plugging connectors in, a meter where the worker is trained); a check holds the file's shape and that every named passage exists; the set's hash is recorded and a later change without a decision is refused. It needs only SC-015's code (the rules' responses and the leaf's warn, 1.11 and 1.12), SC-015 being in force; the engineer reviews the frozen set at the end (6.4).

### 1.6 The answering door and the automatic evaluation runner

Check: one function, `answer(question, packs, demo_mode) -> Reply` (the leaf's `Reply`), is the door through which every mode answers: offline search now, the model later; `scripts/eval.py` feeds every question of the evaluation set (1.5) to it and scores each reply against its expected outcome: the right reply kind; the named passage cited for an in-scope question; "I do not know" where expected; stop, warn or emergency where expected; no stop on a must-not-stop case; it prints a score table and exits non-zero if any safety case or must-not-stop case fails; it runs in the fast loop against the offline mode; the model mode runs on recorded replies in tests, and live only by a separate command; the interface's design is written by a strong-grade agent before it is built (SC-018).

### 1.7 The index

Check: a pack on disk becomes an index, the same bytes every time (goldens, SC-003); a test builds it twice and holds the bytes equal to a golden file.

### 1.8 Keyword search behind `answer()`

Check: `answer()`'s offline mode ranks a pack's passages by keyword, in the standard library, and the runner (1.6) scores it on the evaluation set (1.5): the right passage cited for each in-scope question, "I do not know" with no passage where the passages do not cover the question, the out-of-scope questions refused (HAD-03); the scores of the run are recorded with it (HAD-02).

### 1.9 The safety rules in the answers

Check: a reply on a passage whose text fires a safety rule (`rules_fired`, HAD-04) carries that rule's response (warn, stop or emergency, SC-015) and its words; the runner (1.6) scores the evaluation set's safety, warn and must-not-stop cases and exits non-zero if one fails; a test plants a passage that fires a rule of each response. The walker's half of this (2.3) is built after it.

### 1.10 Tune-up pass 1

Check: `docs/when/tune-up.md` followed in full; the metrics table written; the navigation log reviewed; the human maintainability pass for the code written since the last one (SC-011).

## Phase 2: the offline mode (the floor)

### 2.1 Demo mode

Check: a demo switch lets a `demo` pack run, and every screen shown under it carries the banner "DEMO: not reviewed by an engineer, do not use on a site"; without the switch such a pack is refused (HAD-06, SC-010); a test holds both.

### 2.2 The walker

Check: `solarchat/walker` steps through a pack's procedure (its steps in order, each step's stop shown) and a flow (its checks in order, ending at its fix or its stop), one step at a time, on the good fixture pack and the seed pack; tests hold both and that a walk always ends. The walker decides whether a pack may answer only through the leaf's `may_answer`, and refuses a pack it says no to.

### 2.3 The safety rules in the walker

Check: every walk stops at a safety rule of 1.3 that applies, whatever the pack says, with the rule's words shown; a test plants a pack step that would walk past one.

The walker finds the rules that apply to a step's text with `rules_fired(text)` in `solarchat/safety/rules.py` (whole-word, case-insensitive matching, defined under HAD-04 in `docs/CONTRACT.md`); it does not match triggers itself. Every rule stops here; a rule's response (warn, stop, emergency) is 1.12's, under SC-015 (in force).

### 2.4 The offline shell

Check: `solarchat/cli` runs a conversation end to end with the network off: choose a pack, a procedure or a flow, walk it step by step, and see the demo banner when the pack is a `demo` pack; every step shown lists its passage's sources by title, with the page for a document source or "page not yet found" where the page is `"unknown"` (SC-012); free text the shell cannot place gets "I do not know", with no passage (HAD-03); a test drives it through stdin.

### 2.8 Tune-up pass 2

Check: `docs/when/tune-up.md` followed in full; the metrics table written; the navigation log reviewed; the human maintainability pass for the code written since the last one (SC-011).

Items 2.5 to 2.7 of `docs/ROADMAP.md` join this chain, before this pass, when Phase 2 is reached.

## Phase W: waiting on Ghost

### 0.5 The founding decisions

Check: `theGhost.md` holds Ghost's founding decisions for Solarchat, a decision for each core decision it refuses among them, each with Ghost as its Source. Agents cannot author Ghost's decisions: an agent drafts the questions for Ghost in `docs/HANDOFF.md`, and a builder that reports "waiting on Ghost" has done its job.

Moved: from Phase 0
Waits on: Ghost's founding decisions (the questions in `docs/HANDOFF.md`, "For Ghost": the app's stack, the first real pack's make and model, naming the deploying company, SC-007 in `CLAUDE.md`, the trademark search)

### 1.12 Response types: the walker's use

Check: the walker shows a warn (the rule's words, then the walk continues with its passage), a helpful stop (why, the safe next action, what to bring the supervisor) or an emergency, each by the rule's `response`, and a test plants a rule of each response. The rules' `response` field and the leaf's `ReplyKind.WARN` and `SafetyRule.response` are done (J-034, SC-015); the response words (the safe next action, what to bring) are written with the walker.

Moved: from Phase 1
Waits on: the walker (2.2 and 2.3, in Phase 2); nothing waits on an engineer

### 1.13 The over-firing of SR-03 and SR-02

Check: on the demo pack, SR-03 no longer fires on step-12's prohibition or on the safe method it prescribes (fail-04, fail-07, fail-10), and SR-08 no longer fires on fail-04's list of signs to watch for, each change logged (1.11) with "engineer to confirm"; SR-02's meter, probe, test-lead and crimp triggers are kept for the engineer's final review (6.4), not changed here; `test/test_safety.py`'s pin of what the demo pack fires updated; a planted step that does part connectors under load still fires SR-03.

Moved: from Phase 1
Waits on: Ghost's go-ahead to run it; SC-016 is in force, and Ghost may confirm a precision fix on his word, logged as maintainer (SC-015); nothing waits on an engineer

### 1.14 The engineer's review packet

Check: `scripts/engineer_review_doc.py` writes `docs/ENGINEER-REVIEW.md` from the data, and `--check` in the fast loop fails when it is stale; it lists every "engineer to confirm" mark, every SC-016 change entry whose role is not an electrical engineer marked "pending engineer", every pack page still `"unknown"`, every claim flagged as unsourced (HANDOFF For Ghost 3's list), and each rule's response; a planted break shows the check refusing a stale packet (P-20, F-16).

Moved: from Phase 1
Waits on: Ghost's go-ahead to run it; it needs 1.11's change log and 1.12's responses; nothing waits on an engineer

### 6.4 The engineer's final review

Check: an electrical engineer has read `docs/ENGINEER-REVIEW.md` (1.14) and the frozen evaluation set (1.5) and judged every item in them: SR-01 to SR-14 (words, triggers, responses, and each claim against its source's page in `library/sources/` where the library holds it), SC-015's queue (SR-03's warn, SR-02's meter and crimp triggers, SR-05, SR-11's split), the four open marks (SR-02, SR-06, SR-08 and SR-09's first-aid sentence, SR-12), the demo pack's five flagged claims (fail-04, step-07, step-09, fail-03, fail-08) with its mirrored sources S3 and S8, and 3.4's thresholds; each judgement confirms or reverses a change-log entry (SC-016) with the role "electrical engineer".

Moved: from Phase 6
Waits on: an engineer (unknown; comes in only at the end of the project, F-16)
