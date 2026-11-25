# Design: the conversation moves forward, says plainly what it cannot do, and lets the person correct or quit anywhere (TODO 2.16)

Written by the coordinator (strong grade) on 2026-11-25, from the blind evaluation of 2026-11-23 (its recommendations R6,
R7, R9, R14, R16, R18, R19, R21, R22, R23, R26, R27; the report stays outside the repository, C-033, and the findings are
restated here). Ghost: "yes, start item 4". A mid-grade worker builds section 3; section 4 holds what Ghost confirms
before landing. Pack content (the figures the pack lacks, error codes, light meanings, page numbers) is item 5, not this.

Read with it: SC-019 (the conversational answerer), SC-020, SC-026, SC-027, SC-028; HAD-03; `solarchat/answer/door.py`
(`DO_NOT_KNOW_TEXT`), `solarchat/project/chat.py` (`ask`, `ask_profile`, `with_rule`, `LOWERED_MARK`, `converse`,
`settle_proposal`), `solarchat/project/intake.py`, `solarchat/model/claude.py` (`SYSTEM_PROMPT`).

## 1. What the evaluation found, restated

- **It stalls (R6, R7).** A new worker was asked four turns running for "the highest solar input voltage in the Victron
  manual"; "next step?" got the previous step again word for word; a fact already given ("in full sun") was asked again.
  The pack does not hold the 75/10's limit (item 5 adds it), so asking once is right; asking four times is not.
- **"I do not know. The packs switched on do not cover this." for everything (R9, R23)**: price, weather, meter settings
  and error codes alike, in the project's internal words, with nowhere to go next.
- **"quit" was not honoured during the opening questions (R14)**, and the only way to correct a misread profile was to
  quit and start again.
- **A reply that answered a different question was taken as an answer (R16)**: "yes the display is on" accepted as "yes,
  the panel is in full sun".
- **Only the controller was named, and the panel was never asked about (R18)**; "not sure" got "I have no pack for that
  equipment" instead of help finding a label.
- **Too slow for an electrician (R19)**: "which step are you at?" twice before any content, after "walk me through it".
- **"Safety rule SR-11, lowered for your sign-off" reads as if safety was reduced (R21)**, and the full battery warning
  repeated on every battery turn (R22; the rough edge noted before the demo).
- **It asserted what the person had not said, and asked two things at once (R26, R27).**

## 2. The changes

1. **The prompt** (fixed text in `SYSTEM_PROMPT`, so the cached block stays byte-identical across a run) gains, in its
   Pace paragraph:
   - "Never repeat your previous step. When the worker says next, ok or done, confirm the last step in a few words and
     give the following one."
   - "If you need a fact before the next step, ask for it once. If the worker cannot give it, say plainly what is
     missing and that their supervisor can help, then offer the next step that does not need it, if there is one."
   - "Use what the worker has already told you; never ask for it again."
   - "If the worker's reply answers a different question, say what it told you and ask your question again, once."
   - "Ask one question at a time. Say 'it sounds like' before anything the worker has not said."
   and in its Depth paragraph:
   - "When a licensed electrician or engineer asks to be walked through a whole job, give the steps in order in one reply
     (no more than six short lines), then take them one at a time. Ask which step they are at only when the request is
     open."
2. **A repeated reply is caught (R7).** When the reply the door gives is an answer (not a stop, warn or "I do not know")
   whose words are 85% or more the same as the previous assistant turn's (Python's `difflib.SequenceMatcher` ratio on
   the spoken text), the chat asks the answerer once more, with the same question and a note added to this call's
   messages only: "You just said that. Move on to the next step, or say plainly what you still need." The second reply is
   shown, whatever it is. One retry at most per turn.
3. **"I do not know" in plain words (R9, R23).** `DO_NOT_KNOW_TEXT` becomes: "I can't help with that: it isn't in the
   manuals I have for this equipment. Your site supervisor or engineer can help." The door's kinds and HAD-03 do not
   change (it names no passage and no rule). Dangerous questions are stops by their rules (SR-15 and the others, J-089),
   not this line. The frozen set scores "I do not know" by kind, so no case moves; the record is checked unchanged.
4. **"quit" ends the chat at any prompt (R14).** `ask` treats "quit" as the end of input; the opening questions, the
   equipment question, and the switch question end the chat at once with no profile or answer recorded. The said-back
   line becomes "If that is wrong, tell me what to change." A correction is read as any statement is (SC-026, SC-028:
   "I'm a crew member" lowers at once or is asked; "I'm not signed off for batteries" removes it).
