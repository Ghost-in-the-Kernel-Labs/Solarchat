# Solarchat

Solarchat is an assistant, named **Hadley**, that walks workers on solar sites through installing panels and
finding faults, one step at a time, on a phone. Hadley answers only from **knowledge packs**: manuals and
troubleshooting guides that a person has checked and admitted. It never improvises electrical advice, and it stops
and sends the worker to the site supervisor or engineer wherever a mistake could hurt someone.

This README is for a person reviewing or maintaining the code. How Hadley is kept from giving dangerous advice is
explained in full in [docs/SAFETY-AND-COMPLIANCE.md](docs/SAFETY-AND-COMPLIANCE.md).

## Where the project stands

- **Built:** the contract every module shares (`docs/CONTRACT.md`), the knowledge-pack format and the check that
  refuses a broken pack, the shared types in `solarchat/leaf/`, and the checks and gates that hold the repository to
  its rules.
- **Being built for the demo of 2026-11-23:** the safety rules, the demo pack in the new format, a clearly labelled
  demo mode, the walker that steps a worker through a procedure or a fault, and a command-line conversation that
  runs with the network off (`TODO.md`, items 1.3 to 1.8).
- **Later:** the frozen evaluation set (1.9), keyword search, a small local model that only chooses which checked
  passage to show, the hosted service, and the phone app (`docs/ROADMAP.md`, Phases 2 to 6).

No language model is called anywhere in the code today.

## What each part does

### The product: `solarchat/`

The product is a Python package of modules, one concern each. `docs/modules.json` says what each module may
import, and `test/test_modules.py` refuses an import it does not allow.

| Module | What it does | State |
| --- | --- | --- |
| `solarchat/leaf/` | The contract in code: the passage and its reference, a reply (an answer, "I do not know", or a stop) that cannot be built in a form the contract forbids, and the test of whether a pack is admitted. Every other module imports it; it imports nothing of the project's own. | built |
| `solarchat/packs/` | Reads a knowledge pack from disk and checks it. | planned (the check is in `scripts/checks/packs.py` today) |
| `solarchat/safety/` | The fixed safety rules, kept outside every pack, and the decision to stop and send the worker to the supervisor. | planned (1.3, 1.7) |
| `solarchat/walker/` | Steps a worker through a procedure or a troubleshooting flow, one step at a time, to a fix or a stop. | planned (1.6) |
| `solarchat/project/` | Calls the other modules in order. | planned |
| `solarchat/cli/` | The command-line conversation; parses input and calls `project`, with no logic of its own. | planned (1.8) |

### The knowledge: `packs/`

One folder per knowledge pack. `packs/seed-mc4-leads/` is the demo pack (connecting a panel by its MC4 leads),
written before the format existed and marked **not admitted**: no engineer has reviewed it. `packs/TYPES.md` lists
the installation types a pack can cover. The format a pack must follow is the section "The pack format" in
`docs/CONTRACT.md`.

### The rules: documents at the root and in `docs/`

| File | What it holds |
| --- | --- |
| `theGhost.md` | Every decision, with its reason and what holds it. Core decisions are `C-nnn`, Solarchat's are `SC-nnn`. `docs/decisions.md` is a one-line-per-decision index of it. |
| `docs/CONTRACT.md` | The invariants (`HAD-01` to `HAD-06`) every module obeys, and the knowledge-pack format. |
| `docs/DIRECTIVE-MAP.md` | Each decision and invariant, and the functions that hold it in code: the way from a rule to its code and back. Generated. |
| `docs/SAFETY-AND-COMPLIANCE.md` | How Hadley is kept to checked instructions and away from improvised advice. |
| `docs/GHOST-IN-THE-KERNEL.md` | The philosophy the project is built on: the system should remember why it exists. |
| `docs/ROADMAP.md`, `TODO.md`, `docs/DONE.md` | The plan, the open items in order, and the finished ones. |
| `docs/GLOSSARY.md` | The project's words, one meaning each (pack, passage, flow, mode, admitted, safety rule, and the rest). |
| `docs/journal/` | What happened and why, one entry per event (`J-nnn`). |
| `docs/HANDOFF.md` | What to work on next, and what waits on the maintainer. |
| `docs/SUPPLY-CHAIN.md`, `docs/DEPENDENCY-REVIEW.md`, `docs/REVIEWED-VERSIONS.md` | How a dependency is allowed in and kept safe. |
| `CLAUDE.md`, `docs/when/`, `docs/paths/`, `docs/AGENT.md`, `docs/NAVIGATION-LOG.md` | Instructions for the AI agents that work in the repository, and the measures of how well they find their way. |

