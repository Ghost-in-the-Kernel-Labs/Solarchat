# Design: packs cover the safety rules for their own make and model (SC-024, TODO 1.26)

Written by the coordinator (strong grade) on 2026-11-22, after SC-024 came into force on Ghost's word ("go with your
recommendations on all six", J-069), before anything is built. A mid-grade worker builds each slice of section 8 from
this page alone; where it is not precise enough, the fix is to this page, not a guess (Core C-003). Section 9 holds
what Ghost must answer first.

Read with it: SC-024 and SC-015, SC-016, SC-020 in `theGhost.md`; HAD-03, HAD-04 (as amended) and the pack format in
`docs/CONTRACT.md`; `docs/designs/answering-door.md` (the door's steps); `solarchat/answer/door.py` (step 6, built by
1.9); TODO 1.10 (the rules on the worker's own words) and 2.3 (the walker).

## 1. Ghost's direction, and the shape in one paragraph

Ghost, 2026-11-22: "the invariant design is the packs, because the packs should have the most specific knowledge about
their scenarios ... There are general safety rules to be sure, but a pack should contain detailed instructions about
installation and safety. Only when a pack doesnt have that should the system default to the generic safety rules."

The shape: a make-and-model pack may **declare**, in its manifest, that some of its own passages cover the hazard of a
general rule (SR-nn). When that rule fires during a conversation about that pack, the reply gives the pack's instruction
and response, cited to the pack's passages, in place of the general rule's words. A rule the pack does not declare
fires exactly as today. SR-08 and SR-09 keep the emergency response in every pack; a pack may only add its own words
beside them. Only a handed-over pack may declare, each covering passage cites the maker's manual with a page, and the
engineer's packet lists every declaration.

## 2. The manifest's coverage field

A new optional manifest field, `safety_coverage`, a list (absent or empty: the pack covers nothing):

```json
"safety_coverage": [
  {
    "rule": "SR-02",
    "response": "warn",
    "passages": ["meter-check-1", "meter-check-2"],
    "declared": {"by": "Ghost", "role": "maintainer", "date": "2026-11-23", "evidence": "J-0nn"}
  }
]
```

| Field | Holds |
| --- | --- |
| `rule` | the id of a general rule in `solarchat/safety/rules.json` |
| `response` | what the pack's instruction is: `"warn"` (the worker may go on, with the pack's precautions) or `"stop"`; for SR-08 and SR-09 only `"emergency"` |
| `passages` | one or more of the pack's own passage ids, in the order they are shown; their text is the instruction |
| `declared` | who declared it, in what role, when, on what evidence (SC-016's shape); required on a `demo` pack (Ghost's word, role `maintainer`), absent on a `field` pack (handing it over is the approval, SC-013) |

A rule appears at most once in a pack's list. A declaration never lists an `answer`: covering a hazard means saying what
to do about it, so the reply is still a warn or a stop (SC-024 (4): the reply cites the pack; nothing is silenced).

## 3. What the pack check refuses (SC-024 (1), (2), (3), (5))

`scripts/checks/packs.py` refuses, each shown by a planted break under `test/fixtures/broken/packs/`:

1. a `rule` that is not a general rule's id, or a rule listed twice;
2. a `passages` entry that is not a passage of this pack, or an empty list;
3. a covering passage none of whose citations is a `document` source with a page that is a number (or numbers), so
   `"unknown"` never covers anything, in a `demo` pack as in a `field` pack;
4. `safety_coverage` in a pack that gives `installation_type` without `make` and `model`: coverage is a make-and-model
   pack's (Ghost: "a specific make and model");
5. a `response` other than `warn` or `stop`, or, for SR-08 and SR-09, other than `emergency`;
6. a `demo` pack's declaration without `declared`, or with a `role` other than `maintainer`.

The check cannot tell that a `document` source is the maker's own manual; that is the engineer's to confirm in the
packet (section 6), and the check prints each declaration's sources so the person who loads the packs sees them.

## 4. The door

Step 6 today (1.9) finds the rules fired by the cited passages' text and gives the most severe, then the lowest id.
With coverage, between finding the fired rules and choosing one:

1. **Attribute each hit to a pack.** A rule fired by a cited passage belongs to that passage's pack. A rule fired by the
   worker's own words (1.10's step) belongs to the pack the conversation is about: the one pack switched on, or, when
   several are on, the pack of the passages the answerer cited; with several on and none cited, it belongs to no pack.
2. **Substitute.** A hit whose pack declares its rule becomes that declaration: the response is the declaration's, the
   words are the covering passages' text in order, and the passages are cited. A hit with no pack, or whose pack does
   not declare the rule, stays the general rule.
