# Handoff: what to work on next, and what is waiting on whom

Read `CLAUDE.md` first, then this. `TODO.md` is the chain in order; `docs/DONE.md` is what is finished.

## Where the project stands (2026-11-20)

Stamped from Ghost-Core today and landed on `main` at Ghost's word (J-005) with the founding refusals (SC-002 to
SC-005), the project's ghost, the roadmap and the founding lockfile. Nothing of Solarchat's own is built. Open in
Phase 0: 0.2 (the full gate), 0.4 (the contract and modules), 0.5 (any further founding decision), 0.6.

## Settled by Ghost, 2026-11-20

- The prefix is SC, the stack python, the floor grade mid.
- SC-002 to SC-005 (J-002): the answering step calls a model through one module and no test does; goldens for the
  deterministic parts and the evaluation set for answers; mutation over deterministic code, not prompt text; a
  person admits a pack's text and the bot answers only from it. The wording is the agent's, for your confirmation,
  and covers TODO 0.5's refusals; any other founding decision of yours is still to write.
- Retrieval starts as keyword search in the standard library (Core C-002); the model client is the first dependency
  that will be proposed to you (Core C-012).

## For Ghost: waiting on you

1. Name this project's ghost (`docs/GHOST-IN-THE-KERNEL.md`, TODO 0.1).
2. Pin the stack's image digest and dependencies; wire mutation (TODO 0.2); every `STAMP` marker in the tree is a line to fill (`grep -rn STAMP .`).
3. Write the roadmap's §1 to §6 and Phase 1's items in `TODO.md` (TODO 0.3).
4. Write the first invariants of the contract and set `docs/modules.json` (TODO 0.4).
5. Write the founding decisions in `theGhost.md`, a decision for each core decision this project refuses among them (TODO 0.5): agents cannot author them.

## Trials: questions settled by a run, not an argument

(none yet)

## What to distrust

- TODO 0.2 is half done (J-004): the full python gate stops at ruff reading `test/fixtures/broken/` and at
  `test/test_supply_chain.py:97`; mutmut still names `PROJECT/` and has nothing to mutate until product code exists.
  A session's venv: `python3.12 -m venv .venv && .venv/bin/pip install --only-binary :all: --require-hashes -r requirements.lock`.

## Drafts for Ghost to read (J-003)

- The project's ghost (`docs/GHOST-IN-THE-KERNEL.md`) and the roadmap (`docs/ROADMAP.md`, Phases 1 to 6; `TODO.md`,
  Phase 1) are the agent's drafts from your words of 2026-11-20. Landed as drafts at your word (J-005); correct them freely with later commits.
- Settled by you (J-006): the online model is Claude Sonnet through the Anthropic API, with photos; speech wanted;
  offline, a light open model downloaded inside an app (F-07 to F-09).
- Settled by you (J-008): offline, the small model only chooses the admitted passage and flow, as the worst-case
  backup; online first whenever there is a connection; a phone app and a website (F-10, F-11, P-19).
- Open, the agent's questions to you: connectors (the agent recommends none: they are tools, SC-002); the app's
  stack (5.1); which make and model first (6.2).
