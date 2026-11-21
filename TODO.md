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

### 1.5 Demo mode

Check: a demo switch lets a `demo` pack run, and every screen shown under it carries the banner "DEMO: not reviewed by an engineer, do not use on a site"; without the switch such a pack is refused (HAD-06, SC-010); a test holds both.

### 1.6 The walker

Check: `solarchat/walker` steps through a pack's procedure (its steps in order, each step's stop shown) and a flow (its checks in order, ending at its fix or its stop), one step at a time, on the good fixture pack and the seed pack; tests hold both and that a walk always ends. The walker decides whether a pack may answer only through the leaf's `may_answer`, and refuses a pack it says no to.

### 1.7 The safety rules in the walker

Check: every walk stops at a safety rule of 1.3 that applies, whatever the pack says, with the rule's words shown; a test plants a pack step that would walk past one.

The walker finds the rules that apply to a step's text with `rules_fired(text)` in `solarchat/safety/rules.py` (whole-word, case-insensitive matching, defined under HAD-04 in `docs/CONTRACT.md`); it does not match triggers itself. Every rule stops here; a rule's response (warn, stop, emergency) is 1.12's, under SC-015 (in force).

### 1.8 The offline shell

Check: `solarchat/cli` runs a conversation end to end with the network off: choose a pack, a procedure or a flow, walk it step by step, and see the demo banner when the pack is a `demo` pack; every step shown lists its passage's sources by title, with the page for a document source or "page not yet found" where the page is `"unknown"` (SC-012); free text the shell cannot place gets "I do not know", with no passage (HAD-03); a test drives it through stdin.

### 1.10 Tune-up pass 1

Check: `docs/when/tune-up.md` followed in full; the metrics table written; the navigation log reviewed; the human maintainability pass for the code written since the last one (SC-011).

## Phase W: waiting on Ghost

### 0.5 The founding decisions

Check: `theGhost.md` holds Ghost's founding decisions for Solarchat, a decision for each core decision it refuses among them, each with Ghost as its Source. Agents cannot author Ghost's decisions: an agent drafts the questions for Ghost in `docs/HANDOFF.md`, and a builder that reports "waiting on Ghost" has done its job.

Moved: from Phase 0
Waits on: Ghost's founding decisions (the questions in `docs/HANDOFF.md`, "For Ghost": the app's stack, the first real pack's make and model, naming the deploying company, SC-007 in `CLAUDE.md`, the trademark search)

### 1.9 The evaluation set, version 1

Check: at least thirty in-scope questions each naming the passage that answers it; fifteen out-of-scope questions marked refuse; questions in the pack's field that its passages do not cover, marked "I do not know"; ten safety cases marked stop or emergency; warn cases marked warn (the rule's words shown, then the walk continues); must-not-stop cases (step-12's safe method, fail-04's polarity fix, plugging connectors in, a meter where the worker is trained); a check holds the file's shape and that every named passage exists; the engineer has reviewed the safety, warn and must-not-stop cases (1.14); the set's hash is recorded and a later change without a decision is refused. When Ghost moves it back it runs after 1.14 and takes the number after it (`docs/ROADMAP.md` §6, Phase 1).

Moved: from Phase 1
Waits on: the engineer's review (1.14); SC-015, the response classes the set is written in, is in force

### 1.11 The safety rules' change log

Check: every rule in `solarchat/safety/rules.json` has `changes`, oldest first, each entry `{date, by, role, why, evidence}` with every field filled, backfilled for version 1 (J-027) and the audit's changes (J-030, `docs/audits/2026-11-21-safety-rules.md`); the safety check refuses a rule changed with no new entry, shown by a planted break; `ghost_to_confirm` renamed `engineer_to_confirm` (F-16); `docs/SAFETY-RULES.md` shows each rule's last entry. Runs first of 1.11 to 1.14, so every later change to a rule is logged.

Moved: from Phase 1
Waits on: Ghost's go-ahead to run it; SC-016 is in force (Ghost, 2026-11-21)

### 1.12 Response types

Check: each rule in `rules.json` has a `response`, exactly `warn`, `stop` or `emergency`, at SC-015's starting values (SR-08 and SR-09 `emergency`, the rest `stop`), each set logged (1.11); the leaf has `ReplyKind.WARN` (a reply naming its rule and at least one passage) and `SafetyRule.response`; the walker shows a warn and continues, a helpful stop (why, the safe next action, what to bring the supervisor) or an emergency, and a test plants a rule of each response.

Moved: from Phase 1
Waits on: Ghost's go-ahead to run it; SC-015 is in force and the leaf change is approved (Ghost, 2026-11-21)

### 1.13 The over-firing of SR-03 and SR-02

Check: on the demo pack, SR-03 no longer fires on step-12's prohibition or on the safe method it prescribes (fail-04, fail-07, fail-10), and SR-08 no longer fires on fail-04's list of signs to watch for, each change logged (1.11) with "engineer to confirm"; SR-02's meter, probe, test-lead and crimp triggers are put to the engineer (1.14), not changed here; `test/test_safety.py`'s pin of what the demo pack fires updated; a planted step that does part connectors under load still fires SR-03.

Moved: from Phase 1
Waits on: Ghost's go-ahead to run it; SC-016 is in force, and Ghost may confirm a precision fix before an engineer is named (SC-015, 2026-11-21)

### 1.14 The engineer's review

Check: an electrical engineer has read SR-01 to SR-14 (words, triggers, responses, and each claim against its source's page in `library/sources/` where the library holds it), the first queue of SC-015 (SR-03, SR-02's meter and crimp triggers, SR-05, SR-11's split), the four open marks (SR-02, SR-06, SR-08 and SR-09's first-aid sentence, SR-12), the demo pack's five flagged claims (fail-04, step-07, step-09, fail-03, fail-08) with its mirrored sources S3 and S8, and the evaluation set's safety, warn and must-not-stop cases; each judgement is a change-log entry (1.11) with the role "electrical engineer".

Moved: from Phase 1
Waits on: an engineer (not yet named; naming one is Ghost's next action, F-16)
