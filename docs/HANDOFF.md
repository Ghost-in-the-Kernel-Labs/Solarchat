# Handoff: what to work on next, and what is waiting on whom

Read `CLAUDE.md` first, then this. `TODO.md` is the chain in order; `docs/DONE.md` is what is finished.

## Where the project stands (2026-11-21)

Founded, planned, and holding one demo pack and the leaf. `main` carries the stamp, decisions SC-001 to
SC-008, the project's ghost, the roadmap (Phases 1 to 6), the six-pin lockfile, and the demo pack
`packs/seed-mc4-leads/` (J-017). The full gate passes (J-016, a tune-up commit; the count restarted there).
TODO 0.4 landed (J-018): the package `solarchat/`, the contract's HAD-01 to HAD-06, the module map (leaf, packs,
safety, project, cli) and the leaf's types; 0.2 closed with it. Phase 0 is closed by Tune-up pass 0 (J-019) but
for 0.5, which waits on Ghost in Phase W.

What Solarchat is, in the roadmap's words (`docs/ROADMAP.md` §1 to §3, F-01 to F-15): an assistant named Hadley
that walks workers on solar sites through installing panels and finding faults, on a phone, answering only from
knowledge packs; online it calls Claude Sonnet through the Anthropic API with no tools and no connectors, and reads
photos; offline it runs on the packs, the flows and the safety rules, with at most a small model that only chooses
which admitted passage to show.

## Next, in order

1. **The tune-up with the first human maintainability pass** (SC-011), Ghost's word: right after 1.2.
2. **The demo of Monday 2026-11-23** (SC-010): 1.3 the safety rules (Ghost reads the list), 1.4 the seed pack in
   the format, 1.5 demo mode, 1.6 the walker, 1.7 the safety rules in the walker, 1.8 the offline shell.
3. **1.9 the evaluation set**, frozen before any search or model; 1.10 Tune-up pass 1.

## Settled by Ghost

- 2026-11-20: prefix SC, the python stack, floor grade mid; SC-002 to SC-005 (J-002); the online model, photos,
  speech (J-006, F-07 to F-09); offline the small model only chooses, online first, an app and a website (J-008);
  the manner and the name Hadley (J-009, J-010); no connectors, pictures per step (J-011); demo packs may carry web
  pictures with provenance (J-012, SC-007); the model-name check removed (J-007, SC-006).
- 2026-11-21: the users are workers on sites, not homeowners (J-013); no mutation run (J-015, SC-008); the package
  `solarchat`, the five modules, the prefix HAD and the contract keeping its name (J-018); the repository's default
  branch set to `main` and the old branches deleted (J-019); run Tune-up pass 0 (J-019);
  a tune-up commit every twenty-five commits, not eight (SC-009, J-020); the pack format's procedures, linear
  flows and installation_type (J-022); Monday's demo as an offline walk-through with a labelled demo mode, and the
  walker module (SC-010, J-024); the human maintainability standard (SC-011, J-024).
- The wording of SC-002 to SC-008 is the agent's, for Ghost to confirm.

## For Ghost: waiting on you

1. Read the demo pack with an engineer's eye before anyone relies on it. The worker flagged claims it could not
   source: fail-04 (reversed leads can damage some devices), step-07's stop (battery not yet wired), step-09 (the
   gentle pull), fail-03 (some shortfall from the label is normal), fail-08's fire wording. Sources S3 and S8 were
   read from third-party mirrors and want official copies.
2. The demo pack fits a small kit (a charge controller, a power station, covering the panel) better than a large
   site. A second demo pack, stringing modules on a utility site, would be nearer the users of F-01.
3. `CLAUDE.md`'s three rules still state Core C-033 without SC-007's narrowing, which is why the worker kept to
   openly licensed pictures. Say whether `CLAUDE.md` should name SC-007.
4. Whether the deploying company may be named in the repository (the agent has not written its name).
5. The app's stack (roadmap 5.1): one web client that is both the website and an installable app, or a native app.
6. Which make and model the first real pack covers (roadmap 6.2); Ghost named First Solar as the most troublesome.
7. A trademark search on the name Hadley before it reaches an app store.
8. Ghost-Core's `docs/GHOST-IN-THE-KERNEL.md` opening is a condensed rewrite of the manifesto (J-023); the fix is
   Core's, in a session with push access to it.
9. A stop hook asks for a push whenever a branch is ahead of origin (2026-11-21: it fired on a branch restarted
   from `main`); a hook is outside what an agent may change (`docs/when/coordinate.md`), so it is reported here.
10. `scripts/ship.sh` is stamped without its executable bit (run it as `bash scripts/ship.sh`); a mode change to a
   gate file is yours.

Audit advisories (tune-up step 2): the python gate runs no audit step, so none are listed. An audit tool
(`pip-audit` or the like) would be a new dependency, Ghost's to approve; until then the review's layers 1, 2 and 4
stand alone (`docs/DEPENDENCY-REVIEW.md`).

## Trials: questions settled by a run, not an argument

(none yet; roadmap 3.7 and 5.1 name the first two)

## What to distrust

- The demo pack is not admitted (SC-005) and was written to a provisional layout before 1.2 and 1.3 existed. Its
  drawings were looked at once, rendered together; its text was not read in full by the coordinator.
- The project's ghost and the roadmap are the agent's drafts from Ghost's words, landed for Ghost to correct.
- A session's venv: `python3.12 -m venv .venv && .venv/bin/pip install --only-binary :all: --require-hashes -r requirements.lock`.
- Branches left on origin, all merged into `main` by squash and safe to delete: `claude/audience-f01`, `claude/gate-0-2`, `agent/seed-pack`.