5. **The equipment step (R18).** After a match that names no panel, the chat asks once: "And the panel's make and model?
   Say 'not sure' if you don't know." An answer is read as the first; "not sure" keeps the general panel steps. A first
   answer of "not sure" (or "don't know") gets one helping question before the no-match line: "That's fine. Look for a
   label on the back of the panel and on the front of the controller or power station, and tell me any names you see."
   Two misses give today's no-match line. `--equipment` skips all of it, as today.
6. **The lowered warning (R21, R22).** The first line of a lowered warn becomes "Safety rule SR-11 (you are signed off for
   this work)". The lowering's precautions are shown and spoken in full the first time that rule's lowered warn appears
   in a conversation; after that, the first line alone and then "The precautions above still apply.", then the reply's
   answer. A new profile (a takeover) shows them in full again once.

## 3. What the worker builds

The six changes of section 2, with tests (scripted answerer, scripted input, fake client):
- "quit" at each of the four prompts ends the chat;
- "I'm a crew member" after the said-back line changes the role, through the proposal path;
- a repeated answer is retried once with the note, and the retry is shown;
- an answer that differs is not retried;
- no more than one retry per turn;
- a controller-only match asks for the panel;
- "not sure" gets the helping question, then the no-match line;
- a second battery turn for a signed-off electrician shows the short reminder, and a takeover shows the precautions in full again;
- `DO_NOT_KNOW_TEXT`'s new words appear wherever the old ones did;
- the eval record is unchanged.

Records: SC-029, a journal entry, `docs/DEMO.md` where expected lines change (the label, "I do not know"), README's
mention of "I do not know" if any. The live check is the coordinator's (Haiku, the evaluation's conversations C01, C02,
C03, C04, C06, C09, C13, C22).

## 4. What Ghost confirms

1. The new "I do not know" words (section 2 (3)).
2. The label "Safety rule SR-11 (you are signed off for this work)" and the short reminder after the first time (section
   2 (6)).
3. "quit" ends the chat from any prompt, and corrections go through the proposal path (section 2 (4)).
Recommended: all three as written.

## Ghost's additions, 2026-11-25

Ghost, 2026-11-25, in chat: "Would having meta prompts like asking the bot to keep the conversation flow going and asking can you describe the step your taking now to keep the turns on the user be helpful? Also, instead of simply saying I dont have information for that, the bot should be warning that it doesn't know, so this could be very dangerous if the human doesnt know what they are doing."

1. **The "I do not know" line warns** (replaces section 2 (3)'s wording; section 4 item 1 is now these words). `DO_NOT_KNOW_TEXT` is exactly: "I don't know this one: it isn't in the manuals I have for this equipment. Don't guess. If you are not sure what to do, stop and ask your site supervisor or engineer before you go on." It restates SR-14's own words ("If you are not sure, do not guess ... Go to your site supervisor or engineer"), so it traces to SR-14's sources (HSE, OSHA); the door cites SR-14 and SC-029 beside it. The kind is unchanged and the eval record does not move.
2. **The turn stays with the worker, and teach-back at checkpoints** (prompt only, fixed text in the Pace paragraph, so the cached block is byte-identical across a run): "End every reply with one clear thing for the worker to do or answer, so the next turn is theirs." and "Before a step that could hurt someone or damage equipment, after a step that changes the wiring, or when you cannot tell whether the last step was done, ask the worker to say in their own words what they are about to do or have just done, and check it against the passages before going on; not on every turn." A test holds both sentences and the identical block.
3. **Flag the off-topic** (Ghost, 2026-11-25, in chat, answering the offer that "the model could flag clearly off-topic questions so they get the plain line, with the warning kept whenever there's doubt": "Yes, lets flag that."): `SCHEMA` gains a required boolean `off_topic` (the prompt: "Set off_topic to true only when the question has nothing to do with solar equipment or the work on site (the weather, prices, news, small talk); otherwise false. When in doubt, false."); `ClaudeAnswerer.off_topic` holds the last call's value, reset at the start of every find; the chat (`solarchat/project/offtopic.py`), after the door's reply and the hold check, turns an "I do not know" the answerer flagged into "That's outside what I can help with. I can help with setting up and fixing the equipment I listed at the start." (no warning, the demo banner kept) only when the worker's message is not about the work: it holds no trigger or `holds` word of any rule, no word of an equipment entry's make or model (three characters or more, never "any" or a filler word), and none of the work words (solar, panel, panels, controller, charger, battery, inverter, connector, cable, wire, lead, leads, voltage, volts, amps, fuse, switch, isolator, roof, install, wiring, connect, power, charge, display, light, error, fault, terminal). Any other reply, and an answerer without the flag (the stub), keeps the warning, so a wrong flag never removes the warning from a work question.
