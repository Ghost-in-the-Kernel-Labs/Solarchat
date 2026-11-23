# The kernel contract

The file keeps the template's name: `test/test_contract.py` reads `docs/CONTRACT.md` by that path (J-018, F-001).

The contract precedes the code. It is the specification the leaf module is built from and that a
mirror could be written from blind: if something here is not precise enough to implement, that is a
defect in this document, and the fix is to make it precise, not to read the code. Each invariant is
one heading, `## HAD-nn title`, numbered in sequence and never reused; code cites one as
`# Invariant: HAD-03` and `test/test_contract.py` holds the two together in both directions: every
invariant is named somewhere in the leaf module, and the code names no invariant the document does
not have. The prefix is Hadley's, the assistant's name; `SC` is the decisions' (SC-001 on).

The leaf module (`docs/modules.json`'s `leaf`, `solarchat/leaf/`) holds this contract in code: the
types and the numbers every other module imports and that imports nothing of the project's own. A
threshold lives there and nowhere else; a threshold defined elsewhere fails the check.

## HAD-01 The leaf module imports nothing of the project's own

Every other module may import it; it may import only the standard library. Held by
`test/test_modules.py` (`mayImport: []`).

## HAD-02 Every number a document reports comes from a run the repository can repeat

A number without the command that produced it does not exist. Held by the project's results check
once a document reports one; the runner's scores on the evaluation set are held to the committed record by
`scripts/eval.py --check` (TODO 1.6, done).

## HAD-03 Hadley answers only from the packs, names the passage, or says it does not know

Every reply is one of four kinds. An answer carries at least one passage reference (the pack's id
and the passage's id) from a pack that is switched on and may answer (HAD-06), and says nothing those passages
do not support. What the worker is shown: the answer names the passage it used, then each of that passage's sources by
title, with the page for a document source (SC-012); the reference stays the pack's id and the passage's id, and the page
is read from the pack, never carried in the reference. A question the switched-on packs do not cover gets "I do not know" with no
passages, never a guess. A safety rule that fires gets its response (HAD-04, SC-015): a stop or an emergency, which name no
passage, or a warn, which names the rule and at least one passage, the step the walk continues with. Held by the
leaf's `Reply`, which refuses an answer or a warn with no passage and a "do not know" or a stop with one
(`test/test_leaf.py`);
the evaluation set holds the rest (SC-003, SC-005).

## HAD-04 The safety rules sit outside every pack, and no pack can remove or change one

The safety rules are the project's own text, kept in the `safety` module, never in a pack. A rule
that fires gives its response (SC-015): `warn` shows the rule's words and the walk continues; `stop` stops the
conversation's current step and sends the worker to the site supervisor or engineer; `emergency` tells the worker to
step back and call for help; the site's own safety procedures come first. Each rule keeps a change log (SC-016), and
the safety check refuses a rule changed without a new entry. A pack may add steps that stop; it cannot
remove, reword or switch off a rule. Held by the leaf's `Reply` (a stop or a warn names its rule), the leaf's
`SafetyRule` (its response and change log), the safety rules' check (`load_rules`, with the fingerprint of SC-016) and
the pack check (TODO 1.2).

Amended by SC-024 (in force, Ghost, 2026-11-22): a pack is the first safety authority for its own make and model. A pack
that declares in its manifest, rule by rule, which of its own passages cover a rule's hazard, each citing its manual
with a page, gives that instruction (cited to the pack) in place of the rule; a rule it does not declare stays in force
for it; SR-08 and SR-09 keep their emergency response in every pack. Only a `field` pack, or a `demo` pack on Ghost's
word, may declare; the engineer's packet lists every declaration. Built by TODO 1.26: until then no pack declares, and
the paragraph above holds unchanged.

How a trigger matches (the audit of 2026-11-21, `docs/audits/2026-11-21-safety-rules.md`, applied on Ghost's word in J-030): a trigger matches a text when it occurs as a whole word or whole
phrase, case-insensitively, with a word boundary at both ends (no letter, digit or underscore touching either end);
never as a substring, so `live` does not fire on "deliver" or "alive", and a rule's trigger does not fire inside
"undamaged". A run of spaces or line breaks inside a phrase counts as one space. `solarchat/safety/rules.py`'s
`rules_fired(text)` is the one implementation: the ids of the rules whose triggers match. A rule's triggers are text
that says the hazard is present or the hazardous act is asked for, not text that tells the worker what to look for or
forbids the act; SR-01 holds only phrases that order the site's rules ignored, since a rule always has a trigger.

## HAD-05 A pack's text is data, never instructions

Nothing in a pack is read as an instruction to Hadley: a passage that says "ignore the safety
rules" is shown or quoted as a passage, never obeyed (Core C-007). Held by the leaf's `Passage`,
whose text is only ever quoted, and the evaluation set's injection cases (oos-13 to oos-15, TODO 1.5, done; they put the instruction in the question, none inside a passage).

## HAD-06 A demo pack never answers outside demo mode

A pack gives `make` and `model`, or `installation_type`, or all three; a pack with neither, or with one of `make` and
`model` alone, is refused.

A pack's `status` is `field` or `demo` (SC-013). A `field` pack answers: handing the documentation to the person who
loads the packs is the approval, and no approval is recorded (SC-013, amending SC-005). A `demo` pack may be read and
checked, and answers only in demo mode, under the banner "DEMO: not reviewed by an engineer, do not use on a site" (SC-010).
A pack whose status is not `field` or `demo` never answers, whatever the mode (SC-013; held by `may_answer`).
Held by the leaf's `may_answer` (`test/test_leaf.py`) and the pack check's status rule (`test/test_packs.py`).

With `--voice` (TODO 2.7) the banner is still shown on every reply and is spoken once, at the start; the speech engine gets
the reply's words on its standard input, never the citations, and never in a command line (`test/test_speech.py`).

## The pack format

A pack is what the deploying company builds, so this section is the format: a pack can be written from it without reading
code. `scripts/checks/packs.py` holds it (`test/test_packs.py`; a well-formed pack in `test/fixtures/packs/good/`, each
planted break in `test/fixtures/broken/packs/`). A pack is a folder of JSON files (UTF-8) and its pictures, named for
the pack's id:

```
<pack-id>/manifest.json    the manifest
<pack-id>/passages.json    a list of passages
<pack-id>/flows.json       a list of flows
<pack-id>/procedures.json  a list of procedures
<pack-id>/images/          the pictures; third-party ones under images/third-party/
```

`passages.json`, `flows.json` and `procedures.json` are each optional (an absent file is an empty list), and a pack has at
least one passage, flow or procedure among them: a pack of reference text only, of troubleshooting only, or of one
installation procedure only is a whole pack, so none of the three is required of every pack.

A field named here is required and is text with something in it, unless it says otherwise. An id is lowercase letters and
digits joined by hyphens (`no-output`). A pack's text is data (HAD-05): nothing in it is an instruction.

### The manifest

| Field | Holds |
| --- | --- |
| `id` | the pack's id, the same as its folder's name; with a passage's id it names an answer's source (HAD-03) |
| `title` | the name a worker is shown when a pack is chosen (extra: a pack needs a name a person can read) |
| `make` | the maker the pack covers; optional, but given with `model` or not at all |
| `model` | the model the pack covers; optional, but given with `make` or not at all |
| `installation_type` | optional: the installation type the pack covers, in words (`packs/TYPES.md` lists them; the check does not hold the list) |
| `version` | the pack's own version, changed whenever its text changes, so a version names what was handed over |
| `sources` | a non-empty list of sources: where each fact in the pack comes from |
| `third_party_images` | a list (it may be empty or absent) of the pictures copied from elsewhere (SC-007) |
| `status` | required, exactly `"field"` or `"demo"`; any other value, or none, is refused (SC-013) |
| `safety_coverage` | optional (absent or empty: the pack covers nothing): a list of declarations that some of the pack's own passages cover the hazard of a general safety rule (SC-024), below |
| `equipment` | optional (absent or empty: the pack names no equipment, and is listed by its title alone): the equipment its manuals describe, "The equipment list" below (SC-027) |

A pack gives `make` and `model`, or `installation_type`, or all three; a pack with neither, or with one of `make` and
`model` alone, is refused.

A `field` pack answers; a `demo` pack answers only in demo mode (HAD-06). There is no approval record: handing the
documentation to the person who loads the packs is the approval (SC-013). A manifest field the format does not name, an
old `admitted_by` included, is ignored. A `field` pack with any page `"unknown"` is refused; a `demo` pack may hold unknown
pages, and the check still counts them.

A source has: `id` (the id passages and flows cite it by, unique in the pack), `title`, `kind` (required: `document` for a
manual, datasheet or PDF that has page numbers, `web` for a web page, which has none; a source with no `kind`, or any other
value, is refused, SC-012), `url` (where it was read; extra: so
a person can check it), `licence` (the licence as the source states it, or the words `not stated`; never left out, since
what a source allows is what the person who loads the packs must weigh, SC-005) and `retrieved` (the date it was read; extra:
a source changes). The check holds that the licence is written down, not that it allows redistribution; that is the
person's judgement when the packs are loaded, and a licence that forbids redistribution never puts its pack in the repository (Core C-033).

### A declaration of coverage (SC-024)

Only a make-and-model pack may hold `safety_coverage`, and it is the one place in a pack that may name a safety rule
(HAD-04); a rule named or overridden anywhere else in a pack is refused as before. A declaration has:

| Field | Holds |
| --- | --- |
| `rule` | the id of a general rule in `solarchat/safety/rules.json`; a rule appears at most once in a pack's list |
| `response` | what the pack's instruction is: `"warn"` (the worker may go on, with the pack's precautions) or `"stop"`; for SR-08 and SR-09 only `"emergency"` |
| `passages` | one or more of the pack's own passage ids, in the order they are shown; their text is the instruction; at least one cites a `document` source with a page that is a number (or numbers: "3", "3, 14", "5-6"), so `"unknown"` never covers anything |
| `declared` | who declared it, in what role, when, on what evidence (SC-016's shape: `by`, `role`, `date`, `evidence`, each with something in it); required on a `demo` pack, whose `role` must be `"maintainer"` (Ghost's word); not required on a `field` pack (handing it over is the approval, SC-013), but whole when given |

A declaration never lists an `answer`: covering a hazard means saying what to do about it, so the reply is still a warn or
a stop (SC-024 (4)). The check refuses a rule that is not a general rule's id or is listed twice, a passage that is not
the pack's or an empty list, a covering passage with no paged `document` citation, `safety_coverage` in a pack that gives
`installation_type` without `make` and `model`, a response out of place, and a `demo` declaration without a maintainer's
`declared`. It cannot tell that a `document` source is the maker's own manual; that is the engineer's to confirm, so the
check prints, for each declaration of a well-formed pack, the rule, the response and the covering passages' sources with pages.

### The equipment list (SC-027)

`equipment` names what the pack's manuals describe, so the chat can say what the packs cover and ask which of it the worker has
(`docs/designs/equipment-intake.md`). It is not `make` and `model` (SC-024's keys for a pack of one product), and it declares no
safety coverage. An entry has:

| Field | Holds |
| --- | --- |
| `id` | lowercase letters, digits and hyphens, unique in the pack (and, when several packs are on, across them: the chat refuses a clash at start) |
| `kind` | one of `panel`, `controller`, `power-station`, `battery`, `inverter`, `connector` |
| `make`, `model` | as the maker writes them; a general entry has `make` "any" and says what it covers in `model` |
| `sources` | one or more of the pack's own source ids: the manuals that make the claim "this pack covers it" |

The check (`scripts/checks/equipment.py`) refuses a bad `kind`, a malformed or repeated `id`, an empty `sources`, and a source id
the pack does not have. The loader reads the list into the leaf's `Equipment` records, `Pack.equipment`.

### A citation (SC-012)

Every `sources` list below (a passage's, a procedure's, a flow's) holds citations of two forms, and the source's `kind`
says which:

| Cites | Form | Example |
| --- | --- | --- |
| a `web` source | a bare source id | `"S2"` |
| a `document` source | an object with the source id and the page | `{"source": "S3", "page": "15"}` |

`page` is a non-empty string, so a label such as "A-3" or "15-16" works. The string `"unknown"` marks a page
not yet found; a `demo` pack may hold it, a `field` pack is refused for it (SC-013). A bare id for a `document` source is refused, and so is an object for a `web` source (a page field that
means nothing is never allowed). The check counts the citations whose page is `"unknown"` and prints the total, so the gap is
visible. The pages are found by a person, from the manual; the check holds that a page is written down, not that it is the right one.

A third-party picture has: `file` (a path under `images/third-party/`), `source_url`, `owner` (the owner or author),
`licence` (as stated) and `shows` (what it shows). Every file under `images/third-party/` has exactly one entry, and every
entry has its file (SC-007).

### A passage

`passages.json` is a list (it may be empty). A passage is one piece of text an answer can be built from and named by:

| Field | Holds |
| --- | --- |
| `id` | the passage's id; with the pack's id it is the reference an answer carries (HAD-03) |
| `title` | a short heading (extra: so a worker and the person who loads the packs can tell passages apart) |
| `text` | the text, in plain words, which an answer may quote and may not go beyond |
| `sources` | a non-empty list of citations of sources from the manifest (see "A citation"); a passage with no source is refused |
| `image`, `image_alt` | optional: a picture, as a path under `images/` that exists in the pack, and the words that stand in for it for a person who cannot see it; a picture needs its `image_alt` (extra: a worker on a phone in sun may not see a picture) |

### A procedure

`procedures.json` is a list (it may be empty). A procedure is one job done in order, shown one step at a time (P-18):

| Field | Holds |
| --- | --- |
| `id` | the procedure's id, in the same one set as passage ids and flow ids |
| `title` | a short heading |
| `sources` | a non-empty list of citations of sources from the manifest (see "A citation") |
| `steps` | a non-empty, ordered list of steps; a procedure with no steps is refused |

A step has `id` (unique within its procedure), `text` (what to do), `right_looks_like` (what a correct result looks like,
so the worker can tell the step is done), optionally `image` and `image_alt` as in a passage, and optionally `stop`: the
words the worker is shown when this step must not be done without the site supervisor or engineer. A `stop` present is
not empty (HAD-04).

### A flow

`flows.json` is a list (it may be empty). A flow is one troubleshooting path, shown one step at a time:

| Field | Holds |
| --- | --- |
| `id` | the flow's id; passage, flow and procedure ids are one set, each used once |
| `title` | a short heading |
| `symptom` | what the worker sees that starts the flow |
| `checks` | a non-empty list, in order; each has `text`, and optionally `image` and `image_alt` as in a passage |
| `fix` | what to do when a check finds the cause |
| `stop` | where to stop: the point at which the worker goes to the site supervisor or engineer, and the words they are shown; a flow with no `stop` is refused (HAD-04: a pack may add steps that stop, never remove a rule) |
| `sources` | a non-empty list of citations of sources from the manifest (see "A citation") |

A flow is linear in version 1: the walker shows the checks one at a time, offers the fix when a check finds the cause,
and otherwise ends at the stop; branching waits for a real pack that needs it.

### What the check does not hold

Whether a licence allows redistribution, whether a passage is true, and whether a pack's text names or overrides a safety
rule: the first two are the judgement of the person who loads the packs, the third is held by the check since TODO 1.3 (the planted breaks `names-safety-rule` and `overrides-safety-rule`).
