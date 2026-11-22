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

### 1.7 The index

Check: a pack on disk becomes an index, the same bytes every time (goldens, SC-003); a test builds it twice and holds the bytes equal to a golden file.

### 1.8 Keyword search behind `answer()`

Check: `answer()`'s offline mode ranks a pack's passages by keyword, in the standard library, and the runner (1.6) scores it on the evaluation set (1.5): the right passage cited for each in-scope question, "I do not know" with no passage where the passages do not cover the question, the out-of-scope questions refused (HAD-03); the scores of the run are recorded with it (HAD-02).

### 1.10 The safety rules matched on the worker's words

Check: a worker's question fires a safety rule on its own words, whatever passage the answerer finds or does not find: "I got a shock" gives SR-09's emergency with no passage at all, so the door's order of steps is amended (the design's step 6 reads the question, as well as the cited passages' text, and runs before the "I do not know" of step 5; never the finding's text, never Hadley's own replies), the design is changed first and the change is a decision (HAD-04). SR-14's "do not know" and "don't know" are settled first against HAD-03: "I don't know which lead is positive" is a question, answered from the packs or with "I do not know", not a stop; SR-14 keeps the worker's words that say they are untrained or unsure of the work itself ("not trained", "never done"). The session profile of SC-020 is built here: at the start of a session Hadley asks three or four short questions (role: new to solar, crew member or licensed electrician; signed off by the worker's supervisor, on this site, for meter tests, for connector work, for work at height with fall protection in place), asking what the worker is authorised for and never their credentials; a safety rule may name which profile answers lower its response (SR-02's meter triggers: stop to warn when signed off for meter tests, the warn carrying the precaution: a meter and test leads rated for the string's DC voltage; measure at the connectors; never across a loaded circuit), only a rule, never a pack, and never an emergency; the profile may change how much is explained, never which steps or stops are given; the answers are self-declared and a company's setting for a worker overrides them; each session records the profile it ran under and the engineer's packet shows which answers lowered which rule (P-20). Before any code the design settles, in `docs/designs/`: how the profile is held; how a rule names its lowerings (and how that enters its fingerprint and change log, SC-016); the shape of the side file, keyed by case id, that gives an evaluation case a profile without editing the frozen `evals/v1.json` or its hash (mns-09 runs as signed off for meter tests); whether the meter triggers split from SR-02 into their own rule. SR-08's "smoke" in `fail-04-check-2`'s list of signs to watch for (mns-03) is settled here, not in 1.13. Ghost decides the trigger list on his word (SC-016, role maintainer, "engineer to confirm"); each change is logged (1.11). On the evaluation set, mns-03 and mns-09 pass and leave `evals/known-failures.json`, `safe-01` still stops and the record shows each change (`scripts/eval.py --write`, with `--accept-fall` naming a decision for any case that falls); a planted question with a hazard in its words and no passage found fires its rule.

