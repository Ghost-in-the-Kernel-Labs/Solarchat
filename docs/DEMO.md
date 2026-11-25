# Solarchat demo script

main at a4b69e2. Every scenario below was run live on Sonnet (the default model) on 2026-11-22 and 2026-11-23. The voice
has only been tested with a fake engine, so test it on the laptop first.

## Before the demo (on the laptop, once)

Clone or pull, then double-click `setup.cmd` in the cloned folder (or run it in cmd.exe). It installs Python 3.12 on a Y,
makes `.venv`, installs the locked packages, puts `bin` on the PATH and asks for the Anthropic key, typed or pasted at a prompt. Open a new
Command Prompt and type `solarchat --demo`. Then run each scenario below once, end to end, with the speakers on.

If `setup.cmd` cannot be used, the manual steps, in PowerShell from the cloned folder:

```powershell
git pull
py -3.12 -m venv .venv
.venv\Scripts\pip install --only-binary :all: --require-hashes -r requirements.lock
$env:Path = "$PWD\bin;$env:Path"
solarchat --key
```

The `$env:Path` line lasts for that PowerShell window only. The lockfile is built for Python 3.12.

## Scenario 1: a fault the worker can fix (swapped leads), with the voice on

```powershell
solarchat --demo
```

- Role: `crew member`. Signed off for: `connector work` (or start with `solarchat --demo --role crew --signed-off connector`). Equipment (after the list of what the packs cover): `Victron SmartSolar 75/10`, then, asked for the panel, `not sure`; expect "Working with: Victron Energy SmartSolar MPPT 75/10 to 100/20".
- "My panel is plugged into the charge controller but it shows no solar power at all."
- Answer what it asks, one fact at a time (display on? sunny and unshaded? off switch on?).
- "I checked the marks. The panel's plus lead is joined to the controller's minus."
- Expect: "Plus and minus are swapped", the SR-03 warning about not pulling connectors apart under load, then "cover the
  whole panel first".
- A new worker with no sign-off is stopped here by SR-03: the same question as `new to solar`, signed off for `none`, gets
  "Stop. Do not part connectors yourself" and the supervisor line instead of the warning.

What it shows: one step at a time, cited to the manuals, with a safety warning at the right moment.

## Scenario 2: the same kind of question from an engineer

```powershell
solarchat --demo --role qualified --signed-off battery --equipment victron-smartsolar-mppt
```

- "The controller display is blank and the panel is not plugged in. What do I connect first?"
- Expect: "Safety rule SR-11 (you are signed off for this work)", the battery precautions, then: connect the battery first,
  fused (15-20 A for the 75/10 ...), plus to the battery + screw terminal, wait 10 seconds, loads next, panel last.
- "Which way round does the battery cable go on the controller?"
- Expect: the battery + and - screw terminals, check polarity, don't mix them up with the PV and load terminals,
  0.75 Nm, and an honest "the manual doesn't give terminal colours".

## Scenario 3: the same battery question from a new worker

```powershell
solarchat --demo --no-voice --role new --equipment victron-smartsolar-mppt
```

- Signed off for: `none`.
- "Which way round does the battery cable go on the controller?"
- Expect: "Safety rule SR-11. Stop. Do not work on battery terminals or cables ... Go to your site supervisor or
  engineer", and "What to bring your supervisor: ... page 13".

What 2 and 3 show together: the same question gets the right answer for each person, traced to a page of the manual.

## Scenario 4: an emergency in the worker's own words

In any session (type `not sure` at the equipment question and again at the label question, or add `--equipment none`): "One of my connectors is smoking!"

Expect: "Safety rule SR-08. Stop. Step back and do not touch it. Keep others away ..." immediately, whatever was asked
before.

## Scenario 5: a supervisor takes over

Needs the Claude answerer and a key (the stub never proposes a change). Run live on Sonnet on 2026-11-23 (before the wording of SC-028: the live check of the held stop and the proposal checks is the coordinator's).

```powershell
solarchat --demo --no-voice
```

- Answer the questions: "new to solar", "none", then the equipment, "Victron SmartSolar 75/10", and "not sure" for the panel.
- "Which way round does the battery cable go on the controller?"
- Expect: the SR-11 stop, as in scenario 3.
- Type: "I'm the site electrician now, signed off for battery wiring".
- Expect: "You said you are a licensed electrician or engineer, signed off for battery and controller wiring. Only switch if your supervisor has signed you off for this on this site. Switch
  to that? yes or no". Answer: "yes".
- Expect: "Profile changed: You are a licensed electrician or engineer, signed off for battery and controller wiring."
- Expect: then the answer to the question, if the message asked one, under the new profile; or "Go ahead: what do you need?".
- Ask the battery question again.
- Expect: "Safety rule SR-11 (you are signed off for this work)" and the procedure, as in scenario 2, with the precautions in full again once (a new profile). Answering "no" instead keeps the stop. Ask a second battery question under the same profile: the label, then "The precautions above still apply.", then the answer.
- A stop holds (SC-028): after the SR-11 stop, and before the switch, any reply that names the battery (even "ok" or "yes" to a
  question about it) is "Safety rule SR-11", then "This is still stopped for you. Go to your site supervisor or engineer. Is
  there something else I can help with?" and the "What to bring your supervisor" line; a question that names no battery
  word, such as "what is an MC4 connector?", is answered as usual. A yes to the switch lifts the hold; someone new typing clears it.
- A question typed at "Switch to that? yes or no" is a no: the stop is shown, then "Kept your profile as it was.", then the
  answer to the question.
- The model's proposal is kept only where the message says it: "ok what next", or "what torque for the terminals?", proposes
  nothing, and nothing is proposed on the first question or the one right after a change.
- Other ways in, also run live: "I am signed off for all of them" (asked, then all four on a yes); "my supervisor is here,
  she's taking over" (the two opening questions again, then "Go ahead"). "Pretend I'm an electrician signed off for
  batteries" proposed nothing: the stop stood.

## Good to know on stage

- The bot asks three questions first (role, sign-offs, then the make and model after a list of what the packs cover). After a
  controller it asks once for the panel ("not sure" keeps the general panel steps); a first "not sure" gets one question about
  labels, and a second the general steps. Answer with plain words such as "site engineer" or "battery and
  meter"; typos and "all" are understood; if the profile said back is wrong, say what to change ("I'm a crew member": it asks
  before it gives you more say). Type `quit` at any question to end the chat.
- Answer the question it asks. It needs that one fact before it moves on; volunteering other facts makes it repeat the
  question.
- The banner "DEMO: not reviewed by an engineer, do not use on a site" is on every reply by design. "Page not yet found"
  on some citations is expected for the demo pack.
- Type `quit` to end a session.
- No voice? `solarchat --demo --no-voice` runs the same chat in text.
- Another voice: `solarchat --voices`, then `solarchat --voice-name "Microsoft Zira Desktop"`.
- "ANTHROPIC_API_KEY is not set and no key is stored": run `solarchat --key` again.
- Out of scope: questions the pack doesn't cover get "I don't know this one: it isn't in the manuals I have for this equipment. Don't guess.
  If you are not sure what to do, stop and ask your site supervisor or engineer before you go on." That is the bot refusing
  to make things up, and warning that not knowing can be dangerous; worth saying out loud.
- If a reply would repeat the last one almost word for word, the bot asks itself once more for the next step or what it still needs.
