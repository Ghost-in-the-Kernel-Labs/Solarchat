# Done: finished items of TODO.md, numbers kept

An item moves here from `TODO.md` when its check passes, keeping its number because other documents
cite it. Each line: the item, the date, the journal entries, and its check with a tick.

## Phase 0: founding

### 0.1 This project's ghost, named

Done 2026-11-20 (J-003, J-005). Check: `docs/GHOST-IN-THE-KERNEL.md`'s "This project's ghost" section replaced by Solarchat's; the STAMP comment gone; committed by `scripts/commit.sh --docs-only` with every staged path under `docs/` (the gate refuses at the stack until 0.2), so the item's move from `TODO.md` to `docs/DONE.md` rides in 0.2's commit. ✓

### 0.2 The stack wired

Done 2026-11-21 (J-004, J-016, J-018). Check: `stacks/python/gate.sh` runs green under its image (no mutation run: SC-008), so `scripts/gate.sh` passes and records the tree (J-016's full gate); `stacks/python/PRESENT` present; its STAMP markers gone (the last, `pyproject.toml`'s and the two checks' `OUR_CODE`, by 0.4's package, J-018); each pin of the founding lockfile has its `unreviewed baseline` row in `docs/REVIEWED-VERSIONS.md`; the first commit through the gate landed, carrying 0.1's move to `docs/DONE.md`. ✓

### 0.3 The roadmap and TODO filled

Done 2026-11-20 (J-003, J-005). Check: `docs/ROADMAP.md` §1 to §6 written for Solarchat (its STAMP line gone, Phase 1 planned in §6) and `TODO.md` holds Phase 1's items in order, each with its Check line, ending with its tune-up pass. ✓

### 0.4 The contract and the leaf module

Done 2026-11-21 (J-018). Check: `docs/CONTRACT.md` written with its first invariants, HAD-01 to HAD-06, and kept under its template name, since `test/test_contract.py` reads that path (F-001; Ghost approved the plan in chat); `docs/modules.json`'s package (`solarchat.`) and modules (leaf, packs, safety, project, cli) set, Ghost's approval in chat (C-012); `test/test_contract.py`, now held both ways on `solarchat/leaf/`, and `test/test_modules.py` green on the real folders. ✓

### 0.6 Tune-up pass 0

Done 2026-11-21 (J-019). Check: `docs/when/tune-up.md` followed in full (step 3 does not apply: Solarchat stamps no project); the metrics table written from the warm full gate (fast loop 21.4 s, gate 0.8 min); the navigation log's "Last review" set to 7ef5101. 0.5 moved to Phase W, waiting on Ghost. ✓
