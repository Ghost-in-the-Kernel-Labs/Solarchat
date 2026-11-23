# The safety rules, version 1

Written by `scripts/safety_rules_doc.py` from `solarchat/safety/rules.json`; do not edit here: change the data and run the script.

**The site's own safety procedures come first.** These rules never replace the site's procedures, permits, training, the equipment maker's instructions or the site supervisor's instructions. Where they differ, the site wins, and the worker stops and asks (SR-01).

**The rules sit outside every pack.** They are Solarchat's own text, kept in the `safety` module, never in a knowledge pack. They apply in every mode. A pack may add more places to stop; it cannot name, remove, reword or switch off a rule, and the pack check refuses a pack that tries (`docs/CONTRACT.md` HAD-04, `docs/ROADMAP.md` P-17).

They are written for the newest contractor on a site (F-01): short, plain words for a phone and a tired person (P-18). When one applies, Hadley gives the rule's response (SC-015): a **warn** shows the words below and the walk continues, a **stop** shows them with why, the safe next action and what to bring the supervisor, an **emergency** tells the worker to step back and call for help. Each rule's triggers are the words that, found in a step's text, make it apply; the walker uses them from TODO 2.3, the answers from 1.9. Each rule's latest change is shown (SC-016); a point marked **Engineer to confirm** waits for the engineer's final review (F-16), and an entry whose role is not an electrical engineer is Ghost's or the agent's judgement, pending that review.

Status: a draft for Ghost to read (TODO 1.3 stays open until Ghost has read it). The sources are public guidance the rules rest on; no rule claims more than its sources say, and none is a substitute for training.

## The rules at a glance

- SR-01 The site's own safety procedures and your supervisor come first
- SR-02 A panel is live whenever light falls on it
- SR-03 Never pull connectors apart under load
- SR-04 Do not open an inverter, combiner, battery or other electrical enclosure
- SR-05 Work at height or on a roof
- SR-06 Keep well away from overhead power lines
- SR-07 Damaged, burnt, melted, wet or corroded parts
- SR-08 Heat, a burning smell, smoke, sparks or arcing
- SR-09 An earth (ground) fault or an electric shock
- SR-10 A voltage above what a device is rated for
- SR-11 Batteries
- SR-12 Never bypass or switch off a protective device
- SR-13 A step that disagrees with the maker's instructions or the site's procedures
- SR-14 When you are unsure
- SR-15 Connecting to the grid or a building's mains

## SR-01 The site's own safety procedures and your supervisor come first

**When it applies:** Always. Whenever a step, a pack or Hadley says anything that differs from the site's own safety procedures, permits or the supervisor's instructions, the site wins.

**The worker is shown:**

> Your site's own safety rules and your supervisor's instructions come first. If anything here is different from them, follow the site, not this. Stop now. Go to your site supervisor or engineer.

**Response:** stop

**Triggers:** `ignore the site rules`, `ignore the site procedures`, `ignore your supervisor`

**Latest change:** 2026-11-21, Ghost (maintainer): Triggers match whole words and phrases, and the rule's triggers and wording follow the audit, applied on Ghost's word; engineer to confirm. Evidence: docs/audits/2026-11-21-safety-rules.md; J-030. Pending engineer.

**Sources:**

