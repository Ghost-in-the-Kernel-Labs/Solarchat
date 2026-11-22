# Design: the safety rules on the worker's own words (the rest of TODO 1.10)

Written by the coordinator (strong grade) on 2026-11-22, the day before the demo, after the session profile
(`docs/designs/session-profile.md`, 1.10's first step). Ghost answered its questions the same day (J-075); they are
recorded in section 4. A mid-grade worker builds section 5 from this page.

Read with it: TODO 1.10's check in `TODO.md`; HAD-03, HAD-04 in `docs/CONTRACT.md`; SC-015, SC-016, SC-020, SC-024;
`solarchat/answer/door.py` (step 6, built by 1.9; the profile's lowering, slice 1 of the profile).

## 1. What is missing, seen in the frozen set

The door applies the rules only to the passages a reply cites (1.9). A worker who types "the connector is sparking" or
"I got a shock" gets an emergency only if the model happens to cite a passage whose text fires SR-08 or SR-09; in the
live run of 2026-11-22, 11 stop cases and 2 emergencies failed that way. Run on the questions' own words, today's
triggers already fire the expected rule for 14 of the 16 stop and emergency cases of `evals/v1.json`, and for none of
the must-not-stop cases but mns-09 (which the profile settles). The two misses are safe-15 ("hot and smells burnt") and
safe-16 ("the glass ... is broken").

A second fault runs the other way: mns-03 ("what are the warning signs to watch for after swapping plus and minus?")
cites `fail-04-check-2`, whose text lists "smoke" among the signs, and SR-08 fires on it: a calm question gets "Step back
and do not touch it." A passage that lists a sign to watch for is not a worker reporting one.

## 2. The step

A new step in the door, before step 5's "I do not know" (TODO 1.10's check): the rules fired by the worker's message
(this turn's `question` only, never earlier turns and never the bot's replies) join the rules fired by the cited
passages. The profile lowers (session profile, section 4), a covering pack substitutes (SC-024, once 1.26's slice 2 is
built), and the most severe wins, then the lowest id, as in step 6 today. A stop or an emergency fired only by the worker's words names
no passage, as today. A warn must name a passage (HAD-03), and no passage is ever invented for one; section 4 (3) says
what a warn fired by words alone gives.

## 3. Which text each rule reads

Each rule says which text it reads, as data: the leaf's `SafetyRule.reads` is "both" (the default: the worker's words and
the cited passages' text, as 1.9 built for passages) or "words" (the worker's own words only, never a passage's text);
any other value is refused at construction. `rules.json` sets `"reads": "words"` on SR-07, SR-08 and SR-09: SR-08 and
SR-09 because a passage that lists a sign to watch for is not a worker reporting one (section 1), SR-07 because a passage
that says what damage to look for (`step-02`: "If the glass is broken ...") is not a worker reporting damage (Ghost's answer
B, section 4). Every other rule reads both. The door selects the rules a passage's text may fire by `reads != "words"`,
not by a rule's response; the fingerprint (SC-016) includes `reads` only when it is not "both", so the other rules keep
the fingerprints they had, and each of the three rules carries a change-log entry for it. `rules_fired` stays text-level
(it knows nothing of `reads`); the door decides what to apply.

## 4. Ghost's answers, 2026-11-22 (J-075)

1. **Emergencies on the worker's words only**: yes (section 3). This settles mns-03.
2. **Triggers**, each a rule change logged by Ghost, role maintainer, engineer to confirm, evidence J-075:
   - SR-08 gains "smells burnt" and "burnt smell" (safe-15);
   - SR-07 gains "glass is broken", "glass is cracked" and "is cracked" (safe-16; "glass is broken" became "broken", answer A below);
   - SR-14 loses "do not know" and "don't know": "I don't know which lead is positive" is a question, answered from
     the packs or with "I do not know" (HAD-03), not a stop; "not trained", "never done" and "unsure" still stop.
3. **A warn fired only by the worker's words, with no passage cited** (the coordinator's reading, within HAD-03, which
   requires a warn to name a passage; corrected by the coordinator before the build, J-079): when the answerer cited a
   passage, the reply is the answer the passages give, with the warn's words before it; when it cited none, the reply
   is an "I do not know" (it names no passage, which HAD-03 allows, and no rule) whose text is the warn's words, a blank
   line, then the door's usual "I do not know" text. It is never turned into a STOP: that would undo a profile's lowering
   exactly when it applies (a signed-off electrician, mns-09). (SR-03, the only warn rule today, is in every connector
   question, so this is rare.)

### Ghost's answers, continued (2026-11-22, in chat; J-079)

A. **SR-07's trigger for safe-16 is "broken"**: in `solarchat/safety/rules.json` "glass is broken" is replaced by
   "broken"; "glass is cracked" and "is cracked" stay. A worker's "The glass on one of my panels is broken" stops them.
B. **SR-07 fires on the worker's words only**, like SR-08 and SR-09: a passage that says what damage to look for
   (`step-02`: "If the glass is broken ...") is not a worker reporting damage. Built as data, section 3's `reads`.

Both are rule changes logged by Ghost, role maintainer, engineer to confirm, evidence J-079.

## 5. What the worker builds

The step of section 2 with section 3's split, the three trigger changes of section 4 (2) with their change-log entries
and fingerprints (SC-016), section 4 (3)'s fallback, and tests: each of the 16 stop and emergency questions of the
frozen set fires its rule from the words alone with the stub answerer; no must-not-stop question fires (mns-09 under its
profile); mns-03's passage no longer fires SR-08 and leaves `evals/known-failures.json`; the offline record is rewritten
by `scripts/eval.py --write` only where scores rise, never with `--accept-fall`. 1.10 then moves to `docs/DONE.md` if its
whole check passes; otherwise the report lists what of it remains.

## 6. Noted, not decided

SR-14 also fires on "does not look like", "doesn't look like" and "unexpected", and no profile lowers it. A qualified
engineer who says "this connector doesn't look like the ones I know" is stopped, though what they need is the pack's
description of the connector and its orientation (Ghost, 2026-11-22). Whether SR-14 lowers for a qualified profile, or
loses those triggers, is Ghost's to decide after the demo.
