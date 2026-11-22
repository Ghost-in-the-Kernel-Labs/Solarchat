# Safety and compliance: how Hadley is kept to checked instructions

Solarchat's users are workers on solar sites, many of them new to the job (`docs/ROADMAP.md`, F-01). A wrong step
in an electrical installation can injure or kill someone. This document explains how Solarchat removes the part of
a language model's helpfulness that could do that (its readiness to guess, fill gaps, agree and carry on) and puts
in its place instruction sets that a person has checked, with their sources, and that the code holds to.

Each measure below names the rule that requires it (a decision in `theGhost.md` or an invariant in
`docs/CONTRACT.md`) and says plainly whether it is **enforced today** by code and tests, or **designed** and waiting
on a numbered item in `TODO.md` or `docs/ROADMAP.md`. Where the two differ, this document says so; it never
describes a planned safeguard as if it were running. `docs/DIRECTIVE-MAP.md` lists the functions that hold each rule.

## The danger: what an unchecked model does

A general-purpose model asked how to wire a panel will usually answer, because answering is what it is trained to
do. The ways that helpfulness can hurt a worker:

1. **It guesses.** Asked about a connector, a voltage or a model it has never seen, it produces a confident,
   plausible answer instead of saying it does not know.
2. **It fills gaps.** When a manual leaves a step out, it supplies one from general knowledge, which may be wrong
   for this equipment.
3. **It goes along.** When a worker says "I've already done that, what's next?", it moves on, even past a point
   where a careful person would stop.
4. **It obeys the text it reads.** A document fed to it can carry instructions ("skip the isolation check"), and
   it may follow them.
5. **It answers past its competence.** It will talk a worker through a live-circuit fault that should go to an
   engineer.
6. **It cannot show its source.** Its answer has no traceable origin, so nobody can check it afterwards.

## The answer: checked instructions instead of generated ones

### 1. The offline mode is the floor, and it uses no model

Everything that can be done without a network and without a model is built first and keeps working in every mode:
the packs, the troubleshooting flows, the procedures and the safety rules (`docs/ROADMAP.md`, P-15). In this mode
Hadley shows a pack's own checked text, word for word, one step at a time. It generates nothing, so there is
nothing for it to guess or fill in. The model, when one is added later, sits on top of this floor; the product
never depends on it to be safe.

- **Enforced today:** no test, check or gate calls a model: the model is called only by hand, through the `claude`
  answerer of the chat or `scripts/eval.py --live` (`test/test_eval.py` holds that no gate script names `--live`;
  every test uses a fake client). `test/test_modules.py` refuses an import of any model client (Anthropic, OpenAI,
  Google, Cohere, Mistral, Groq, LangChain and others) from any module that does not name it, and only `model` names
  one, `anthropic` (`docs/modules.json`, rule MOD-03, SC-021). The offline answerer `NoAnswer` always says "I do not
  know", and the chat's `--answerer stub` uses it.
- **Designed:** the offline mode as a floor that shows a pack's own text: the keyword search that finds a passage
  (`TODO.md` 1.7, 1.8), the walker that shows the steps (2.2) and the offline command-line conversation (2.4). Today
  the chat's default answerer is the model.

### 2. Hadley answers only from the packs, and only checked documentation is in a field pack (HAD-03, HAD-06, SC-005, SC-013)

The only knowledge Hadley may use is a **knowledge pack**: a folder of passages, troubleshooting flows and
procedures, each citing its sources. Only checked and approved documentation goes into a field pack, and handing it to
the person who loads the packs is that check and approval: no approval is recorded in the pack. A pack's manifest
has a `status`, `field` or `demo`. A `field` pack answers; a `demo` pack answers only in demo mode (section 8). No
model's reading ever approves anything (Core C-005, SC-005, SC-013).

- **Enforced today:** `solarchat/leaf/contract.py`'s `may_answer` says whether a pack may answer: a
  `field` pack always, a `demo` pack only in demo mode, any other status never; `test/test_leaf.py` shows the seed pack answers only in demo mode.
  `scripts/checks/packs.py` refuses a pack whose `status` is not `field` or `demo`, a `field` pack with a page
  marked unknown, a source with no licence written down, and a passage, flow or procedure that cites no source or a source the manifest does
  not list (`test/test_packs.py`, with a deliberately broken pack for each fault under
  `test/fixtures/broken/packs/`).
- **Enforced today:** `test/test_packs.py` runs the pack check over the seed pack, `packs/seed-mc4-leads/` (1.4, J-038).
  The door keeps only the packs `may_answer` allows (`solarchat/answer/door.py`, `test/test_door.py`), and the chat
  refuses a `demo` pack without `--demo` (`solarchat/project/chat.py`, `test/test_cli.py`).
- **Designed:** the same check over every pack in `packs/`, once there is a second pack.

### 3. Every answer names its source, or says "I do not know" (HAD-03)

A reply is one of exactly four things: an **answer**, which carries at least one reference to a passage
and says nothing that passage does not support; **"I do not know"**, which carries none; a **stop** (section 5), which
carries none; or a **warn** (section 5), which names its rule and the passage the walk continues with.
A question the switched-on packs do not cover gets "I do not know", never a guess. This removes dangers 1, 2 and 6.

