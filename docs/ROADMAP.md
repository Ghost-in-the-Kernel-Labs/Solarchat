# Roadmap: the plan, not the decision log

A plan, in phases. Each phase's steps are items with a check that fails before the work and passes
after; each phase ends with a numbered tune-up pass (C-024). When a phase is built, its section
shrinks to a ten-line header and the decisions it produced live in `theGhost.md`. `TODO.md` is this
plan as a chain: the open items, in order, with the checks copied; `docs/DONE.md` is what is
finished.

## 1. The product in three sentences

Solarchat walks a person installing solar panels on a site through setting them up and finding what is wrong,
on their phone, where the panels are, answering only from knowledge packs (manuals and troubleshooting guides) that can be
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
- **P-11 The agent's environment is a first-class deliverable**, funded at one commit in twenty-five (C-022, C-024, SC-009).
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
- **P-19 Online first, offline always.** At run time the conversation uses the Anthropic model whenever there
  is a connection, and drops to the offline floor only when there is none; the floor is built first (P-15) so
  that the drop is never a dead end (F-10).
- **P-18 Written for a phone and a tired person.** One step at a time, short, in plain words, and the
  conversation can be picked up where it stopped (F-03).


## 3. Settled facts

| Id | Fact | Source | Implication |
| --- | --- | --- | --- |
| F-01 | The users are a mix of people installing on sites for the deploying company: contractors new to the job, the company's own crews, and outside employees installing on its behalf. They are workers, not homeowners (corrected by Ghost, J-013; the first reading, a rural homeowner, was the agent's). | Ghost, 2026-11-20, in chat (J-013) | The safety rules and the wording are for the newest contractor on a site (P-17, P-18); a stop sends the worker to the site supervisor or engineer, and the site's own safety procedures always come first. |
| F-02 | Many of them call an engineer for things as simple as connecting a panel correctly; engineers are short, the backlog grows and the reviews turn bad. | Ghost, 2026-11-20, in chat | The first pack and the first evaluation questions are the simple setup faults, not the rare ones. |
| F-03 | They are outside on remote sites, on a phone, with a poor signal; they stop and give up, or wait for an engineer. | Ghost, 2026-11-20, in chat | Offline first (P-15); a conversation resumes where it stopped (P-18). |
| F-04 | The bot must run no code and know nothing outside its packs. | Ghost, 2026-11-20, in chat | The model gets no tools (SC-002); out-of-scope questions are refused and are a third of the evaluation set. |
| F-05 | Knowledge libraries are swapped in and out, starting from public material. | Ghost, 2026-11-20, in chat | The pack format comes first; a manufacturer's manual is loaded where the bot is deployed, never committed (SC-005, Core C-033). |
| F-07 | The online model is Claude Sonnet through the Anthropic API, chosen over Haiku for its reasoning; the customer can show it a photo, and it asks for the make and model and says where to find them when it cannot tell. | Ghost, 2026-11-20, in chat | 3.1 is settled for the online side; a photo is evidence the bot states back and the customer confirms (Core C-005); Sonnet against Haiku is measured on the evaluation set, not argued (Core C-004). |
| F-08 | The customer should be able to speak and be spoken to, hands busy with the panel. | Ghost, 2026-11-20, in chat | Speech is the phone's own, around the text conversation (Phase 5); it is not a model feature the kernel depends on. |
| F-09 | Offline, Ghost wants a very light open model downloaded ahead of time inside an app that ships with the online version built in. | Ghost, 2026-11-20, in chat | Phase 5 is an app; whether a small model may write an answer, or only choose which admitted passage and flow to show, is settled by a trial against the safety and refusal cases (5.1, Core C-004). The model's weights are downloaded, never committed (Core C-033). |
| F-10 | Offline, a small model only chooses: it works out what the customer asks and picks the admitted passage and flow, and the words shown are the pack's. It is the worst-case backup; whenever there is a connection the Anthropic model is used. | Ghost, 2026-11-20, in chat (J-008) | Online first at run time (P-19); 5.1 no longer chooses among rivals, it tests that the choosing model passes the safety and refusal cases, with no model as the fallback if it does not. |
| F-11 | The product is reached through both a phone app and a website. | Ghost, 2026-11-20, in chat (J-008) | The hosted mode serves both (4.5, Phase 5); one client that is both a website and an installable app is a candidate for 5.1. |
| F-12 | The assistant has a voice and a manner of its own: British, clean and clinical, dry humour at times; its own name, no existing character's name, and no imitation of a particular actor's voice. | Ghost, 2026-11-20, in chat (J-009) | The manner is the framing around an answer, never its substance: a safety stop is said plainly with no humour (P-17), and the evaluation set checks that the manner changes no instruction. Offline the voice is the phone's own British voice. The name is Ghost's to choose. |
| F-13 | The assistant's name is Hadley. | Ghost, 2026-11-20, in chat (J-010) | Used in the manner (3.5) and the clients; a trademark search before it reaches an app store. |
| F-14 | The model has no connectors (a photo is read by the model directly). A pack holds, by installation type, the failures commonly met, the correct installation steps, and a picture for each step of what right looks like; the assistant shows the pictures step by step. | Ghost, 2026-11-20, in chat (J-011) | The pack format (1.2) carries a picture per step and failures grouped by type; pictures in the repository are the project's own drawings or openly licensed, never copied (Core C-033); a place where a real photograph is wanted is listed for a person to supply. |
| F-15 | The libraries built here are demos. The finished libraries are made by the company that deploys the product. | Ghost, 2026-11-20, in chat (J-012) | A demo pack may carry web pictures with their provenance (SC-007); the pack format and its admission check (1.2) are what the deploying company builds to, so they matter more than the demo's content. |
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
- 1.3 The safety rules, version 1, for the newest contractor on a site (F-01): the points at which every mode
  stops and sends the worker to the site supervisor or engineer, and the rule that the site's own safety
  procedures come first; held outside every pack.
