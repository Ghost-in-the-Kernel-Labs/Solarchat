# Design: the session profile, who the bot is talking to (SC-020, the first step of TODO 1.10)

Written by the coordinator (strong grade) on 2026-11-22, the day before the demo, on Ghost's word: "the decision to not
ask who the person they were talking with is probably a mistake. context is important." SC-020 decided the profile on
2026-11-21 and left four things for this design to settle (where it is held, how a rule names its lowerings, the
evaluation side file, the meter split); this page settles them and sizes the build for one evening. Section 8 holds
what Ghost must answer first.

Read with it: SC-020, SC-015, SC-016, SC-024 in `theGhost.md`; HAD-03, HAD-04 in `docs/CONTRACT.md`;
`solarchat/safety/rules.json`; `solarchat/answer/door.py`; `solarchat/project/chat.py`; `solarchat/model/claude.py`.

## 1. The problem, seen live

Asked "the controller display is blank and the panel is not plugged in; what do I connect first?", the bot answered
"the battery goes on the controller first ... but don't wire the battery yourself; that's a job for the site
engineer." Right for the newest contractor; wrong for the engineer who is there to wire it. Ghost: "the engineer may be
qualified on many other systems, but just not be aware of what the specific connector on this one looks like. They need
a description of what the connector looks like and proper orientation, not a refusal."

Two causes. The bot never asks who it is talking to, so every rule answers as for the newest contractor; and the model
is told to give one small step, never how much a qualified person needs. A third cause is the pack's content (the seed
pack does not describe battery terminals), which a make-and-model pack fixes (SC-024), not this design.

## 2. The questions, asked once at the start

Two questions, before the first one the worker types (SC-020: three or four at most):

1. "Before we start: what is your role? New to solar, crew member, or licensed electrician or engineer?"
2. "Which of these has your supervisor signed you off for on this site: meter tests, connector work, battery and
   controller wiring, work at height with fall protection? Say the ones that apply, or none."