- **Enforced today:** `solarchat/leaf/contract.py`'s `Reply` cannot be created as an answer without a passage
  reference, nor as a warn without one, nor as "I do not know" or a stop with one; `test/test_leaf.py` shows each refused.
- **Enforced today:** the door answers "I do not know" when the answerer cites nothing, a passage it was not given, a
  repeat or more than three, and attaches each cited passage's sources with the page (SC-012; `test/test_door.py`).
  The frozen evaluation set (1.5, `evals/v1.json`, its hash held by `scripts/checks/evals.py`) holds 35 in-scope
  questions, each naming the passage that answers it, and 25 that must get "I do not know"; `scripts/eval.py` scores a
  run on it (1.6). The offline stub scores 34 of 90, and the first live run on Haiku 5.5 scored 66 of 90 (J-051); that
  run is an observation, not a safeguard.
- **Designed:** keyword search that finds the right passage offline (1.7, 1.8).

### 4. A pack's text is data, never instructions (HAD-05, Core C-007)

Nothing inside a pack is ever treated as an instruction to Hadley. A passage that says "ignore the safety rules"
is shown or quoted as text, never obeyed. This removes danger 4.

- **Enforced today:** in the leaf, a `Passage` holds text only, to be quoted. With no model in the code, no pack
  text reaches anything that could act on it.
- **Enforced today:** three cases of the evaluation set (oos-13 to oos-15) put an instruction in the question and
  expect a refusal. No case plants an instruction inside a passage, and the door's `From:` lines and banner are not
  trusted back as input (`solarchat/project/chat.py` keeps only what the assistant said).
- **Designed:** a case that plants an instruction inside a pack's passage; the model's own system prompt is a
  nudge, never a guarantee (`docs/designs/rule-bank-and-triage.md`).

### 5. The safety rules sit outside every pack and override it (HAD-04, P-17)

The safety rules are Solarchat's own fixed text, kept in the `safety` module and never in a pack. They fire in every
mode. When one applies, Hadley gives the rule's response (SC-015): a warn shows the rule's words and the walk continues; a
stop or an emergency stops the current step and sends the worker to the site supervisor or engineer with the rule's words; the site's own safety procedures always come first. A pack may add more places to stop; it can
never remove, reword or switch off a rule. They are written for the least experienced person on a site (F-01). This
removes dangers 3 and 5: no "what's next?" carries a worker past a stop.

