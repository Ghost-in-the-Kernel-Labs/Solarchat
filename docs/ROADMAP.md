# Roadmap: the plan, not the decision log

A plan, in phases. Each phase's steps are items with a check that fails before the work and passes
after; each phase ends with a numbered tune-up pass (C-024). When a phase is built, its section
shrinks to a ten-line header and the decisions it produced live in `theGhost.md`. `TODO.md` is this
plan as a chain: the open items, in order, with the checks copied; `docs/DONE.md` is what is
finished.

## 1. The product in three sentences

Solarchat walks a person who has bought a solar panel through setting it up and finding what is wrong, on
their phone, where the panel is, answering only from knowledge packs (manuals and troubleshooting guides) that can be
switched in and out. It runs in three modes on one kernel: offline (no network, no model), local (on one's own
machine) and hosted (a service behind an API). The thesis to hold: the knowledge already exists, and the product is
the path from it to the person at the minute they need it; the thesis to refuse: a clever general assistant that
happens to know about solar.

## 2. Principles

The core's principles, copied from Ghost-Core when this project was stamped; add this project's own below them.

- **P-01 The check before the thing it checks.** Every document arrives with its check and the
  check's planted break, in the same commit (C-003, C-013).
- **P-02 A refactor changes no result.** Every test green before and after, every generated file
  identical (C-017).
- **P-03 Findings before claims.** What a check proves about a parent or a practice is a row in
  `docs/FINDINGS.md` before it is a sentence anywhere else (C-014).
- **P-04 One shape until proven.** One check framework, one test runner, one fast loop; a second
  arrives when the first has failed a stated test (C-002).
- **P-05 Numbered decisions, test-checked supersession** (C-008).
- **P-06 Plans shrink into decisions.** A built phase becomes a ten-line header.
- **P-07 The routing table is the front door** (C-020, C-021).
- **P-08 One canonical word per concept, from the first file** (C-011).
- **P-09 Ratchets only where there is debt** (C-023).
- **P-10 Proven by a run, not on paper.** "Done" never means "on paper" (C-004).
- **P-11 The agent's environment is a first-class deliverable**, funded at one commit in eight (C-022, C-024).
- **P-12 Cloud-primary.** Nothing requires the maintainer's own machine (AGT-01).
- **P-13 CI minutes are spent by hand** (C-032).
- **P-14 Core checks run with nothing installed.** Python 3 standard library, `-I` (C-022).

Solarchat's own:

- **P-15 The offline mode is the floor.** Everything that can be done with no network and no model is built
  first and keeps working in every mode: the packs, the search, the troubleshooting flows, the safety rules.
  The model is added on top and the product never depends on it to be safe or useful (F-02, F-03, SC-002).
- **P-16 An answer is a passage with a source, or it is "I do not know"** (SC-005).
- **P-17 The safety rules are not knowledge.** They sit outside every pack, fire in every mode, and are
  written for the least experienced reader (F-01, SC-005).
- **P-18 Written for a phone and a tired person.** One step at a time, short, in plain words, and the
  conversation can be picked up where it stopped (F-03).


## 3. Settled facts

| Id | Fact | Source | Implication |
| --- | --- | --- | --- |
| F-01 | The customers are people in rural areas who bought a panel and are setting it up themselves; they are not installers. | Ghost, 2026-11-20, in chat | The safety rules and the wording are for a homeowner (P-17, P-18). |
| F-02 | Many of them call an engineer for things as simple as plugging the panel in correctly; engineers are short, the backlog grows and the reviews turn bad. | Ghost, 2026-11-20, in chat | The first pack and the first evaluation questions are the simple setup faults, not the rare ones. |
| F-03 | They are outside, on a phone, with a poor signal; they come back inside and give up. | Ghost, 2026-11-20, in chat | Offline first (P-15); a conversation resumes where it stopped (P-18). |
| F-04 | The bot must run no code and know nothing outside its packs. | Ghost, 2026-11-20, in chat | The model gets no tools (SC-002); out-of-scope questions are refused and are a third of the evaluation set. |
| F-05 | Knowledge libraries are swapped in and out, starting from public material. | Ghost, 2026-11-20, in chat | The pack format comes first; a manufacturer's manual is loaded where the bot is deployed, never committed (SC-005, Core C-033). |
| F-06 | Three modes are wanted: hosted behind an API, local, and offline. | Ghost, 2026-11-20, in chat | One kernel, three shells (P-15); the phases below. |

## 4. What is deliberately not built

- **Tools for the model, or any code execution** (F-04, SC-002).
- **General knowledge.** No question outside the switched-on packs is answered, however easy.
- **System design advice**: sizing, choosing equipment, grid-connection paperwork, or any electrical work a
  manual reserves for a licensed person. The bot says who to call.
- **A trained or fine-tuned model.** Knowledge changes by switching packs, never by training.
- **A vector database or embeddings**, until the evaluation set shows keyword search failing on real questions
  (Core C-002).
- **Manufacturers' manuals in the repository** (Core C-033).
- **A store of customers' conversations in the repository**, or any kept longer than the conversation needs.
- **A second language stack**, until Phase 5's decision.

## 5. The meta-architecture

The core's table, copied from Ghost-Core when this project was stamped; add this project's contract and modules.