The answers are read by plain word matching, never by the model, so a model cannot talk a worker into a sign-off:
role words (`new`, `crew`, `electrician`, `engineer`), sign-off words (`meter`, `connector`, `battery` or `controller`,
`height` or `roof`), and `none`. An answer that names no role is asked once more; a second miss is "new to solar". An
answer to question 2 that names nothing known is "none". The bot then says the profile back in one line ("You are a
licensed electrician or engineer, signed off for battery and controller wiring.") and the worker's first question is
asked for.

`--role` and `--signed-off` on the chat set the answers and skip the questions (for tests and a scripted demo); they are
self-declared, exactly as typed answers are. The company's override of SC-020 (3) is not built here: there is no
company setting yet, and section 8 asks Ghost to accept that for now.

## 3. Where the profile is held

A leaf record, `Profile(role: str, signed_off: frozenset[str])`, with `role` one of `new`, `crew`, `qualified` and
`signed_off` a subset of `meter`, `connector`, `battery`, `height`; refused at construction otherwise. The default is
`Profile("new", frozenset())`, so a caller that passes none gets today's behaviour exactly. It lives for one chat
session in memory, in `solarchat/project/chat.py`, and is passed to the door with every question; nothing else holds
it, never a pack and never a rule (SC-020). A session ends with the chat; a new chat asks again.

## 4. How a rule names its lowerings (SC-020 (1))

A rule in `rules.json` may carry `lowered_for`, a list:

```json
"lowered_for": [
  {"signed_off": "meter", "response": "warn",
   "words": "You are signed off for meter tests: use a meter and test leads rated for the string's DC voltage, measure at the connectors, never across a loaded circuit."}
]
```

`signed_off` (one of section 3's four) or `role` (`qualified`) names the profile answer; `response` is lower than the
rule's own (`stop` to `warn`); `words` replace `words_shown` in the warn, and are the precautions that still apply; they say only what the rule's own
`sources` say (Ghost, 2026-11-22: everything the bot says traces to a source), and the warn's body is the pack's cited
answer, so the procedure itself comes from the manual. An
`emergency` rule never carries `lowered_for`, and the safety check refuses one. `lowered_for` enters the rule's
fingerprint, so adding one needs a change-log entry (SC-016: by Ghost, role maintainer, engineer to confirm).

The door's step 6 (and 1.10's worker's-words step, later) finds the fired rules as today, lowers each one whose
`lowered_for` matches the profile, then chooses the most severe as today. A covering pack (SC-024) is applied before a
lowering, and a profile never lowers a covered rule (Ghost's answer 4, J-071).

## 5. How much the bot explains (SC-020 (2))

The answerer is told the profile. `ClaudeAnswerer` adds one line to the conversation (not to the cached system block,
which stays byte-identical across a run): "The worker: <role words>; signed off for: <list or none>." The system prompt
gains one paragraph under Pace: for a licensed electrician or engineer, give the whole step the passages describe in one
reply, including what a part looks like and which way round it goes when the passages say so; for someone new to solar,
the one next small step with its reason. Which steps and stops are given does not change (SC-020 (2), HAD-03): only how
much of a step is said at once.

## 6. What is recorded (SC-020 (4))

There is no session record yet in the project (TODO 1.14 and the hosted mode will add one). For now the chat shows the
profile at the start, every warn that a profile lowered says so in its first line ("Safety rule SR-11, lowered for your
sign-off"), and the profile is part of the history the answerer sees. The engineer's packet (1.14) lists every rule's
`lowered_for` with its change-log entry.

## 7. The evaluation side file, and the meter split

`evals/profiles.json` maps a case id to a profile (`{"mns-09": {"role": "qualified", "signed_off": ["meter"]}}`);
the runner passes it to the door for that case and the default for every other; `evals/v1.json` and its hash are
untouched, and the record shows the profile each case ran under. mns-09 should then leave `evals/known-failures.json`
once SR-02 lowers for `meter`.

The meter triggers stay in SR-02 for now (no split): SR-02 lowers as a whole for a meter sign-off, and its warn keeps
the live-panel warning in its words. A split is a later rule change if the engineer asks for it.

## 8. What Ghost must answer, ranked

1. **The lowering table** (each a rule change on Ghost's word, role maintainer, engineer to confirm):

   | Rule | Lowered to warn for | Why |
   | --- | --- | --- |
   | SR-02 live panel, meters | signed off for meter tests | SC-020's own example |
   | SR-11 batteries | signed off for battery and controller wiring | Ghost's engineer wiring the battery |
   | SR-05 work at height | signed off for work at height with fall protection | the sign-off names exactly this |
   | SR-04 opening an enclosure | none for now | setup needs no enclosure opened; add later if asked |
   | SR-01, SR-06, SR-07, SR-10, SR-12, SR-13, SR-14 | never | site rules, power lines, damage, overvoltage, bypassing, the maker's instructions and being unsure stop everyone |
   | SR-08, SR-09 | never (emergencies) | SC-020 |

   Recommended: as in the table.
2. **The leaf change**: `Profile`, `answer(..., profile)`, `SafetyRule.lowered_for`. Recommended: yes.
3. **A fourth sign-off, battery and controller wiring**, and the role "licensed electrician or engineer" (SC-020 named
   "licensed electrician"). Recommended: yes, for Ghost's case.
4. **No company override yet** (SC-020 (3)): self-declared answers only until a company setting exists. Recommended:
   accept for now; the engineer's packet and the on-screen profile keep it visible.

## 9. The slices, in order

1. **The profile and the lowering**: the leaf's `Profile` and `SafetyRule.lowered_for`, the safety check's refusals
   (an emergency with `lowered_for`, a response not lower than the rule's, an unknown sign-off), `rules.json`'s
   lowerings from section 8 with their change-log entries, the door's lowering, each with tests; `evals/profiles.json`
   and the runner (mns-09).
2. **The questions and the explanation**: the two questions and their word matching in the chat, `--role` and
   `--signed-off`, the profile line to the answerer and the prompt's paragraph, the lowered warn's first line; tests with
   the fake client and scripted input.

### Ghost's answers, 2026-11-22 (J-074)

Both questions put to Ghost were answered as recommended: the lowering table of section 8 (1) exactly (SR-02 for meter
tests, SR-11 for battery and controller wiring, SR-05 for work at height with fall protection; every other rule never;
SR-08 and SR-09 never), and the rest approved whole: the leaf change, the fourth sign-off and the role "licensed
electrician or engineer", the explanation depth, and no company override for now.