- 1.4 The seed pack: one small pack built from public sources, each named with its licence, in the project's own
  words and its own drawings, covering the simple setup faults of F-02 for one installation type: the correct
  steps, each with a picture, and the common failures (F-14). Ghost asked for a first draft ahead of 1.2 (J-011):
  it is built to a provisional layout under `packs/`, marked not admitted, and is brought to 1.2's format and
  admitted by a person before the item closes.
- 1.5 Demo mode: a labelled switch that lets a pack that is not admitted run, for a demo only (SC-010).
- 1.6 The walker, moved from 2.3 for the demo of 2026-11-23 (SC-010): one step at a time through a procedure or
  a flow, to a fix or a stop.
- 1.7 The safety rules enforced in the walker, moved from 2.4's walker half (SC-010).
- 1.8 The offline shell, moved from 2.6 (SC-010): a command-line conversation that runs end to end with the
  network off.
- 1.9 The evaluation set, version 1, frozen: in-scope questions with the passage that answers each,
  out-of-scope questions that must be refused, and safety cases that must stop. It still comes before any
  search or model (Core C-003): the walker answers no question.
- 1.10 Tune-up pass 1, with the human maintainability pass (SC-011)

### Phase 2: the offline mode (the floor)

- 2.1 Ingestion: a pack on disk becomes an index, the same bytes every time (goldens, SC-003).
- 2.2 Search: keyword ranking in the standard library, scored against 1.9's in-scope questions.
- 2.3 (moved to 1.6, SC-010)
- 2.4 The safety rules enforced in the search (the walker's half moved to 1.7, SC-010).
- 2.5 Switching packs on and off, and two packs for different models side by side.
- 2.6 (moved to 1.8, SC-010)
- 2.7 Tune-up pass 2

### Phase 3: the local mode (a model on top)

- 3.1 The model door: one module, the only one that imports a model client (a dependency proposed to Ghost;
  Core C-012, SC-002). The online model is Claude Sonnet through the Anthropic API (F-07); it is given no tools
  and no connectors.
- 3.2 The answering step: the found passages and the question in, an answer that cites its passage or says it
  does not know out; no tools.
- 3.3 Tests against recorded replies; no test calls a model.
- 3.4 The evaluation run, by hand, its scores recorded; the refusal and safety thresholds set by Ghost.
- 3.5 The manner (F-12): written once beside the prompt, with evaluation cases that the same question gets the
  same steps with and without it, and that a safety stop carries no humour.
- 3.6 A photo in the conversation: the bot says what it reads (the label, the connectors), the customer confirms,
  and only then does it act on it; when it cannot tell, it asks for the make and model and says where the label is.
- 3.7 Sonnet against Haiku on the evaluation set, cost beside score.
- 3.8 When the model cannot be reached, the conversation falls to the offline mode and says so.
- 3.9 Tune-up pass 3

### Phase 4: the hosted mode (a service behind an API)

- 4.1 The API's contract: start a conversation, send a message, resume one.
- 4.2 The service, and what it keeps of a conversation and for how long.
- 4.3 Pack administration: which packs a deployment has on, and their versions.
- 4.4 Limits against abuse, and a hostile-input test set (Core C-007).
- 4.5 The website: a page that holds the conversation against the API, photos included (F-11).
- 4.6 Tune-up pass 4

### Phase 5: the phone

The customer of F-03 is on a phone outside. This phase decides how the offline mode reaches that phone; the
likeliest form is a page the phone keeps, with the packs and flows stored on it, which is a second language
stack and so Ghost's decision before any of it is built.

- 5.1 The decision: the app's stack (F-11: a website and a phone app), and the trial of the small on-device model
  in the role Ghost gave it (F-10: it only chooses the passage and flow): the same safety and refusal cases as
  the online model, the pass condition written first; if it fails, offline runs with no model.
- 5.2 The phone shell: packs and flows stored on the phone; the model used when there is signal.
- 5.3 A conversation resumes where it stopped, outside or back indoors.
- 5.4 Speech in and out, by the phone's own recognition and voice (F-08), in the assistant's manner (F-12); a
  richer voice from a speech service is a dependency proposed to Ghost, online only, from a licensed stock voice.
- 5.5 Tune-up pass 5

### Phase 6: real packs and the engineer

- 6.1 Reading a manufacturer's manual into a pack (a document reader, a dependency proposed to Ghost), loaded
  at deployment.
- 6.2 The first real make and model. Waits on Ghost: which.
- 6.3 The handover: when the bot stops, a summary for the engineer of what was tried and seen.
- 6.4 A pilot, with an engineer reading the answers (Core C-005).
- 6.5 Tune-up pass 6