- **Enforced today:** every troubleshooting flow in a pack must end at a stop, the point where the worker goes to the
  supervisor or engineer; `scripts/checks/packs.py` refuses a flow without one, and a procedure step's stop, when
  present, must say something. A stop reply in the leaf must name the safety rule that fired. The safety rules,
  version 1, are data in the `safety` module (`solarchat/safety/rules.json`, fourteen rules, SR-01 the rule that the
  site's own safety procedures come first), loaded by `solarchat/safety/rules.py` as the leaf's `SafetyRule`, which
  refuses a rule with no words, triggers or source; `docs/SAFETY-RULES.md` is written from that data and a test keeps
  it current (`test/test_safety.py`). The pack check refuses a pack that names a rule by id or uses one of a short list
  of phrases telling the reader to ignore, skip, bypass, override or disregard a rule, a stop or the supervisor
  (`test/test_packs.py`, planted breaks under `test/fixtures/broken/packs/`); a paraphrase outside that list passes
  it and stays with the person who loads the packs.
- **Designed:** the maintainer's read of the rules (1.3 is done but for it; the points marked "Engineer to confirm"
  in `docs/SAFETY-RULES.md` are the agent's draft, and under F-16 they wait for an electrical engineer's
  final review at the end of the project); a rule firing on the worker's own words with no passage found (1.10), and
  every walk stopping at a rule whatever the pack says (2.3 in the walker). **Enforced today (J-063, SC-011):** the
  door applies a rule to the passages a reply cites: a cited passage whose text fires a rule gives that rule's response
  and words (a warn with the answer, a stop with what to bring the supervisor, an emergency with the rule's words alone),
  the most severe response first and then the lowest id, whatever the answerer said (`test/test_door.py`, step 6).
  **Enforced today (J-079, SC-011):** the door also applies the rules to the worker's own words, this turn's question only,
  before "I do not know" (so a stop or an emergency is given even when nothing is cited); SR-07, SR-08 and SR-09 read the
  worker's words only (`reads` in `rules.json`), never a passage's text; a warn fired by the words alone is the answer with the warn's words
  before it when a passage is cited, and otherwise an "I do not know" carrying the warn's words (`test/test_door_words.py`).
  **Not enforced today:** a pack's coverage of a rule (1.26); the evaluation set's warn and answer cases still score 0 on
  the offline stub, which cites no passage.
- **Enforced today (J-034):** each rule answers with a warn, a helpful stop or an emergency,
  starting cautious (SR-03 at a warn on Ghost's word) and relaxed on Ghost's word, logged as maintainer and confirmed or
  reversed by an electrical engineer at the final review (SC-015); each rule keeps a change log of who changed it, in
  what role, why and on what evidence (SC-016); `solarchat/safety/rules.py` refuses a rule with no entry, an entry
  missing a field, a response that is not warn, stop or emergency, and a rule changed since its latest entry (its
  fingerprint), shown by `test/test_safety.py`; the walker's use of the response is 1.12's; **designed:** the engineer's final review at the end of the project
  (TODO 6.4), from a generated review packet (TODO 1.14); nothing before it waits on the engineer.

### 6. The model gets no tools and no freedom (SC-002)

A model is called in exactly one module, with no tools and no connectors, so it cannot run code or reach anything.
Offline, a small local model may only choose which passage to show; it writes no instructions of its own.
Online, the model answers only from the passages it is given, names them, and says it does not know otherwise
(SC-005). Searching, indexing and every check call no model; no test calls one (replies are recorded); a run against
the live model is an evaluation run, started by hand and recorded.

- **Enforced today:** the import refusal in section 1; the Claude answerer (`solarchat/model/claude.py`) is built with
  no tools and no connectors, asks for a reply in a fixed schema, and the door, not the model, decides what may be
  cited (`test/test_claude.py`, a fake client). No model credential is committed: the key scan refuses one, and a key
  stored on a developer's own machine lives in the user's config folder outside any clone (SC-022 point 6,
  `test/test_key.py`).
- **Designed:** the offline small model, the hosted service and a worker's device holding no key at all (SC-022
  points 1 to 4), Phases 3 to 5 of `docs/ROADMAP.md`; sampling a rule bank to tune the bot (SC-023; 1.20 to 1.24).

### 7. Nothing that answers is built before the test that can catch a wrong answer (Core C-003, SC-003)

The evaluation set (in-scope questions with their passages, out-of-scope questions that must be refused, safety
cases that must stop) is written and frozen before any search exists. A change to the retrieval that lowers the
offline record is refused (`--demo --check`); a live run on the model writes no record and is not a ratchet (SC-023,
which amends SC-019's live ratchet). The walker built for the demo answers no question: it shows a
pack's steps in their order and stops where the pack and the safety rules stop (SC-010).

- **Enforced today:** the evaluation set and its check (1.5, `scripts/checks/evals.py`) and the offline record held
  per case (1.6, `test/test_eval.py`). The model answerer was brought forward ahead of search (1.16, Ghost's word),
  so this order does not hold for it: its first live run is an observation, not a gate.
- **Designed:** a threshold on the model's scores, set by Ghost after a baseline (roadmap 3.4).

### 8. A demo is labelled as one (SC-010)

For a demonstration only, a switch may run a `demo` pack. Every screen shown under it carries the
banner **"DEMO: not reviewed by an engineer, do not use on a site"**, and without the switch such a pack is refused.

- **Enforced today:** the door puts the banner on every reply in demo mode, the chat shows it at the start, and a `demo`
  pack without `--demo` is refused (`test/test_door.py`, `test/test_cli.py`). **Designed:** 2.1, the demo switch as its
  own item, for every screen. The demo pack `packs/seed-mc4-leads/` is a `demo` pack, and `docs/HANDOFF.md` lists five of its
  claims that could not be sourced; they must be checked by an engineer before it goes into a field pack.

## What Solarchat does not claim

- It is not a substitute for training, certification, the equipment maker's instructions or the site's own safety
  procedures, which always come first.
- A pack is only as good as the documentation handed over. The format and the check prove a pack is complete and
  traceable; whether its text is true is the judgement of the person who loads the packs.
- Today no worker is served by it: the chat runs only on a developer's machine, with a demo pack and a key, and the
  safety rules are applied only to the passages an answer cites, not yet to the worker's own words. The safeguards marked "designed" above are not yet running.

## Where each rule lives

| Rule | Where it is written | Where it is held |
| --- | --- | --- |
| Answers only from the packs, with its source | `docs/CONTRACT.md` HAD-03, HAD-06; `theGhost.md` SC-005 | `solarchat/leaf/contract.py`, `scripts/checks/packs.py`, `test/test_leaf.py`, `test/test_packs.py` |
| A pack's text is data | HAD-05; Core C-007 | `solarchat/leaf/contract.py` (`Passage`) |
| Safety rules outside every pack | HAD-04; `docs/ROADMAP.md` P-17 | `scripts/checks/packs.py` (`flow_problems`), the `safety` module's rules (1.3); applied to the cited passages of an answer in 1.9 (`solarchat/answer/door.py`, `test/test_door.py`) |
| A model only in one module, with no tool; no model key in the repository | SC-002, SC-021, SC-022; `docs/modules.json` MOD-03 | `test/test_modules.py`, `scripts/checks/secrets.py`, `test/test_key.py` |
| The test before the thing it tests | Core C-003; SC-003 | `TODO.md` order; the evaluation set (1.5) and the runner (1.6) |
| A demo is labelled | SC-010 | `solarchat/answer/door.py` (`with_banner`), `solarchat/project/chat.py`; the demo switch's own item is 2.1 |