### The checks and gates: `scripts/`

Everything here runs on the Python standard library with nothing installed. Most of it is inherited from
Ghost-Core, the template the project was stamped from.

| Script | What it does |
| --- | --- |
| `scripts/fast.sh` | The fast loop: every document check and unit test, in about 20 seconds. Run it after every change. |
| `scripts/gate.sh` | The gate. `--fast` is the check before a change lands; the full gate (slow tests, linters, metrics) runs at each tune-up. It records the tree it passed on. |
| `scripts/save.sh` | Saves a session's work on its own branch, after a scan for keys. |
| `scripts/commit.sh` | The only way a commit reaches `main`: scans for keys, runs the fast loop, refuses a tree the gate did not pass, and refuses ordinary commits while a tune-up is due (every 25 commits). |
| `scripts/ship.sh` | The only push to `main`. |
| `scripts/decisions_index.py`, `scripts/journal_index.py`, `scripts/directive_map.py`, `scripts/metrics.py` | Write the generated files: the decision index, the journal index, the directive map, and the metrics table in `docs/AGENT.md`. A test fails when any of them is stale. |
| `scripts/next_id.py` | The next free decision or journal number. |
| `scripts/score.py` | Places each open TODO item at a grade (how strong an agent it needs), from facts. |
| `scripts/review_scan.py` | Scans a dependency update's diff for warning signs before it is allowed in. |
| `scripts/checks/packs.py` | Checks a knowledge pack against the format: refuses a missing licence, a flow with no stop, a passage with no source, a picture with no alt text, and more. |
| `scripts/checks/contract.py`, `modules.py`, `imports.py` | Hold the code to the contract, the module map and the lockfile. |
| `scripts/checks/secrets.py`, `supply_chain.py`, `dependency_review.py` | Refuse a committed key, a hook or unpinned workflow, and an unreviewed dependency. |
| `scripts/checks/readability.py` | Short functions, a docstring on every function, no `*args` or `**kwargs`. |
| `scripts/checks/ghost.py`, `journal.py`, `todo.py`, `glossary.py`, `pointers.py`, `registers.py`, `navigation.py`, `claude_md.py`, `metrics.py`, `agent_table.py`, `score.py`, `grades.py`, `tables.py`, `gate_record.py`, `common.py` | Hold each document to its shape: numbered in order, every field present, every pointer resolving. |

### The tests: `test/`

One test file per check or module (`test/test_packs.py` for the pack check, `test/test_leaf.py` for the leaf, and
so on). Each check is also shown refusing a deliberately broken input, kept under `test/fixtures/broken/`; a check
that cannot fail proves nothing. `test/fixtures/packs/good/` is a small well-formed pack.

### The toolchain: `stacks/python/`, `requirements.in`, `requirements.lock`, `pyproject.toml`

The Python stack's gate and its pinned tools (pytest and ruff, installed only from the hashed lockfile).

## Running it

```bash
bash scripts/fast.sh
```

The fast loop needs nothing installed. The full gate needs the virtual environment:

```bash
python3.12 -m venv .venv && .venv/bin/pip install --only-binary :all: --require-hashes -r requirements.lock
```

## How a change is made

A change is saved on a working branch (`scripts/save.sh`), passes the fast checks (`scripts/gate.sh --fast`), is
committed through `scripts/commit.sh` and pushed with `scripts/ship.sh`. A function that carries out a decision
says so on the line above it, `# Decision: SC-005 (why)`, and `docs/DIRECTIVE-MAP.md` collects those citations. A
new module, a new dependency, or a change to a decision is the maintainer's call, recorded in `theGhost.md`.
