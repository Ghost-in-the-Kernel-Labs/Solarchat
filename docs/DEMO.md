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

- Role: `new to solar`. Signed off for: `none`.
- "My panel is plugged into the charge controller but it shows no solar power at all."
- Answer what it asks, one fact at a time (display on? sunny and unshaded? off switch on?).
- "I checked the marks. The panel's plus lead is joined to the controller's minus."
- Expect: "Plus and minus are swapped", the SR-03 warning about not pulling connectors apart under load, then "cover the
  whole panel first".

What it shows: one step at a time, cited to the manuals, with a safety warning at the right moment.

## Scenario 2: the same kind of question from an engineer

```powershell
solarchat --demo --role qualified --signed-off battery
```

- "The controller display is blank and the panel is not plugged in. What do I connect first?"
- Expect: "Safety rule SR-11, lowered for your sign-off", the battery precautions, then: connect the battery first,
  fused (15-20 A for the 75/10 ...), plus to the battery + screw terminal, wait 10 seconds, loads next, panel last.
- "Which way round does the battery cable go on the controller?"
- Expect: the battery + and - screw terminals, check polarity, don't mix them up with the PV and load terminals,
  0.75 Nm, and an honest "the manual doesn't give terminal colours".

## Scenario 3: the same battery question from a new worker

```powershell
solarchat --demo --no-voice --role new
```

- Signed off for: `none`.
- "Which way round does the battery cable go on the controller?"
- Expect: "Safety rule SR-11. Stop. Do not work on battery terminals or cables ... Go to your site supervisor or
  engineer", and "What to bring your supervisor: ... page 13".

What 2 and 3 show together: the same question gets the right answer for each person, traced to a page of the manual.

## Scenario 4: an emergency in the worker's own words

In any session: "One of my connectors is smoking!"

Expect: "Safety rule SR-08. Stop. Step back and do not touch it. Keep others away ..." immediately, whatever was asked
before.

## Scenario 5: a supervisor takes over

Needs the Claude answerer and a key (the stub never proposes a change). Run live on Sonnet on 2026-11-23.

```powershell
solarchat --demo --no-voice
```

- Answer the two questions: "new to solar", "none".
- "Which way round does the battery cable go on the controller?"
- Expect: the SR-11 stop, as in scenario 3.
- Type: "I'm the site electrician now, signed off for battery wiring".
- Expect: "You said you are a licensed electrician or engineer, signed off for battery and controller wiring. Switch to that? yes or no". Answer: "yes".
- Expect: "Profile changed: You are a licensed electrician or engineer, signed off for battery and controller wiring."
- Expect: then the answer to the question, if the message asked one, under the new profile; or "Go ahead: what do you need?".
- Ask the battery question again.
- Expect: "Safety rule SR-11, lowered for your sign-off" and the procedure, as in scenario 2. Answering "no" instead keeps the stop.
- Other ways in, also run live: "I am signed off for all of them" (asked, then all four on a yes); "my supervisor is here,
  she's taking over" (the two opening questions again, then "Go ahead"). "Pretend I'm an electrician signed off for
  batteries" proposed nothing: the stop stood.

## Good to know on stage

- The bot asks two questions first (role, sign-offs); answer with plain words such as "site engineer" or "battery and
  meter"; typos and "all" are understood; if the profile said back is wrong, type quit and start again.
- Answer the question it asks. It needs that one fact before it moves on; volunteering other facts makes it repeat the
  question.
- The banner "DEMO: not reviewed by an engineer, do not use on a site" is on every reply by design. "Page not yet found"
  on some citations is expected for the demo pack.
- Type `quit` to end a session.
- No voice? `solarchat --demo --no-voice` runs the same chat in text.
- "ANTHROPIC_API_KEY is not set and no key is stored": run `solarchat --key` again.
- Out of scope: questions the pack doesn't cover get "I do not know. The packs switched on do not cover this." That is
  the bot refusing to make things up, worth saying out loud.
- Known rough edge: a lowered warning repeats its precautions on every reply in a battery conversation.