| Document | What it holds | Test |
| --- | --- | --- |
| `CLAUDE.md` | the routing table, the when list, the binding rules | `test/test_claude_md.py` (words, rows, pointers) |
| `theGhost.md` | the decisions | `test/test_ghost.py` |
| `docs/GLOSSARY.md` | the words | `test/test_glossary.py` |
| `docs/journal/` | what happened | `test/test_journal.py` |
| `TODO.md`, `docs/DONE.md`, this file | the plan as a chain | `test/test_todo.py` |
| `docs/HANDOFF.md` | what waits on whom | `test/test_journal.py` (open conflicts), `test/test_registers.py` (raised escalations) |
| `docs/FINDINGS.md`, `docs/ESCALATIONS.md` | the registers | `test/test_registers.py` |
| `docs/NAVIGATION-LOG.md` | the debriefs and the last review | `test/test_navigation.py` |
| `docs/AGENT.md` | the environment contract and the metrics | `test/test_metrics.py` |
| `docs/CONTRACT.md`, `docs/modules.json` | the kernel contract and the import graph | `test/test_contract.py`, `test/test_modules.py` |
| `docs/when/*.md`, `docs/paths/*.md` | what to do in a situation; a workpath's rows | `test/test_pointers.py` |
| `docs/SUPPLY-CHAIN.md` | the baseline and where this repository stands | `test/test_supply_chain.py` |


## 6. Phases

### Phase 0: founding

- 0.1 this project's ghost, named (a `--docs-only` commit: the gate refuses at the stack until 0.2)
- 0.2 the stack wired, so the gate can pass and the first gated commit lands
- 0.3 the roadmap and TODO filled: §1 to §6 and Phase 1's items
- 0.4 the contract and the leaf module
- 0.5 the founding decisions, Ghost's (agents cannot author Ghost's decisions; a builder that reports "waiting on Ghost" has done its job)
- 0.6 Tune-up pass 0

### Phase 1: the pack and the oracle (no model, no product code that answers)

What a wrong answer is has to be written down before anything can give one (Core C-003).

- 1.1 The words: pack, passage, flow, mode, admitted, safety rule, in `docs/GLOSSARY.md`.
- 1.2 The pack format, as the contract: a manifest (make, model, version, source, licence, who admitted it and
  when), passages, and flows (symptom, check, fix, and where to stop); a check that refuses a broken pack.
- 1.3 The safety rules, version 1, for a homeowner: the points at which every mode stops and says to call an
  engineer; held outside every pack.
- 1.4 The seed pack: one small pack built by hand from material whose licence allows redistribution, covering
  the simple setup faults of F-02.
- 1.5 The evaluation set, version 1, frozen: in-scope questions with the passage that answers each,
  out-of-scope questions that must be refused, and safety cases that must stop.
- 1.6 Tune-up pass 1

### Phase 2: the offline mode (the floor)

- 2.1 Ingestion: a pack on disk becomes an index, the same bytes every time (goldens, SC-003).
- 2.2 Search: keyword ranking in the standard library, scored against 1.5's in-scope questions.
- 2.3 The flow walker: one step at a time, from a symptom to a fix or a stop.
- 2.4 The safety rules enforced in the walker and the search.
- 2.5 Switching packs on and off, and two packs for different models side by side.
- 2.6 The offline shell: a command-line conversation that runs end to end with the network off.
- 2.7 Tune-up pass 2

### Phase 3: the local mode (a model on top)

- 3.1 The model door: one module, the only one that imports a model client (a dependency proposed to Ghost;
  Core C-012, SC-002). Open for Ghost: a hosted model reached with a key, a model on the machine, or both.
- 3.2 The answering step: the found passages and the question in, an answer that cites its passage or says it
  does not know out; no tools.
- 3.3 Tests against recorded replies; no test calls a model.
- 3.4 The evaluation run, by hand, its scores recorded; the refusal and safety thresholds set by Ghost.
- 3.5 When the model cannot be reached, the conversation falls to the offline mode and says so.
- 3.6 Tune-up pass 3

### Phase 4: the hosted mode (a service behind an API)

- 4.1 The API's contract: start a conversation, send a message, resume one.
- 4.2 The service, and what it keeps of a conversation and for how long.
- 4.3 Pack administration: which packs a deployment has on, and their versions.
- 4.4 Limits against abuse, and a hostile-input test set (Core C-007).
- 4.5 Tune-up pass 4

### Phase 5: the phone

The customer of F-03 is on a phone outside. This phase decides how the offline mode reaches that phone; the
likeliest form is a page the phone keeps, with the packs and flows stored on it, which is a second language
stack and so Ghost's decision before any of it is built.

- 5.1 The decision: how the offline mode runs on a phone.
- 5.2 The phone shell: packs and flows stored on the phone; the model used when there is signal.
- 5.3 A conversation resumes where it stopped, outside or back indoors.
- 5.4 Tune-up pass 5

### Phase 6: real packs and the engineer

- 6.1 Reading a manufacturer's manual into a pack (a document reader, a dependency proposed to Ghost), loaded
  at deployment.
- 6.2 The first real make and model. Waits on Ghost: which.
- 6.3 The handover: when the bot stops, a summary for the engineer of what was tried and seen.
- 6.4 A pilot, with an engineer reading the answers (Core C-005).
- 6.5 Tune-up pass 6
