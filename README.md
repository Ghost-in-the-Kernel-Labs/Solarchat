# Solarchat

A domain-only chatbot that walks a customer through setting up and troubleshooting specific makes and models of solar panels, answering only from swappable knowledge packs of manuals and debugging guides; it runs no code.

## Status

No feature exists yet. The project is stamped from Ghost-Core ca0637d; it begins at TODO 0.1, and
`docs/HANDOFF.md` says what the human fills in first.

## Running the fast loop

    bash scripts/fast.sh

Every document check and unit test, with nothing installed; `scripts/save.sh` saves a session's work on its own
branch, `scripts/gate.sh --fast` is the check before a landing (`scripts/commit.sh`), `scripts/ship.sh` the only push
to `main`, and the full `scripts/gate.sh` runs at each tune-up (C-040).
