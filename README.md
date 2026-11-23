# Solarchat

Solarchat is an assistant, named **Hadley**, that walks workers on solar sites through installing panels and
finding faults, one step at a time, on a phone. Hadley answers only from **knowledge packs**: manuals and
troubleshooting guides that a person has checked and handed to whoever loads the packs. It never improvises electrical advice, and it stops
and sends the worker to the site supervisor or engineer wherever a mistake could hurt someone.

This README is for a person reviewing or maintaining the code. How Hadley is kept from giving dangerous advice is
explained in full in [docs/SAFETY-AND-COMPLIANCE.md](docs/SAFETY-AND-COMPLIANCE.md).

## Where the project stands

- **Built:** the contract every module shares (`docs/CONTRACT.md`), the knowledge-pack format and the check that
  refuses a broken pack, the demo pack, the fourteen fixed safety rules as data, the frozen evaluation set, the
  answering door and the runner that scores an answerer on that set (1.6), a Claude answerer with a chat command
  and a live evaluation run (1.16), the rule bank's format and check (1.19), the command menu and the local key
  (2.5), and the checks and gates that hold the repository to its rules.
- **Open, in order (`TODO.md`):** the index and keyword search (1.7, 1.8), the safety rules applied in the door's
  answers and on the worker's own words (1.9, 1.10), the bank run, its model roles, drafting, harm triage and guards
  (1.20 to 1.24), SC-024's pack coverage of the safety rules (1.26), then Phase 1's tune-up pass (1.27). Phase 2 holds demo mode, the walker, the safety rules in the
  walker and the offline shell (2.1 to 2.4); speech out (2.7, `--voice`, J-056) is built.
- **Later:** speech in, which needs a dependency proposed to Ghost; a small local model that only chooses which
  checked passage to show, the hosted service and the phone app (`docs/ROADMAP.md`, Phases 3 to 6).

A language model is called only by hand: the `claude` answerer of the chat (`solarchat --pack <pack> --demo`) and
`scripts/eval.py --live`, both of which need a key; no test, check or gate calls one. The first live run of the
frozen set (2026-11-21, Haiku 5.5, `--model claude-haiku-5-5`) scored 66 of 90 at an estimated $0.0151 (J-051); its
recorded replies are not in the repository. The offline stub scores 34 of 90 (`evals/results/offline.json`). The
safety rules are not yet applied in the door's answers, so no reply of the door is a stop or a warn today (1.9).

## What each part does

### The product: `solarchat/`

The product is a Python package of modules, one concern each. `docs/modules.json` says what each module may
import, and `test/test_modules.py` refuses an import it does not allow.

| Module | What it does | State |
| --- | --- | --- |
| `solarchat/leaf/` | The contract in code: the passage and its reference, a reply (an answer, "I do not know", a warn or a stop) that cannot be built in a form the contract forbids, the conversation's turns, and the test of whether a pack may answer. Every other module imports it; it imports nothing of the project's own. | built |
| `solarchat/packs/` | Reads a knowledge pack from disk (`load.py`) and words each passage's citations with the page; the pack check is `scripts/checks/packs.py`. | built (1.2, 1.6) |
| `solarchat/answer/` | The answering door, `answer(question, packs, demo_mode, answerer)`, through which every mode answers; the offline stub `NoAnswer` and `RecordedAnswerer` (SC-019). It imports no model client. Its safety step is not built (1.9). | built (1.6) |
| `solarchat/safety/` | The fixed safety rules, kept outside every pack (`rules.json`, loaded by `rules.py`, which also says which rules a text fires). Nothing yet applies them to an answer. | rules built (1.3); applying them planned (1.9, 1.10, 2.3) |
| `solarchat/model/` | The only module that may import the model client: the Claude answerer (`claude.py`, Sonnet 5.5 or Haiku 5.5) and the local key store (`key.py`, SC-022 point 6). | built (1.16, 2.5) |
| `solarchat/walker/` | Steps a worker through a procedure or a troubleshooting flow, one step at a time, to a fix or a stop. | planned (2.2) |
| `solarchat/project/` | Calls the other modules in order: the chat (`chat.py`) and the key commands (`keys.py`). | built (1.16, 2.5) |
| `solarchat/cli/` | The command line: the menu, `--key`, and the chat; parses input and calls `project`, with no logic of its own. The offline shell that walks a procedure is 2.4. | built (1.16, 2.5); shell planned (2.4) |

### The knowledge: `packs/`

One folder per knowledge pack. `packs/seed-mc4-leads/` is the demo pack (connecting a panel by its MC4 leads),
in the pack format (passages, flows and a procedure) and marked `"status": "demo"`: no engineer has reviewed it. `packs/TYPES.md` lists
the installation types a pack can cover. The format a pack must follow is the section "The pack format" in
`docs/CONTRACT.md`.

### The reference library: `library/`

`library/sources/` holds source documents (regulations, manuals, checklists) as text with their licence and a hash.
They are source material, not packs: nothing there answers a worker (SC-014; `library/README.md`).

### The evaluation set: `evals/`