The session profile, its first step, is designed in `docs/designs/session-profile.md` (J-074; Ghost's answers recorded there); its two slices are built first, then the worker's-words matching, designed in `docs/designs/worker-words.md` (J-075).

Slice 1 built (J-077): the leaf's `Profile` and `SafetyRule.lowered_for`, three lowerings (SR-02 meter, SR-11 battery, SR-05 height), the door's `profile` argument, `evals/profiles.json` and the runner; mns-09 left `known-failures.json`. Slice 2 (the questions, the explanation, the lowered warn's first line) is next.

The worker's-words step built (J-078, on `agent/worker-words`; the coordinator renumbers at landing): `door.py`'s words step, emergencies on the question only, the three trigger changes (one of them, SR-07's, awaits Ghost's wording for safe-16, see the journal), mns-03 off `known-failures.json`. 1.10 stays open for slice 2.

### 1.21 The model roles and the live bank run

Check: `solarchat/model/roles.py`, a new file in the module `model` (the only importer of the SDK, SC-021), holds the interrogator, the grader and the explainer of the design's 4.2 and 7(a), each with an injectable client and a JSON schema; `test/test_roles.py` with a fake client holds that the grader's request carries the rule, the transcript and the cited passages and never `SYSTEM_PROMPT` or a guard, that the interrogator's request never carries the rule's question, and each schema's refusal and malformed reply; `scripts/bank_run.py --live` runs a sample through the door with `ClaudeAnswerer` (`--model`, Haiku 5.5 by default), grades it, grades the canaries in `evals/bank/canaries.json`, re-grades the spot-check sample on `--check-model`, prints the watch list, the tokens and the cost of each model, writes transcripts under `build/bank/` and one ledger line, with the `checks` field of the design's 5.4 (2); `--replay` re-grades stored transcripts with no bot call; `--live` is named by no gate script. The first live run is Ghost's, by hand.

### 1.22 Drafting the bank with Opus

Check: `scripts/bank_draft.py --live --family F --count N` asks Claude Opus 5.5 (the drafter role in `solarchat/model/roles.py`) for rules in the shape of 3.2 from the pack, `solarchat/safety/rules.json` and the library's index, given the family's existing behaviours, and writes them to `build/bank/drafts/`; `--accept D-nnn [--skip id ...]` runs the bank's check on each, numbers the accepted rules and appends them, never editing an accepted rule (tested with a fake client); the first batches (`scope`, `allows`, `ask`, `pace`, then `safety`) are reviewed and accepted, the review recorded in the journal.

### 1.23 Harm triage

Check: `scripts/triage.py <run> <rule>` writes `evals/triage/TR-nnn.json` in the shape of the design's section 7: three explain calls with the bot's own context, the suspects ranked and widened by the cited passages and the passage sharing the most five-word phrases with the harmful reply, a baseline arm and an ablated arm of eight re-runs for each of the top three (the passage removed in memory, the pack on disk untouched, a test holds its bytes), and the outcome by 7(b) to 7(d) (`pack-change`, `pack-finding`, `safety-trigger`, `guard`, `rare`, `unresolved`), with `engineer_to_confirm` set on a pack change; tested with fakes for every outcome, no model called in the fast loop.

### 1.24 Guards

Check: `solarchat/model/guards.json` in the shape of the design's section 6, appended to the system block in id order by `system_text` (the cache-stable bytes test still holds); `ClaudeAnswerer` takes `guards`; a check in the fast loop refuses a guard that names no triage record whose outcome is `guard`, and a total over the budget Ghost sets; a run with a guard's served rules in its sample also runs them with the guard removed and records both verdicts; the retirement rule of section 7 is printed on the trend page when a guard meets it; 1.14's check is extended in its text to list triage pack changes and findings, the guards in force with their triage records, and the watch list's safety rules.

### 1.26 Packs cover the safety rules for their own make and model (SC-024)

Check: first a design in `docs/designs/` (SC-024 in force, Ghost 2026-11-22; HAD-04 as amended): the manifest's coverage field (per rule id: the covering passages and the response each gives), how the door's step 6 and 1.10's worker's-words step choose a covering passage over the general rule, how the walker (2.3) does the same, the emergency floor for SR-08 and SR-09, what a reply shows and cites, and how a session records which pack covered which rule; Ghost's questions ranked, if any. Then the build: the pack check refuses a declaration that names an unknown rule, a passage not in the pack, a covering passage whose citation page is "unknown", a declaration in a pack that is neither `field` nor a `demo` pack on Ghost's word, and any declaration that lowers SR-08 or SR-09, each by a planted break under `test/fixtures/broken/packs/`; the door gives a covering passage's response and words, cited, in place of the rule, and the general rule wherever no declaration exists, each shown by a test on a fixture pack; the engineer's packet (1.14) lists every declaration. The seed pack declares nothing until Ghost names one.

Design written: `docs/designs/pack-coverage.md` (J-070), its section 8 the slices and section 9 Ghost's five questions; Ghost answered all five as recommended (J-071), the leaf change approved; the slices are built in order.

Slice 1 built (J-072): `safety_coverage` in the pack format, the check's six refusals (`scripts/checks/coverage.py`), `SafetyCoverage` in the leaf and `Pack.coverage`, the `covered` fixture; slices 2 to 4 remain, so 1.26 stays open.

### 1.27 Tune-up pass 1

Check: `docs/when/tune-up.md` followed in full; the metrics table written; the navigation log reviewed; the human maintainability pass for the code written since the last one (SC-011).

Renumbered: from 1.18, so the bank's items 1.19 to 1.24 come before it (SC-023 in force, J-051); then from 1.25, so 1.26 comes before it (SC-024 in force, J-069).

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

Items 2.9 and 2.10 of `docs/ROADMAP.md` (renumbered from 2.5 and 2.7, J-058) join this chain, before this pass, when Phase 2 is reached; this pass is then renumbered after them.

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

Check: on the demo pack, SR-03 no longer fires on step-12's prohibition or on the safe method it prescribes (fail-04, fail-07, fail-10), each change logged (1.11) with "engineer to confirm"; SR-02's meter, probe and test-lead triggers are kept for the engineer's final review (6.4), not changed here (its crimp trigger was removed on Ghost's word, J-041); `test/test_safety.py`'s pin of what the demo pack fires updated; a planted step that does part connectors under load still fires SR-03.

Done so far (J-041, Ghost's word of 2026-11-21): SR-10's trigger 'add a panel in series' is removed (mns-06 no longer over-fires) and SR-02's trigger 'crimp' is removed, each logged pending engineer review (F-16). Left open: mns-03 (SR-08 on fail-04-check-2) is 1.10's (old 2.6, matching on the worker's words, Ghost 2026-11-21), not this item's; mns-09 (SR-02 on 'multimeter') is 1.10's too, by Ghost's meter sign-off decision (SC-020). Not closed.

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
