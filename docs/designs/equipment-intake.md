# Design: the bot names what it covers, then asks for the make and model (TODO 2.14)

Written by the coordinator (strong grade) on 2026-11-23, on Ghost's word after a run on Windows. A mid-grade worker builds
section 6 from this page; where it is not precise enough, the fix is to this page, not a guess (Core C-003).

Read with it: SC-024 (packs are the authority for their own make and model) and `docs/designs/pack-coverage.md`; SC-019
(the conversational answerer); SC-020 and SC-026 (the profile, the model's proposal checked by the chat); the pack format
in `docs/CONTRACT.md`; `solarchat/packs/load.py`; `solarchat/model/claude.py`; `solarchat/project/chat.py`.

## 1. What is wrong, seen on Windows

After the two profile questions, Ghost typed "I need help setting up this solar panel" and the bot answered "First step:
check the voltages match. Find the open-circuit voltage (Voc) on the panel's label." Ghost: "first step here is wrong. The
bot should be asking what the make and model of the panel is, and be giving coverage options from the packs that it is
able to assist with."

The bot never learns what equipment is in front of the worker, so it starts from the general steps whatever the panel and
controller are, and the worker cannot tell which equipment the packs actually cover.

## 2. Ghost's answers (2026-11-23, in chat)

1. **List, then ask**: after the profile, the bot says what the packs cover, then asks for the make and model of the panel
   and the controller. With no match it says so and offers the general steps, warning that the maker's own instructions
   come first where they differ.
2. **The model reads the answer, checked**: the model picks matching equipment from the packs' own lists, so "victron
   75 10" and "smart solar mppt" both work; the chat accepts only an entry actually on a list and says back what it
   matched. Choosing equipment unlocks no safety rule, so SC-020's word-matching guard is not needed here.

## 3. The manifest's equipment list

A new optional manifest field, `equipment`, a list (absent or empty: the pack names no equipment, and is listed by its
title alone):

```json
"equipment": [
  {"id": "victron-smartsolar-75-10", "kind": "controller", "make": "Victron Energy",
   "model": "SmartSolar MPPT 75/10 to 100/20", "sources": ["S4", "S5"]}
]
```

| Field | Holds |
| --- | --- |
| `id` | lowercase letters, digits and hyphens, unique in the pack |
| `kind` | one of `panel`, `controller`, `power-station`, `battery`, `inverter`, `connector` |
| `make`, `model` | as the maker writes them; a general entry has `make` "any" and says what it covers in `model` |
| `sources` | one or more of the pack's own source ids: the manuals that make the claim "this pack covers it" (Ghost: everything the bot says traces to a source) |

The pack check (`scripts/checks/packs.py`) refuses a bad `kind`, a duplicate or malformed `id`, an empty `sources`, or a
source id the pack does not have, each with a planted break under `test/fixtures/broken/packs/`. The loader reads the list
into a record beside `SafetyCoverage` (an `Equipment(id, kind, make, model, sources)` record and `Pack.equipment`, a leaf
change under Core C-012 that this design asks Ghost to confirm, section 7). `equipment` is not `make`/`model` (SC-024's
make-and-model pack keys): it names what the pack's manuals describe, and declares no safety coverage.

The seed pack's list (the worker checks each against the pack's sources, and adds none the sources do not support):

- `victron-smartsolar-mppt`: controller, Victron Energy, SmartSolar MPPT 75/10 to 100/20; S4, S5, S10.
- `ecoflow-r600`: power station, EcoFlow, R600; S8.
- `mc4-connector`: connector, any, MC4 and MC4-compatible connectors; S2, S7.
- `crystalline-panel-mc4`: panel, any, crystalline silicon panels with MC4 leads (the general steps); S3. Its `model` says
  it is the general case.

## 4. The intake, in the chat

After the profile is said back (and before the first `> ` prompt for a question):

1. **The list** (no model call): "I can help with:" then one line per equipment entry of the packs switched on, grouped by
   kind, as "<make> <model>" ("any" makes print as the model's words alone). Spoken when the voice is on.
2. **The question**: "What is the make and model of your panel, and of your charge controller or power station? Say
   'not sure' if you don't know." Spoken.
3. **The reading**: the answer goes to the answerer's new `identify(text, equipment) -> tuple[str, ...]`, which returns
   equipment ids. `ClaudeAnswerer.identify` makes one small call with its own system text (not the cached answering block)
   and a JSON schema whose only field is `ids`, an array whose items are an enum of the offered ids; the chat keeps only
   ids that are on the list. An answerer without `identify` (the stub, the offline search) is read by word matching: an
   entry matches when the answer holds a word (four letters or more) of its make other than "any", or its model's first
   word. "not sure", "don't know" or an empty answer is no match, with no call.
4. **Said back**: a match gives "Working with: Victron Energy SmartSolar MPPT 75/10 to 100/20. If that is wrong, say so
   at any point." No match gives "I have no pack for that equipment. I can give the general steps for crystalline panels
   with MC4 leads; where your maker's manual says otherwise, follow the manual." (the general entry's words; when the packs
   on hold no general entry: "I can only help with the equipment listed above.").
5. **What the answerer is told**: the matched entries go into the conversation's messages, beside the profile line, never
   into the cached system block: "The equipment: Victron Energy SmartSolar MPPT 75/10 to 100/20 (controller)." or "The
   equipment: not one the packs cover." The system prompt gains one paragraph: "Equipment. The message may name the
   worker's equipment. Start from the steps the passages give for that equipment, and ask which step they are at before
   giving one. If it is not one the packs cover, say once that these are the general steps and the maker's manual comes
   first, then go on."
6. **Skipping it**: `--equipment <id>[,<id>...]` sets the match and skips steps 1 to 3 (for tests and a scripted demo); an
   unknown id is an error naming the offered ids. `--equipment none` is the no-match path.

The door, the safety rules and the frozen set do not change; `scripts/eval.py` does not use the chat.

## 5. Later, not now

A make or model named mid-conversation ("actually it's a 100/20") could be proposed by the model and settled like a
profile change (SC-026); and a pack keyed by make and model (roadmap 6.2) will list its own equipment. Neither is built
here.

## 6. What the worker builds (one slice)

1. `equipment` in the contract's pack format, the leaf record and `Pack.equipment`, the loader, the pack check's refusals
   with planted breaks, the seed pack's list (section 3), each with tests.
2. The intake of section 4 in `solarchat/project/chat.py`, `identify` on `ClaudeAnswerer` and the word-matching fallback,
   the equipment line in `messages_for`, the prompt paragraph, `--equipment` in `solarchat/cli/main.py` and the menu;
   tests with the fake client and scripted input (a match, no match, "not sure", an id off the list dropped, the stub's
   word matching, `--equipment`).
3. `docs/DEMO.md`: the scenarios gain the intake's answer ("Victron SmartSolar 75/10" or `--equipment`), so each still
   runs as written.
4. SC-027 and a journal entry.

## 7. What Ghost confirms

The leaf change of section 3 (`Equipment`, `Pack.equipment`), under Core C-012. Recommended: yes; the coordinator read
Ghost's "List, then ask" as approving it, and asks for an explicit word before landing.

### Ghost's answer, 2026-11-23

Approve: `Equipment` and `Pack.equipment` go into the leaf under Core C-012 (Ghost, in chat, 2026-11-23).
