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

### 1.3 The safety rules, version 1

Check: a document outside every pack lists the stop points for the newest contractor on a site, each with the words the worker is shown, and says the site's own safety procedures come first; the pack check refuses a pack that names or overrides one; Ghost has read the list.

### 1.4 The seed pack

Check: one pack in the repository passes 1.2's check; its manifest names a source whose licence allows redistribution, and the licence text or its link is recorded; it covers connecting a panel, polarity, and a panel that shows no output.

### 1.5 The evaluation set, version 1

Check: at least thirty in-scope questions each naming the passage that answers it, fifteen out-of-scope questions marked refuse, and ten safety cases marked stop; a check holds the file's shape and that every named passage exists; the set's hash is recorded and a later change without a decision is refused.

### 1.6 Tune-up pass 1

Check: `docs/when/tune-up.md` followed in full; the metrics table written; the navigation log reviewed.

## Phase W: waiting on Ghost

### 0.5 The founding decisions

Check: `theGhost.md` holds Ghost's founding decisions for Solarchat, a decision for each core decision it refuses among them, each with Ghost as its Source. Agents cannot author Ghost's decisions: an agent drafts the questions for Ghost in `docs/HANDOFF.md`, and a builder that reports "waiting on Ghost" has done its job.

Moved: from Phase 0
Waits on: Ghost's founding decisions (the questions in `docs/HANDOFF.md`, "For Ghost": the app's stack, the first real pack's make and model, naming the deploying company, SC-007 in `CLAUDE.md`, the trademark search)
