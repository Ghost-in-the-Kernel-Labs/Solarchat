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

1. **TODO 1.3 is landed, with Ghost's read still open**: landed 2026-11-21 on Ghost's word with the draft's answers;
   Ghost has not yet read `docs/SAFETY-RULES.md`; the five points stay open. J-027 (renumbered from J-026 at the landing),
   reviewed by the coordinator. Fourteen rules, SR-01 to SR-14, in `solarchat/safety/rules.json`, read by
   `solarchat/safety/rules.py` as the leaf's `SafetyRule`; `docs/SAFETY-RULES.md` generated from them
   (`scripts/safety_rules_doc.py`); the pack check refuses a pack that names a rule or tells the reader to skip one.
   1.3 is in `docs/DONE.md`, marked as all but Ghost's read. Next for Ghost: read `docs/SAFETY-RULES.md` and answer its
   five "Ghost to confirm" marks (below, For Ghost 1); a change of an answer is a change to `rules.json`, then
   `scripts/safety_rules_doc.py`.
3. **The demo of Monday 2026-11-23** (SC-010), after 1.3: 1.4 the seed pack in the format (convert
   `packs/seed-mc4-leads/` to passages, flows and procedures; still not admitted), 1.5 demo mode, 1.6 the walker
   (`solarchat/walker`, a module Ghost approved), 1.7 the safety rules in the walker (it must settle whether a
   rule's triggers match the step's text or the worker's replies, and match whole words: the 1.3 worker's notes),
   1.8 the offline shell. Each went to a fresh worker of its grade with the brief of `docs/when/hand-out-a-task.md`,
   saved on its own branch and landed by the coordinator after Ghost's word; 1.3 went to the strong grade.
4. **1.9 the evaluation set**, frozen before any search or model; 1.10 Tune-up pass 1, with the next human
   maintainability pass (SC-011: Ghost-Core's toolkit under `scripts/` a few files at a time, each with its proof
   that nothing changed; then the tests).

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

1. **The safety rules** (TODO 1.3, landed 2026-11-21 on Ghost's word with the draft's answers; Ghost has not yet read
   `docs/SAFETY-RULES.md`; the five points stay open): read `docs/SAFETY-RULES.md`, and answer its five
   "Ghost to confirm" marks: SR-02, is measuring a voltage a stop for the newest contractor (the draft: yes); SR-03,
   is plugging connectors together a stop as well as pulling them apart (the makers say de-energise for both); SR-06,
   the overhead-lines rule (beyond the brief; it gives no distance, so the site's applies); SR-08 and SR-09, the
   emergency and first-aid sentences the cited sources do not state; SR-12, the never-bypass rule (beyond the brief).
   Also: the roof, ladder and climb triggers stop every rooftop step (deliberate); four sources were cited from search
   results without the page being read (J-027).
2. **Page citations** (SC-012, on `agent/page-citations`): the seed pack's citations of its document sources carry a
   page, and 89 of them are `"unknown"`: S3 Trina installation manual 35, S7 PVEL/HelioVolta safety guide 22, S5 Victron
   troubleshooting chapter 19, S4 Victron installation chapter 10, S6 BRE fire report 3 (S8's 15 citations use page 15,
   from its title). A person finds each page in the manual; the check counts the unknown pages and prints the total
   (`python3 -I scripts/checks/packs.py <pack>`), and does not yet run over the seed pack, which TODO 1.4 converts.
3. Read the demo pack with an engineer's eye before anyone relies on it. The worker flagged claims it could not
   source: fail-04 (reversed leads can damage some devices), step-07's stop (battery not yet wired), step-09 (the
   gentle pull), fail-03 (some shortfall from the label is normal), fail-08's fire wording. Sources S3 and S8 were
   read from third-party mirrors and want official copies.
4. The demo pack fits a small kit (a charge controller, a power station, covering the panel) better than a large
   site. A second demo pack, stringing modules on a utility site, would be nearer the users of F-01.
5. `CLAUDE.md`'s three rules still state Core C-033 without SC-007's narrowing, which is why the worker kept to
   openly licensed pictures. Say whether `CLAUDE.md` should name SC-007.
6. Whether the deploying company may be named in the repository (the agent has not written its name).
7. The app's stack (roadmap 5.1): one web client that is both the website and an installable app, or a native app.
8. Which make and model the first real pack covers (roadmap 6.2); Ghost named First Solar as the most troublesome.
9. A trademark search on the name Hadley before it reaches an app store.
10. Ghost-Core's `docs/GHOST-IN-THE-KERNEL.md` opening is a condensed rewrite of the manifesto (J-023); the fix is
   Core's, in a session with push access to it.
11. A stop hook asks for a push whenever a branch is ahead of origin (2026-11-21: it fired on a branch restarted
   from `main`); a hook is outside what an agent may change (`docs/when/coordinate.md`), so it is reported here.
12. `scripts/ship.sh` is stamped without its executable bit (run it as `bash scripts/ship.sh`); a mode change to a
   gate file is yours.
12. **The coordinator's conditional** (2026-11-21, Ghost's ask): `CLAUDE.md` gains "If you are the coordinator",
   sending it to `docs/when/coordinate.md`, "Who does each item", the assignment rule of C-026, C-027 and C-036 in
   seven steps. The wording is the agent's, and two steps go past the ghost's text for your confirmation: a raise above
   the score writes its reason in the journal, and a strong Cost line on an item scored lower says why. Ghost-Core's
   template could carry the same section (a Core change, in a session with push access to it). Saved on
   `agent/coordinator-conditional`; land it on your word.

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
- Branches left on origin, all merged into `main` by squash and safe to delete (this session's proxy refuses a
  branch deletion, HTTP 403): `agent/words-1-1`, `agent/pack-format-1-2`; `agent/safety-rules-1-3`, now landed.
  Earlier ones Ghost deleted on 2026-11-21. The remote's name is `Ghost-in-the-Kernel-Labs/Solarchat`; a fresh clone
  may still name it in lower case, which works through GitHub's redirect.
- Branches deleted earlier, kept here for the record: `claude/audience-f01`, `claude/gate-0-2`, `agent/seed-pack`.