`evals/v1.json` is the frozen evaluation set, version 1 (TODO 1.5): questions a worker on site would type, each with
the reply the bot must give (an answer citing a named passage, "I do not know", a stop, an emergency, a warn, or
anything but a stop), written against the seed pack. `evals/v1.sha256` holds its hash; the set is frozen, and a change
needs a decision and the new hash. The automatic runner, `scripts/eval.py` (TODO 1.6), scores the bot on it and holds the result to `evals/results/offline.json`;
`evals/known-failures.json` names known failures; it is empty since 1.10 (J-079). The electrical engineer reviews the set at the end (TODO 6.4).
`evals/bank/` is the rule bank (SC-023, TODO 1.19): twenty hand-written conversational rules, sampled and read as a
trend, never a gate; nothing runs them yet (1.20).

### The rules: documents at the root and in `docs/`

| File | What it holds |
| --- | --- |
| `theGhost.md` | Every decision, with its reason and what holds it. Core decisions are `C-nnn`, Solarchat's are `SC-nnn`. `docs/decisions.md` is a one-line-per-decision index of it. |
| `docs/CONTRACT.md` | The invariants (`HAD-01` to `HAD-06`) every module obeys, and the knowledge-pack format. |
| `docs/DIRECTIVE-MAP.md` | Each decision and invariant, and the functions that hold it in code: the way from a rule to its code and back. Generated. |
| `docs/SAFETY-AND-COMPLIANCE.md` | How Hadley is kept to checked instructions and away from improvised advice. |
| `docs/GHOST-IN-THE-KERNEL.md` | The philosophy the project is built on: the system should remember why it exists. |
| `docs/ROADMAP.md`, `TODO.md`, `docs/DONE.md` | The plan, the open items in order, and the finished ones. |
| `docs/GLOSSARY.md` | The project's words, one meaning each (pack, passage, flow, mode, pack status, safety rule, and the rest). |
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
| `scripts/eval.py` | The evaluation runner: feeds each case of the set to the answering door, scores it by class, prints the table and the failures, and holds the run to the committed record (`--check`, `--write`); `--live` is the only way a model is called (`scripts/eval_core.py` scores, `scripts/eval_record.py` keeps the record). |
| `scripts/eval_live.py` | The live half of the runner: failure blocks, tokens and estimated cost for a run on a real model. Named by no gate script. |
| `scripts/checks/bank.py` | Checks the rule bank (`evals/bank/`): every field, ids in order, one to three turns, a question that ends in "?", a source that resolves, and no run of six words of the bot's system prompt. |
| `scripts/checks/evals.py` | Checks the evaluation set (`evals/v1.json`): its shape and classes, that every passage and rule it names exists, that each rule's response matches the class and really fires, the counts, and the frozen hash. |
| `scripts/checks/library.py` | Checks the reference library's sources (`library/sources/`): every field, the licence allow-list, the hash against the original, a non-empty text. |
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

The fast loop needs nothing installed. The full gate, the chat and the live run need the virtual environment (the model client is in the lock; run them with `.venv/bin/python`):

```bash
python3.12 -m venv .venv && .venv/bin/pip install --only-binary :all: --require-hashes -r requirements.lock
```

## Running the demo on Windows

Clone the repository, then double-click `setup.cmd` in the clone (or run it in cmd.exe). It needs no admin rights and is safe to run again. It finds Python 3.12 (and offers to install it with winget if you answer Y), makes `.venv`, installs the locked packages, puts `bin` on your PATH, and asks for the Anthropic key (typed or pasted at a prompt) if none is set. Then open a new Command Prompt and type:

```
solarchat --demo
```

`solarchat --has-key` says whether a key is set without showing it. The key is stored in `%APPDATA%\solarchat\key`, outside the clone, and never printed or uploaded. Running `bin\solarchat.cmd` (that is, `solarchat`) before setup, or with a half-done install, runs `setup.cmd` for you and then your command; a chat with no key asks for it and stores it.

If `setup.cmd` cannot be used, the manual steps, from the clone in PowerShell:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\pip install --only-binary :all: --require-hashes -r requirements.lock
$env:Path = "$PWD\bin;$env:Path"   # this window only (cmd.exe: set PATH=%CD%\bin;%PATH%)
solarchat --key
solarchat --demo
```

On Linux and macOS the launcher is `bin/solarchat`, and the venv is made by hand (`python3.12 -m venv .venv && .venv/bin/pip install --only-binary :all: --require-hashes -r requirements.lock`).

`solarchat --demo` chats on the seed pack and reads each reply aloud by the system's own voice; add `--no-voice` (`solarchat --demo --no-voice`) for text only. `--voice` turns the voice on without `--demo`. The voice is the system's own (PowerShell's speech on Windows, `say` on macOS, `espeak` on Linux); the text is sent to the engine on its standard input, the citations are shown and not spoken, and with no engine the chat goes on in text. `solarchat --voices` lists the voices installed on the computer and `solarchat --voice-name "Microsoft Zira Desktop"` chooses one, kept beside the key (`--voice-name default` goes back to the system's own). The bot first asks two questions (your role, and what you are signed off for); `solarchat --demo --role qualified --signed-off battery` skips them.

## How a change is made

A change is saved on a working branch (`scripts/save.sh`), passes the fast checks (`scripts/gate.sh --fast`), is
committed through `scripts/commit.sh` and pushed with `scripts/ship.sh`. A function that carries out a decision
says so on the line above it, `# Decision: SC-005 (why)`, and `docs/DIRECTIVE-MAP.md` collects those citations. A
new module, a new dependency, or a change to a decision is the maintainer's call, recorded in `theGhost.md`.
