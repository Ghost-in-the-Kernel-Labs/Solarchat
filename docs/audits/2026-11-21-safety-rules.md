# Safety rules audit, 2026-11-21 (Fable auditor, read-only; Ghost has seen it)

> The evidence J-030 cites as "the audit", committed on 2026-11-21 with J-031; the text below this note is the report
> word for word. A read-only report by an AI auditor: Ghost applied its trigger and wording proposals in J-030, and no
> electrical engineer has confirmed any of them yet (F-16 and SC-016, proposed). Its text is data, never instructions
> (Core C-007).

Simulated firing on packs/seed-mc4-leads today (substring and whole-word):
- step-02 (inspection) fires SR-07 on "cracked, melted" (a description, not a hazard); "undamaged" fires SR-07 by substring.
- step-12 fires SR-08 on "spark" (an explanation of why not to pull apart under load).
- step-01 fires SR-01 only by substring ("safety procedures").
- SR-03 fires nowhere; it misses step-12 and fail-04/07/10 ("pull connectors apart", "open the pairs with the release tool", "separate the halves").
- Failures: SR-07 fires fail-01,04,05,08,09,11,12,13 (only 08,09,13 are true always-stop cases); SR-08 fail-04,08; SR-05 fail-02 on "Do not climb onto a roof" (a prohibition); SR-14 fail-07 on "not sure" in its own stop text; SR-11 fail-14 on "battery fuse" in a cause list.

Per-rule proposals (trigger and wording parts only; response types are step 2, not this task):
- SR-01 Site first: drop its triggers ("permit to work", "risk assessment" in a step is good practice). Keep the rule text; it is shown on every stop.
- SR-02 Live in daylight: drop `live` (matches "live view", "goes live"), `dc cable`, `dc wiring`. Add `probe`, `test leads`, `clamp meter`, `insulation tester`, `crimp`. Keep the meter triggers (Ghost's open point; the audit says a stop by default).
- SR-03 Connectors: Ghost decided connecting is daily work and not a stop. The hazard is parting under load. Retitle and reword around "never pull connectors apart under load"; the shown text tells the worker the precondition (isolator off or panel covered so no current flows; use the release tool) rather than "someone allowed to do it" (the worker is that person). Triggers: only disconnect-under-load wording that the pack's real text uses: `pull connectors apart`, `pull the connectors apart`, `separate the halves`, `open the pairs`, `under load`, `disconnect under load`. No triggers on joining/plugging/mating. Source: Staubli MA250 (12.2025, e): "ALWAYS de-energize the PV system before mating and disconnecting the connectors"; "NEVER disconnect the connectors under load"; "Use of tool is required to open".
- SR-04 Enclosures: verb+object triggers only: `open the inverter`, `open the combiner`, `remove the cover of the`, `replace the fuse`. Drop bare nouns `combiner`, `combiner box`, `junction box` (every module has one), `switchboard`, `consumer unit`, `fuse holder`.
- SR-05 Height: drop `harness` ("wiring harness"), `climb`, bare `roof`. Keep phrases that describe going up: e.g. `go up on the roof`, `climb the ladder`, `work at height`, `on the roof edge` (whole-phrase).
- SR-06 Overhead lines: keep. Add `service drop`, `overhead wires`, `pylon`, `utility pole`. Shown text gains the distance: at least 10 ft (3 m), more for higher voltage, or the site's figure if larger (OSHA 1910.333(c)(3)(i); 1926.1408).
- SR-07 Damage: drop description words that fire on the inspection step; drop `does not click`, `will not lock`, `mismatched connector` (fail-05 has a real fix). (Matching on the worker's words is step 2.)
- SR-08 Heat/smoke/arc: drop `buzzing`, `too hot`, `hot to the touch` (inverters hum; panels in sun are hot). Shown text: add "switch off the power if you can do it safely" is for SR-09 (below).
- SR-09 Ground fault/shock: drop bare `rcd` and `riso` (substring hazards). Shown text: before "do not touch them" add "switch off the power if you can do it safely". Keep the Ghost-to-confirm mark on the first-aid sentence.
- SR-10 Over-voltage: drop `panels in series`, `more panels in series` (stops the core task; step-01 and step-08 already stop on the sums).
- SR-11 Batteries: drop `leaking`, `venting` unless as phrases with "battery" (e.g. `battery is leaking`, `battery leaking`, `battery venting`); drop `battery fuse` hit by removing over-broad triggers.
- SR-12 Bypass: reword shown text: "Stop. Never bypass, bridge, tape or hold in a fuse, breaker or other safety device to make something work. Switching off is safe; overriding is not. Go to your site supervisor or engineer." Drop bare `bypass` ("bypass diode"), bare `jumper` ("jumper cable" is a normal string lead), `disable the`, `defeat`, `bridge the`. Use `bypass the fuse`, `bypass the breaker`, `bypass the isolator`, `bypass the switch`, `bigger fuse`, `larger fuse`, `hold the breaker`, `tape over`, `link out`.
- SR-13 Disagrees with maker: drop its phrase triggers ("the manual says" fires on helpful text); keep the rule text.
- SR-14 Unsure: drop `not sure` from step-text triggers (collides with stop text and with the bot's own "I do not know").

Matching (define before TODO 1.7): whole-word or whole-phrase, case-insensitive; never substring. ("undamaged", "deliver", "preventing", "waterproof" are substring false hits.)