3. **Choose.** Of the hits after substitution, the most severe response wins, then the lowest rule id (SC-015 and the
   answering door's answer 8, unchanged).
4. **The emergency floor.** A covered SR-08 or SR-09 is an emergency: the general rule's words first, then the pack's
   covering passages' text, cited.

A substituted reply names the general rule it covers (`rule_id`, as today) and the pack's passages, and says whose
instruction it is: its text ends with "From the <pack title> pack (covers <SR-nn> for <make> <model>)." on its own line.

## 5. The leaf change (Ghost approves it under Core C-012)

Today `Reply` refuses a STOP that names a passage (HAD-03: a stop names none) and has no place to say a pack covered it.
1.26 needs:

- `Reply` gains `covered_by: str | None = None`, the id of the pack whose declaration gave the reply; when it is set, the
  reply is a WARN or a STOP and names at least one passage of that pack; when it is not set, the rules stand as they are.
- HAD-03's sentence "a stop name[s] none" gains "unless a pack's declaration covers its rule (SC-024)".
- A `SafetyCoverage` record (rule, response, passages, declared) and the manifest's tuple of them, read by
  `solarchat/packs/load.py`; the door imports nothing new (`packs` and `safety` it already may).

## 6. What is recorded, and what the engineer sees

Every reply with `covered_by` set is recorded in the session as any reply is, so a session shows which pack covered
which rule. The engineer's packet (TODO 1.14) gets a section: per pack, each declaration with its rule, response,
passages, their sources and pages, and `declared`, marked "engineer to confirm" (SC-024 (6), P-20).

## 7. How it meets the other decisions

- **SC-020 (the session profile).** A profile lowers a general rule only. A covered rule's response is the pack's, and a
  profile does not lower it further: the manual already said what that make and model needs.
- **TODO 1.10.** 1.10 adds the worker's-words step; section 4 already places its hits. 1.10's own design settles where
  that step runs; coverage applies the same way wherever it runs.
- **The walker (2.3).** The walker applies the same function to the step it shows, so a walk and an answer give the
  same instruction for the same hazard.
- **The frozen set.** `evals/v1.json` is untouched; the seed pack declares nothing (it is keyed by installation type,
  section 3 (4)), so every frozen case scores as today. Coverage is tested on a fixture pack with `make` and `model`.

## 8. The slices, in order (each small enough for a mid-grade worker)

1. **The format and the check**: `safety_coverage` in the contract's pack format, the loader's `SafetyCoverage`, the
   six refusals of section 3 with their planted breaks, a good fixture pack that declares SR-02 (warn) and SR-08
   (emergency, words beside). Needs Ghost's answer to question 1 only for the leaf record; the check can land first.
2. **The leaf and the door**: `covered_by`, HAD-03's sentence, section 4's attribution, substitution, choice and floor,
   each with a test on the fixture pack; 1.9's tests unchanged.
3. **The packet**: section 6's listing, with 1.14.
4. **The walker**: with 2.3.

## 9. What Ghost must answer, ranked

1. **The leaf change** (section 5): `Reply.covered_by`, and a stop that a pack covers may name the pack's passages.
   Recommended: yes; without it a covered stop cannot cite whose instruction it is, which SC-024 (4) requires.
2. **Several packs switched on** (section 4 (1)): a worker's-words hit belongs to the one pack on, or to the pack the
   answerer cited, and otherwise to no pack, so the general rule applies. Recommended: as written; a hazard said in
   words before any product is named is answered generally.
3. **The maker's own manual** (section 3): the check holds that a covering passage cites a paged `document`; that the
   document is the maker's own is the engineer's to confirm, not the check's. Recommended: as written.
4. **The profile** (section 7): a profile never lowers a covered rule. Recommended: yes.
5. **Make and model only** (section 3 (4)): an installation-type pack, like the seed pack, cannot declare coverage.
   Recommended: yes, as SC-024 says "a specific make and model"; say if a type pack written from one maker's manual
   should be able to.

### Ghost's answers, 2026-11-22 (in chat: "go with your recommendations")

All five as recommended (J-071): (1) the leaf change is approved: `Reply.covered_by`, and a stop a pack covers names
the pack's passages; (2) with several packs on, a worker's-words hit belongs to the one pack on or the pack cited, else
the general rule applies; (3) the check holds a paged `document`, and the engineer confirms it is the maker's own manual;
(4) a session profile never lowers a covered rule; (5) only a make-and-model pack may declare coverage.