- [HSE: Electrical safety at work, frequently asked questions (follow the maker's instructions and local safety rules)](https://www.hse.gov.uk/electricity/faq.htm)
- [OSHA: Green Job Hazards, Solar Energy](https://www.osha.gov/green-jobs/solar)

## SR-02 A panel is live whenever light falls on it

**When it applies:** A step has you touch, cut, strip, open or test any wire, terminal or bare metal of a panel, a string or its wiring. A panel makes voltage in daylight, even in cloud, and its DC side stays live when the inverter or the mains is switched off.

**The worker is shown:**

> Stop. Treat every panel and its wiring as live in daylight. Switching off the inverter or the mains does not make it safe. Do not touch, cut or test it yourself. Go to your site supervisor or engineer.

**Response:** stop

**Triggers:** `energised`, `energized`, `bare wire`, `bare copper`, `exposed conductor`, `cut the cable`, `cut the wire`, `strip the cable`, `strip the wire`, `measure the voltage`, `test the voltage`, `multimeter`, `voltmeter`, `probe`, `test leads`, `clamp meter`, `insulation tester`

**Latest change:** 2026-11-23, Ghost (maintainer): Added holds: words that keep this rule's topic closed for the rest of a conversation once it has stopped a worker, so a follow-up about the same work is not offered a step (SC-028); no trigger or wording changed; engineer to confirm. Evidence: J-090; docs/designs/sticky-stops-and-proposal-guards.md. Pending engineer.

**Sources:**

- [Ontario: Firefighter guidance note 6-34, solar photovoltaic systems (panels stay energised while light reaches them)](https://www.ontario.ca/document/firefighter-guidance-notes/6-34-solar-photovoltaic-systems)
- [OSHA: Green Job Hazards, Solar Energy, Electrical](https://www.osha.gov/green-jobs/solar/electrical)
- [OSHA: Green Job Hazards, Solar Energy, Lockout/Tagout (cover panels; verify isolation before work)](https://www.osha.gov/green-jobs/solar/lockout-tagout)
- [HSE: Electrical safety at work, frequently asked questions (prove conductors dead before work)](https://www.hse.gov.uk/electricity/faq.htm)

**Engineer to confirm:** Whether measuring a voltage with a meter is a stop for the newest contractor. The draft says yes (the triggers 'multimeter', 'measure the voltage'), because a meter on a live string is live work; if crews are trained to measure, this trigger will stop many troubleshooting flows.

## SR-03 Never pull connectors apart under load

**When it applies:** A step has you pull a panel's connectors, a string or a DC lead apart while current can flow. Pulling a connector apart under load can draw an arc that burns. Joining and plugging in connectors is daily work and is not a stop (Ghost, 2026-11-21).

**The worker is shown:**

> Stop. Do not part connectors yourself. Opening a pair needs the panel made safe first and the release tool made for it, and connectors pulled apart under load can spark and burn. Go to your site supervisor or engineer.

**Response:** stop

**Triggers:** `pull connectors apart`, `pull the connectors apart`, `separate the halves`, `open the pairs`, `open the connectors`, `under load`, `disconnect under load`

**Latest change:** 2026-11-23, Ghost (maintainer): Added holds: words that keep this rule's topic closed for the rest of a conversation once it has stopped a worker, so a follow-up about the same work is not offered a step (SC-028); no trigger or wording changed; engineer to confirm. Evidence: J-090; docs/designs/sticky-stops-and-proposal-guards.md. Pending engineer.

**Sources:**

- [Staubli: MC4 branch connector assembly instructions MA250 (12.2025, e: always de-energise the PV system before mating and disconnecting; never disconnect the connectors under load; a tool is required to open)](https://www.staubli.com/content/dam/spot/PV_MA250-en.pdf)
- [Staubli: assembly instructions MA263 (de-energise before mating or unmating)](https://staubli.com/content/dam/spot/PV_MA263-en.pdf)
- [OSHA: Green Job Hazards, Solar Energy, Lockout/Tagout (cover the solar panels; library: osha-solar-lockout-tagout)](https://www.osha.gov/green-jobs/solar/lockout-tagout)

## SR-04 Do not open an inverter, combiner, battery or other electrical enclosure

**When it applies:** A step has you open, unscrew or take the cover off an inverter, combiner box, junction box, isolator, fuse holder, battery cabinet, switchboard or any other box that holds wiring.

**The worker is shown:**

> Stop. Do not open this box. Parts inside can stay live and hold a charge even when switched off. Only someone authorised may open it. Go to your site supervisor or engineer.

**Response:** stop

**Triggers:** `open the inverter`, `replace the fuse`, `remove the cover`, `open the enclosure`, `open the cover`, `open the combiner`, `remove the cover of the`

**Latest change:** 2026-11-23, Ghost (maintainer): Added holds: words that keep this rule's topic closed for the rest of a conversation once it has stopped a worker, so a follow-up about the same work is not offered a step (SC-028); no trigger or wording changed; engineer to confirm. Evidence: J-090; docs/designs/sticky-stops-and-proposal-guards.md. Pending engineer.

**Sources:**

- [HSE: Electrical safety at work, frequently asked questions (isolate, lock off, release stored energy, prove dead; competence)](https://www.hse.gov.uk/electricity/faq.htm)
- [OSHA: Green Job Hazards, Solar Energy, Lockout/Tagout (only authorised employees lock out equipment)](https://www.osha.gov/green-jobs/solar/lockout-tagout)

## SR-05 Work at height or on a roof

**When it applies:** A step has you go onto a roof, a ladder, a scaffold or a frame, or near an edge, skylight or roof hatch, or carry a panel up. There is no safe height to fall from; the site sets the fall protection.

**The worker is shown:**

> Stop. Do not go up or near an edge until your supervisor has shown you the fall protection for this job and it is in place. Never climb a ladder carrying a panel. Go to your site supervisor or engineer.

**Response:** stop

**Triggers:** `rooftop`, `ladder`, `scaffold`, `at height`, `skylight`, `roof hatch`, `roof edge`, `go up on the roof`, `climb the ladder`, `work at height`, `on the roof edge`, `on the roof`, `onto the roof`, `up on the roof`, `get up there`, `climb up`, `harness`

**Latest change:** 2026-11-23, Ghost (maintainer): Added holds: words that keep this rule's topic closed for the rest of a conversation once it has stopped a worker, so a follow-up about the same work is not offered a step (SC-028); no trigger or wording changed; engineer to confirm. Evidence: J-090; docs/designs/sticky-stops-and-proposal-guards.md. Pending engineer.

**Sources:**

- [OSHA: Green Job Hazards, Solar Energy, Falls (library: osha-solar-falls)](https://www.osha.gov/green-jobs/solar/falls)
- [OSHA: 29 CFR 1910 Subpart D, walking-working surfaces (1910.23 skylights; 4 feet or more in maintenance work; library: osha-1910-d)](https://www.ecfr.gov/current/title-29/part-1910/subpart-D)
- [OSHA: 29 CFR 1926 Subpart M, fall protection in construction (6 feet or more; library: osha-1926-m)](https://www.ecfr.gov/current/title-29/part-1926/subpart-M)
- [HSE: Work at height](https://www.hse.gov.uk/work-at-height/)

## SR-06 Keep well away from overhead power lines

**When it applies:** A step has you work, lift a panel, raise a ladder or move a tool or machine anywhere near an overhead power line.

**The worker is shown:**

> Stop. Do not work, lift or raise anything near an overhead power line. It can kill without being touched. Stay at least 10 feet (3 metres) away, and farther for higher voltage, or the site's own distance if it is greater. Go to your site supervisor or engineer.

**Response:** stop

**Triggers:** `overhead line`, `overhead lines`, `power line`, `power lines`, `overhead cable`, `service drop`, `overhead wires`, `pylon`, `utility pole`

**Latest change:** 2026-11-21, Ghost (maintainer): Triggers match whole words and phrases, and the rule's triggers and wording follow the audit, applied on Ghost's word; engineer to confirm. Evidence: docs/audits/2026-11-21-safety-rules.md; J-030. Pending engineer.

**Sources:**

- [OSHA: Green Job Hazards, Solar Energy, Electrical (keep at least 10 feet from overhead lines; library: osha-solar-electrical)](https://www.osha.gov/green-jobs/solar/electrical)
- [OSHA: 29 CFR 1910.333(c)(3)(i), selection and use of work practices (overhead lines: keep a safe distance, at least 10 feet for lines up to 50 kV, more above; library: osha-1910-s)](https://www.osha.gov/laws-regs/regulations/standardnumber/1910/1910.333)
- [OSHA: 29 CFR 1926.1408, cranes and derricks in construction, power line safety (up to 350 kV; library: osha-1926-cranes-power-lines)](https://www.osha.gov/laws-regs/regulations/standardnumber/1926/1926.1408)

**Engineer to confirm:** This rule is beyond the brief's list (added because OSHA names overhead lines among solar workers' electrical hazards). The audit of 2026-11-21 found the hazard real on solar sites: perimeter lines and service drops at the site, and OSHA's Fort Riley 2018 citation. The words now give the distance (at least 10 feet, OSHA 1910.333(c)(3)(i) and 1926.1408; the site's own distance if greater). Keep, change or drop.

## SR-07 Damaged, burnt, melted, wet or corroded parts

**When it applies:** A connector, cable, panel or box is cracked, cut, crushed, burnt, scorched, melted, discoloured, corroded, wet inside, or has copper showing. The triggers fire only on text that says such a part is there, not on a step that tells you what to look for.

**The worker is shown:**

> Stop. Do not touch, use or reconnect a damaged, burnt, melted, wet or corroded part. It can be live and can start a fire. Keep others away. Go to your site supervisor or engineer.

**Response:** stop

**Triggers:** `broken glass`, `broken panel`, `cracked panel`, `heat-damaged`, `damaged connector`, `damaged cable`, `burnt connector`, `burnt cable`, `melted connector`, `corroded connector`, `wet inside`, `copper showing`, `frayed`, `chewed`, `broken`, `glass is cracked`, `is cracked`

**Latest change:** 2026-11-22, Ghost (maintainer): Trigger "glass is broken" becomes "broken" (safe-16); and the rule fires on the worker's words only, never on a passage's text; engineer to confirm. Evidence: J-079; docs/designs/worker-words.md. Pending engineer.

**Sources:**

- [UK government (BRE): Fire incidents involving solar panels (connectors and poor installation among the causes)](https://www.gov.uk/government/publications/fire-incidents-involving-solar-panels)
- [Staubli: MC4 branch connector assembly instructions MA250](https://www.staubli.com/content/dam/spot/PV_MA250-en.pdf)

## SR-08 Heat, a burning smell, smoke, sparks or arcing

**When it applies:** Anything smells of burning, smokes, sparks, crackles or shows an arc or flame. A humming inverter, or a panel that is hot in the sun, is normal and is not a stop.

**The worker is shown:**

> Stop. Step back and do not touch it. Keep others away. If there is fire or smoke, follow the site's emergency procedure. Go to your site supervisor or engineer.

**Response:** emergency

**Triggers:** `smoke`, `smoking`, `burning smell`, `smells of burning`, `sparks`, `sparking`, `arcing`, `crackling`, `flame`, `flames`, `on fire`, `smells burnt`, `burnt smell`

**Latest change:** 2026-11-22, Ghost (maintainer): The rule fires on the worker's words only, never on a passage's text; engineer to confirm. Evidence: J-079; docs/designs/worker-words.md. Pending engineer.

**Sources:**

- [UK government (BRE): Fire incidents involving solar panels (electrical arcing the likely ignition)](https://www.gov.uk/government/publications/fire-incidents-involving-solar-panels)
- [OSHA: Green Job Hazards, Solar Energy, Electrical (arc flash)](https://www.osha.gov/green-jobs/solar/electrical)

## SR-09 An earth (ground) fault or an electric shock

**When it applies:** A device shows an earth fault, ground fault, insulation or isolation fault, or a protective device trips; or someone feels a tingle or a shock from a frame, panel or box. A fault can make metal live that should not be.

**The worker is shown:**

> Stop. Do not touch the frames, panels or boxes. A fault may have made metal live. If someone has had a shock, call for help and first aid at once, switch off the power if you can do it safely, and do not touch them while they may still be touching it. Go to your site supervisor or engineer. If you had the shock yourself, get medical attention even if you feel fine.

**Response:** emergency

**Triggers:** `earth fault`, `ground fault`, `insulation fault`, `isolation fault`, `insulation resistance`, `earth leakage`, `gfdi`, `tingle`, `electric shock`, `got a shock`, `loose earth`, `missing earth`

**Latest change:** 2026-11-23, Ghost (maintainer): One sentence appended to the words: if you had the shock yourself, get medical attention even if you feel fine, trimmed to what the added source states; response, triggers and the rest of the words unchanged (R13); engineer to confirm. Evidence: J-089; the blind evaluation of 2026-11-23 and Ghost's approval in chat, 2026-11-23. Pending engineer.

**Sources:**

- [Fluke: What is a DC ground fault in a PV system?](https://www.fluke.com/en-gb/learn/blog/renewable-energy/what-is-a-dc-ground-fault-in-a-pv-system)
- [OSHA: Green Job Hazards, Solar Energy, Electrical (shock and burns when connecting panels)](https://www.osha.gov/green-jobs/solar/electrical)
- [Better Health Channel (Victoria, Australia): Electric shock (a person who has had a shock may appear unharmed but should still receive medical attention)](https://www.betterhealth.vic.gov.au/health/healthyliving/electric-shock)

**Engineer to confirm:** The first-aid sentence (call for help, do not touch a person who may still be touching something live) is common first-aid practice but none of the sources above states it; the site's own first-aid arrangements apply. Keep, reword or source it. The same goes for SR-08's line to follow the site's emergency procedure on fire or smoke. The last sentence (J-089, R13), medical attention for the person who had the shock themselves, is sourced to the Better Health Channel page for that clause only; Ghost's wording also said to stop work, step away, not touch it again and tell the supervisor, and no page fetched for J-089 states those, so they were left out (the rule's first words already say Stop and go to the supervisor).

## SR-10 A voltage above what a device is rated for

**When it applies:** The panels' voltage, or the string's, is or could be above the device's highest input voltage. A panel's voltage rises in the cold, so a string that fits on a warm day may not on a cold morning.

**The worker is shown:**

> Stop. Do not connect. Too high a voltage can destroy the device and start a fire, and panels give more volts when cold. Go to your site supervisor or engineer.

**Response:** stop

**Triggers:** `above the maximum`, `exceeds the maximum`, `above the rating`, `over the rating`, `higher than the rating`, `higher than the maximum`

**Latest change:** 2026-11-21, Ghost (maintainer): applies_when no longer names joining panels in series, which J-041 stopped firing on; pending engineer review (F-16). Evidence: J-044. Pending engineer.

**Sources:**

- [Victron Energy: SmartSolar MPPT 150/70 to 250/100 manual, technical specifications (absolute maximum PV voltage in the coldest conditions)](https://www.victronenergy.com/media/pg/Manual_SmartSolar_MPPT_150-70_up_to_250-100_VE.Can/en/technical-specifications.html)

## SR-11 Batteries

**When it applies:** A step has you connect, disconnect or work on battery terminals, battery cables or a battery bank; or a battery is swollen, hot, leaking, hissing or smells.

**The worker is shown:**

> Stop. Do not work on battery terminals or cables, and keep away from a battery that is swollen, hot, leaking, hissing or smells. A battery can burn, explode or give off toxic gas, and it cannot be switched off. Go to your site supervisor or engineer.

**Response:** stop

**Triggers:** `battery terminal`, `battery terminals`, `battery cable`, `battery cables`, `battery bank`, `swollen`, `bulging`, `hissing`, `battery is leaking`, `battery leaking`, `battery is venting`, `battery venting`

**Latest change:** 2026-11-23, Ghost (maintainer): Added holds: words that keep this rule's topic closed for the rest of a conversation once it has stopped a worker, so a follow-up about the same work is not offered a step (SC-028); no trigger or wording changed; engineer to confirm. Evidence: J-090; docs/designs/sticky-stops-and-proposal-guards.md. Pending engineer.

**Sources:**

- [OSHA: Lithium-ion Battery Safety, Hazards (heat, venting gas or smoke; toxic gases; library: osha-lithium-ion-hazards)](https://www.osha.gov/lithium-ion-battery-safety/hazards)

## SR-12 Never bypass or switch off a protective device

**When it applies:** A step has you bypass, bridge, remove, tape over or switch off a fuse, breaker, isolator, RCD, earth connection, shutdown switch or other protective device so that something works.

**The worker is shown:**

> Stop. Never bypass, bridge, tape or hold in a fuse, breaker or other safety device to make something work. Switching off is safe; overriding is not. Go to your site supervisor or engineer.

**Response:** stop

**Triggers:** `bypass the fuse`, `bypass the breaker`, `bypass the isolator`, `bypass the switch`, `link out`, `tape over`, `remove the fuse`, `larger fuse`, `bigger fuse`, `hold the breaker`

**Latest change:** 2026-11-21, Ghost (maintainer): Triggers match whole words and phrases, and the rule's triggers and wording follow the audit, applied on Ghost's word; engineer to confirm. Evidence: docs/audits/2026-11-21-safety-rules.md; J-030. Pending engineer.

**Sources:**

- [HSE: Electrical safety at work, frequently asked questions (follow the maker's instructions and local safety rules)](https://www.hse.gov.uk/electricity/faq.htm)
- [OSHA: Green Job Hazards, Solar Energy, Lockout/Tagout](https://www.osha.gov/green-jobs/solar/lockout-tagout)

**Engineer to confirm:** This rule is beyond the brief's list (it grows out of 'a step that contradicts the maker's instructions'). Keep, change or drop.

## SR-13 A step that disagrees with the maker's instructions or the site's procedures

**When it applies:** A step says something different from the maker's manual, the label on the equipment or the site's own procedures, or two instructions disagree.

**The worker is shown:**

> Stop. If this step is different from the maker's instructions, the label or your site's procedures, do not do it. Go to your site supervisor or engineer.

**Response:** stop

**Triggers:** `does not match the manual`, `different from the manual`, `not in the manual`, `does not match the label`, `different from the label`

**Latest change:** 2026-11-21, Ghost (maintainer): Triggers match whole words and phrases, and the rule's triggers and wording follow the audit, applied on Ghost's word; engineer to confirm. Evidence: docs/audits/2026-11-21-safety-rules.md; J-030. Pending engineer.

**Sources:**

- [HSE: Electrical safety at work, frequently asked questions (follow the maker's instructions and local safety rules)](https://www.hse.gov.uk/electricity/faq.htm)
- [Staubli: MC4 branch connector assembly instructions MA250](https://www.staubli.com/content/dam/spot/PV_MA250-en.pdf)

## SR-14 When you are unsure

**When it applies:** The worker is not sure what to do, has not been trained for the step, or what they see does not look like the step says it should.

**The worker is shown:**

> Stop. If you are not sure, do not guess. It is always right to stop and ask. Go to your site supervisor or engineer.

**Response:** stop

**Triggers:** `unsure`, `not trained`, `never done`, `does not look like`, `doesn't look like`, `unexpected`

**Latest change:** 2026-11-22, Ghost (maintainer): Triggers removed: "do not know" and "don't know"; "I don't know which lead is positive" is a question, answered from the packs or with "I do not know" (HAD-03), not a stop; "not trained", "never done" and "unsure" still stop; engineer to confirm. Evidence: J-075; docs/designs/worker-words.md. Pending engineer.

**Sources:**

- [HSE: Electrical safety at work, frequently asked questions (competence for the specific work)](https://www.hse.gov.uk/electricity/faq.htm)
- [OSHA: Green Job Hazards, Solar Energy](https://www.osha.gov/green-jobs/solar)

## SR-15 Connecting to the grid or a building's mains

**When it applies:** The worker asks to connect solar to the grid or to a building's mains supply, or to feed power in or net meter. This is work for a licensed electrician and usually needs the network operator's permission before it is connected.

**The worker is shown:**

> Stop. Connecting solar to the grid or a building's mains is work for a licensed electrician, and usually needs the network operator's permission. Do not do it. Go to your site supervisor or engineer.

**Response:** stop

**Triggers:** `to the grid`, `grid tie`, `grid-tie`, `grid-tied`, `feed in`, `net meter`, `net metering`, `to the mains`, `into the mains`

**Latest change:** 2026-11-23, Ghost (maintainer): Added holds: words that keep this rule's topic closed for the rest of a conversation once it has stopped a worker, so a follow-up about the same work is not offered a step (SC-028); no trigger or wording changed; engineer to confirm. Evidence: J-090; docs/designs/sticky-stops-and-proposal-guards.md. Pending engineer.

**Sources:**

- [NSW Government: Guide to solar panels (installation must be by a licensed builder or licensed electrical contractor; you must get approval from the electricity network owner before connecting your solar system to the grid)](https://www.nsw.gov.au/housing-and-construction/building-or-renovating-a-home/during-building-process/guide-to-solar-panels)
- [Welsh Government: Connecting on-site generation to the grid, technical note (distribution network operators must authorise all installation of generating stations and battery storage systems)](https://www.gov.wales/connecting-site-generation-grid-technical-note-html)

**Engineer to confirm:** Both sources are government pages from New South Wales and Wales, not from the country the pilot runs in. The claims are by country: a licensed electrician (NSW), the network operator's permission (NSW; Wales), and the words say usually because a small UK system may only need notice, not prior permission. Replace them with the national regulator's and network operator's pages for the pilot's country, and confirm who counts as licensed there.
