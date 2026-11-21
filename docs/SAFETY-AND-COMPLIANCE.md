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

- **Enforced today:** no language model is called anywhere in the code. `test/test_modules.py` refuses an import of
  any model client (Anthropic, OpenAI, Google, Cohere, Mistral, Groq, LangChain and others) from any module that
  does not name it, and no module names one (`docs/modules.json`, rule MOD-03).
- **Designed:** the walker that shows the steps (`TODO.md` 1.6) and the offline command-line conversation (1.8).

### 2. Hadley answers only from the packs, and only checked documentation is in the library (HAD-03, HAD-06, SC-005, SC-013)

The only knowledge Hadley may use is a **knowledge pack**: a folder of passages, troubleshooting flows and
procedures, each citing its sources. Only checked and approved documentation goes into the library, and handing it to
the person who loads the library data is that check and approval: no approval is recorded in the pack. A pack's manifest
has a `status`, `library` or `demo`. A `library` pack answers; a `demo` pack answers only in demo mode (section 8). No
model's reading ever approves anything (Core C-005, SC-005, SC-013).

- **Enforced today:** `solarchat/leaf/contract.py`'s `may_answer` says whether a pack may answer: a
  `library` pack always, a `demo` pack only in demo mode, any other status never; `test/test_leaf.py` shows the seed pack answers only in demo mode.
  `scripts/checks/packs.py` refuses a pack whose `status` is not `library` or `demo`, a `library` pack with a page
  marked unknown, a source with no licence written down, and a passage, flow or procedure that cites no source or a source the manifest does
  not list (`test/test_packs.py`, with a deliberately broken pack for each fault under
  `test/fixtures/broken/packs/`).
- **Designed:** the pack check run over every pack in `packs/` once the demo pack is converted (1.4).

### 3. Every answer names its source, or says "I do not know" (HAD-03)

A reply is one of exactly three things: an **answer**, which carries at least one reference to a passage
and says nothing that passage does not support; **"I do not know"**, which carries none; or a **stop** (section 5).
A question the switched-on packs do not cover gets "I do not know", never a guess. This removes dangers 1, 2 and 6.

- **Enforced today:** `solarchat/leaf/contract.py`'s `Reply` cannot be created as an answer without a passage
  reference, nor as "I do not know" or a stop with one; `test/test_leaf.py` shows each refused.
- **Designed:** the frozen evaluation set (1.9) of in-scope questions, each with the passage that answers it, and
  out-of-scope questions that must get "I do not know".

### 4. A pack's text is data, never instructions (HAD-05, Core C-007)

Nothing inside a pack is ever treated as an instruction to Hadley. A passage that says "ignore the safety rules"
is shown or quoted as text, never obeyed. This removes danger 4.

- **Enforced today:** in the leaf, a `Passage` holds text only, to be quoted. With no model in the code, no pack
  text reaches anything that could act on it.
- **Designed:** injection cases in the evaluation set (1.9), before any model is added.

### 5. The safety rules sit outside every pack and override it (HAD-04, P-17)

The safety rules are Solarchat's own fixed text, kept in the `safety` module and never in a pack. They fire in every
mode. When one applies, Hadley stops the current step and sends the worker to the site supervisor or engineer with
the rule's words; the site's own safety procedures always come first. A pack may add more places to stop; it can
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
  it and stays with the person who loads the library.
- **Designed:** the maintainer's read of the rules (1.3 stays open until then; the points marked "Ghost to confirm"
  in `docs/SAFETY-RULES.md` are the agent's draft, and under F-16, proposed, they are an electrical engineer's to
  confirm); every walk stopping at a rule whatever the pack says, using each rule's triggers (1.7).
- **Proposed, not decided:** each rule answers with a warn, a helpful stop or an emergency, starting cautious and
  relaxed only by an electrical engineer (SC-015); each rule keeps a change log of who changed it, in what role, why
  and on what evidence (SC-016); the engineer's review before the evaluation set is frozen (TODO 1.14).

### 6. When a model is added, it gets no tools and no freedom (SC-002)

A model is called in exactly one module, with no tools and no connectors, so it cannot run code or reach anything.
Offline, a small local model may only choose which passage to show; it writes no instructions of its own.
Online, the model answers only from the passages it is given, names them, and says it does not know otherwise
(SC-005). Searching, indexing and every check call no model; no test calls one (replies are recorded); a run against
the live model is an evaluation run, started by hand and recorded.

- **Enforced today:** the import refusal in section 1.
- **Designed:** Phases 3 and 4 of `docs/ROADMAP.md`, and only after the evaluation set is frozen.

### 7. Nothing that answers is built before the test that can catch a wrong answer (Core C-003, SC-003)

The evaluation set (in-scope questions with their passages, out-of-scope questions that must be refused, safety
cases that must stop) is written and frozen before any search or model exists. A change to a prompt, the retrieval
or the model that lowers a recorded score is refused. The walker built for the demo answers no question: it shows a
pack's steps in their order and stops where the pack and the safety rules stop (SC-010).

- **Enforced today:** the order is held in `TODO.md` (search and models come after 1.9).
- **Designed:** the evaluation set and its check (1.9).

### 8. A demo is labelled as one (SC-010)

For a demonstration only, a switch may run a `demo` pack. Every screen shown under it carries the
banner **"DEMO: not reviewed by an engineer, do not use on a site"**, and without the switch such a pack is refused.

- **Designed:** 1.5. The demo pack `packs/seed-mc4-leads/` is a `demo` pack, and `docs/HANDOFF.md` lists five of its
  claims that could not be sourced; they must be checked by an engineer before it goes into the library.

## What Solarchat does not claim

- It is not a substitute for training, certification, the equipment maker's instructions or the site's own safety
  procedures, which always come first.
- A pack is only as good as the documentation handed over. The format and the check prove a pack is complete and
  traceable; whether its text is true is the judgement of the person who loads the library.
- Today nothing in the repository answers a worker. The safeguards marked "designed" above are not yet running.

## Where each rule lives

| Rule | Where it is written | Where it is held |
| --- | --- | --- |
| Answers only from the packs, with its source | `docs/CONTRACT.md` HAD-03, HAD-06; `theGhost.md` SC-005 | `solarchat/leaf/contract.py`, `scripts/checks/packs.py`, `test/test_leaf.py`, `test/test_packs.py` |
| A pack's text is data | HAD-05; Core C-007 | `solarchat/leaf/contract.py` (`Passage`) |
| Safety rules outside every pack | HAD-04; `docs/ROADMAP.md` P-17 | `scripts/checks/packs.py` (`flow_problems`), the `safety` module (1.3) |
| No model in the code; one door when there is | SC-002; `docs/modules.json` MOD-03 | `test/test_modules.py` |
| The test before the thing it tests | Core C-003; SC-003 | `TODO.md` order; the evaluation set (1.9) |
| A demo is labelled | SC-010 | the demo switch and its test (1.5) |
