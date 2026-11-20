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

### 0.2 The stack wired

Check: `stacks/python/gate.sh` runs green under its image, mutation included, so `scripts/gate.sh` passes and records the tree; `stacks/python/PRESENT` present; its STAMP markers gone; each pin of the founding lockfile and image has its `unreviewed baseline` row in `docs/REVIEWED-VERSIONS.md` (`python3 -I scripts/checks/dependency_review.py --baseline J-nnn` prints them; `docs/DEPENDENCY-REVIEW.md`, "The record"); the first commit through the gate lands, carrying 0.1's move to `docs/DONE.md`.

### 0.4 The contract and the leaf module

Check: `docs/CONTRACT.md` renamed and its first invariants written; `docs/modules.json`'s package and modules set; `test/test_contract.py` and `test/test_modules.py` green on the real folders.

### 0.5 The founding decisions

Check: `theGhost.md` holds Ghost's founding decisions for Solarchat, a decision for each core decision it refuses among them, each with Ghost as its Source. Agents cannot author Ghost's decisions: an agent drafts the questions for Ghost in `docs/HANDOFF.md`, and a builder that reports "waiting on Ghost" has done its job.

### 0.6 Tune-up pass 0

Check: `docs/when/tune-up.md` followed in full; the metrics table written; the navigation log's "Last review" set.

## Phase 1: the pack and the oracle

### 1.1 The words

Check: `docs/GLOSSARY.md` holds pack, passage, flow, mode, admitted and safety rule, one meaning each; `test/test_glossary.py` green.

### 1.2 The pack format

Check: the contract document states the manifest's fields (make, model, version, source, licence, admitted by, admitted on), a passage and a flow (symptom, check, fix, stop); a check under `scripts/checks/` accepts a well-formed pack and refuses each planted break (a missing licence, a flow with no end, a passage with no source).

### 1.3 The safety rules, version 1

Check: a document outside every pack lists the stop points for a homeowner, each with the words the customer is shown; the pack check refuses a pack that names or overrides one; Ghost has read the list.

### 1.4 The seed pack

Check: one pack in the repository passes 1.2's check; its manifest names a source whose licence allows redistribution, and the licence text or its link is recorded; it covers connecting a panel, polarity, and a panel that shows no output.

### 1.5 The evaluation set, version 1

Check: at least thirty in-scope questions each naming the passage that answers it, fifteen out-of-scope questions marked refuse, and ten safety cases marked stop; a check holds the file's shape and that every named passage exists; the set's hash is recorded and a later change without a decision is refused.

### 1.6 Tune-up pass 1

Check: `docs/when/tune-up.md` followed in full; the metrics table written; the navigation log reviewed.
