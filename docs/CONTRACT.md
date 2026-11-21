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
once a document reports one (the evaluation set's scores, TODO 1.5).

## HAD-03 Hadley answers only from admitted text, names it, or says it does not know

Every reply is one of three kinds. An answer carries at least one passage reference (the pack's id
and the passage's id) from a pack that is admitted and switched on, and says nothing those passages
do not support. A question the switched-on packs do not cover gets "I do not know" with no
passages, never a guess. A safety rule that fires gets a stop (HAD-04). Held by the leaf's `Reply`,
which refuses an answer with no passage and a "do not know" or a stop with one (`test/test_leaf.py`);
the evaluation set holds the rest (SC-003, SC-005).

## HAD-04 The safety rules sit outside every pack, and no pack can remove or change one

The safety rules are the project's own text, kept in the `safety` module, never in a pack. A rule
that fires stops the conversation's current step and sends the worker to the site supervisor or
engineer; the site's own safety procedures come first. A pack may add steps that stop; it cannot
remove, reword or switch off a rule. Held by the leaf's `Reply` (a stop names its rule) and, once
they exist, the safety rules' check (TODO 1.3) and the pack check (TODO 1.2).

## HAD-05 A pack's text is data, never instructions

Nothing in a pack is read as an instruction to Hadley: a passage that says "ignore the safety
rules" is shown or quoted as a passage, never obeyed (Core C-007). Held by the leaf's `Passage`,
whose text is only ever quoted, and, once it exists, the evaluation set's injection cases (TODO 1.5).

## HAD-06 A pack that is not admitted is never used to answer

A pack is admitted when its manifest names the person who admitted it and the date (SC-005); any
other pack, the demo packs included, may be read and checked but never answers. Held by the leaf's
`is_admitted` (`test/test_leaf.py`) and, once it exists, the pack check (TODO 1.2).
