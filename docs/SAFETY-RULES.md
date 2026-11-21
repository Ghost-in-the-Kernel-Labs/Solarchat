# The safety rules, version 1

Written by `scripts/safety_rules_doc.py` from `solarchat/safety/rules.json`; do not edit here: change the data and run the script.

**The site's own safety procedures come first.** These rules never replace the site's procedures, permits, training, the equipment maker's instructions or the site supervisor's instructions. Where they differ, the site wins, and the worker stops and asks (SR-01).

**The rules sit outside every pack.** They are Solarchat's own text, kept in the `safety` module, never in a knowledge pack. They apply in every mode. A pack may add more places to stop; it cannot name, remove, reword or switch off a rule, and the pack check refuses a pack that tries (`docs/CONTRACT.md` HAD-04, `docs/ROADMAP.md` P-17).

They are written for the newest contractor on a site (F-01): short, plain words for a phone and a tired person (P-18). When one applies, Hadley stops the current step, shows the words below, and sends the worker to the site supervisor or engineer. Each rule's triggers are the words that, found in a step's text, make it apply; the walker uses them from TODO 1.7. A point marked **Ghost to confirm** is the agent's draft reading, not yet Ghost's.

Status: a draft for Ghost to read (TODO 1.3 stays open until Ghost has read it). The sources are public guidance the rules rest on; no rule claims more than its sources say, and none is a substitute for training.

## The rules at a glance

- SR-01 The site's own safety procedures and your supervisor come first
- SR-02 A panel is live whenever light falls on it
- SR-03 Never pull connectors apart while current can flow
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

## SR-01 The site's own safety procedures and your supervisor come first

**When it applies:** Always. Whenever a step, a pack or Hadley says anything that differs from the site's own safety procedures, permits or the supervisor's instructions, the site wins.

**The worker is shown:**

> Your site's own safety rules and your supervisor's instructions come first. If anything here is different from them, follow the site, not this. Stop now. Go to your site supervisor or engineer.

**Triggers:** `permit to work`, `method statement`, `site procedure`, `site procedures`, `site rules`, `safety procedure`, `risk assessment`

**Sources:**

- [HSE: Electrical safety at work, frequently asked questions (follow the maker's instructions and local safety rules)](https://www.hse.gov.uk/electricity/faq.htm)
- [OSHA: Green Job Hazards, Solar Energy](https://www.osha.gov/green-jobs/solar)

## SR-02 A panel is live whenever light falls on it

**When it applies:** A step has you touch, cut, strip, open or test any wire, terminal or bare metal of a panel, a string or its wiring. A panel makes voltage in daylight, even in cloud, and its DC side stays live when the inverter or the mains is switched off.

**The worker is shown:**

> Stop. Treat every panel and its wiring as live in daylight. Switching off the inverter or the mains does not make it safe. Do not touch, cut or test it yourself. Go to your site supervisor or engineer.

**Triggers:** `live`, `energised`, `energized`, `bare wire`, `bare copper`, `exposed conductor`, `cut the cable`, `cut the wire`, `strip the cable`, `strip the wire`, `measure the voltage`, `test the voltage`, `multimeter`, `voltmeter`, `dc cable`, `dc wiring`

**Sources:**

- [Ontario: Firefighter guidance note 6-34, solar photovoltaic systems (panels stay energised while light reaches them)](https://www.ontario.ca/document/firefighter-guidance-notes/6-34-solar-photovoltaic-systems)
- [OSHA: Green Job Hazards, Solar Energy, Electrical](https://www.osha.gov/green-jobs/solar/electrical)
- [OSHA: Green Job Hazards, Solar Energy, Lockout/Tagout (cover panels; verify isolation before work)](https://www.osha.gov/green-jobs/solar/lockout-tagout)
- [HSE: Electrical safety at work, frequently asked questions (prove conductors dead before work)](https://www.hse.gov.uk/electricity/faq.htm)

**Ghost to confirm:** Whether measuring a voltage with a meter is a stop for the newest contractor. The draft says yes (the triggers 'multimeter', 'measure the voltage'), because a meter on a live string is live work; if crews are trained to measure, this trigger will stop many troubleshooting flows.

## SR-03 Never pull connectors apart while current can flow

**When it applies:** A step has you unplug, separate or disconnect a panel's connectors, a string or a DC lead. Pulling a connector apart under load can draw an arc that burns.

**The worker is shown:**

> Stop. Do not pull the connectors apart. Under load they can spark and burn you. The system must be made safe first, by someone allowed to do it. Go to your site supervisor or engineer.

**Triggers:** `unplug`, `disconnect the connector`, `disconnect the connectors`, `pull the connectors apart`, `separate the connectors`, `disconnect the string`, `disconnect the panel`, `disconnect the lead`

**Sources:**

- [Staubli: MC4 branch connector assembly instructions MA250 (never disconnect under load)](https://www.staubli.com/content/dam/spot/PV_MA250-en.pdf)
- [Staubli: assembly instructions MA263 (de-energise before mating or unmating)](https://staubli.com/content/dam/spot/PV_MA263-en.pdf)

**Ghost to confirm:** Whether plugging a connector together (not only pulling one apart) is also a stop. The draft stops only on disconnecting; the makers' instructions say to de-energise before both.

## SR-04 Do not open an inverter, combiner, battery or other electrical enclosure

**When it applies:** A step has you open, unscrew or take the cover off an inverter, combiner box, junction box, isolator, fuse holder, battery cabinet, switchboard or any other box that holds wiring.

**The worker is shown:**

> Stop. Do not open this box. Parts inside can stay live and hold a charge even when switched off. Only someone authorised may open it. Go to your site supervisor or engineer.

**Triggers:** `open the inverter`, `inverter cover`, `combiner box`, `combiner`, `junction box`, `isolator cover`, `fuse holder`, `replace the fuse`, `battery cabinet`, `battery enclosure`, `switchboard`, `distribution board`, `consumer unit`, `breaker panel`, `remove the cover`, `open the enclosure`, `open the cover`

**Sources:**

- [HSE: Electrical safety at work, frequently asked questions (isolate, lock off, release stored energy, prove dead; competence)](https://www.hse.gov.uk/electricity/faq.htm)
- [OSHA: Green Job Hazards, Solar Energy, Lockout/Tagout (only authorised employees lock out equipment)](https://www.osha.gov/green-jobs/solar/lockout-tagout)

## SR-05 Work at height or on a roof

**When it applies:** A step has you go onto a roof, a ladder, a scaffold or a frame, or near an edge, skylight or roof hatch, or carry a panel up. There is no safe height to fall from; the site sets the fall protection.

**The worker is shown:**

> Stop. Do not go up or near an edge until your supervisor has shown you the fall protection for this job and it is in place. Never climb a ladder carrying a panel. Go to your site supervisor or engineer.

**Triggers:** `roof`, `rooftop`, `ladder`, `scaffold`, `at height`, `skylight`, `roof hatch`, `roof edge`, `harness`, `climb`

**Sources:**

- [OSHA: Green Job Hazards, Solar Energy, Falls](https://www.osha.gov/green-jobs/solar/falls)
- [HSE: Work at height](https://www.hse.gov.uk/work-at-height/)

## SR-06 Keep well away from overhead power lines

**When it applies:** A step has you work, lift a panel, raise a ladder or move a tool or machine anywhere near an overhead power line.

**The worker is shown:**

> Stop. Do not work, lift or raise anything near an overhead power line. It can kill without being touched. Go to your site supervisor or engineer.

**Triggers:** `overhead line`, `overhead lines`, `power line`, `power lines`, `overhead cable`

**Sources:**

- [OSHA: Green Job Hazards, Solar Energy, Electrical (keep at least 10 feet from overhead lines)](https://www.osha.gov/green-jobs/solar/electrical)

**Ghost to confirm:** This rule is beyond the brief's list (added because OSHA names overhead lines among solar workers' electrical hazards). The words give no distance: the site's own distance applies (OSHA's is at least 10 feet). Keep, change or drop.

## SR-07 Damaged, burnt, melted, wet or corroded parts

**When it applies:** A connector, cable, panel or box is cracked, cut, crushed, burnt, scorched, melted, discoloured, corroded, wet inside, or has copper showing, or a connector does not lock or does not match its other half.

**The worker is shown:**

> Stop. Do not touch, use or reconnect a damaged, burnt, melted, wet or corroded part. It can be live and can start a fire. Keep others away. Go to your site supervisor or engineer.

**Triggers:** `damaged`, `burnt`, `burned`, `scorched`, `melted`, `discoloured`, `discolored`, `cracked`, `broken glass`, `corroded`, `corrosion`, `water inside`, `wet inside`, `copper showing`, `frayed`, `chewed`, `does not click`, `will not lock`, `mismatched connector`

**Sources:**

- [UK government (BRE): Fire incidents involving solar panels (connectors and poor installation among the causes)](https://www.gov.uk/government/publications/fire-incidents-involving-solar-panels)
- [Staubli: MC4 branch connector assembly instructions MA250](https://www.staubli.com/content/dam/spot/PV_MA250-en.pdf)

## SR-08 Heat, a burning smell, smoke, sparks or arcing

**When it applies:** Anything is hotter than it should be, smells of burning, smokes, sparks, crackles, buzzes or shows an arc or flame.

**The worker is shown:**

> Stop. Step back and do not touch it. Keep others away. If there is fire or smoke, follow the site's emergency procedure. Go to your site supervisor or engineer.

**Triggers:** `smoke`, `smoking`, `burning smell`, `smells of burning`, `spark`, `sparks`, `sparking`, `arcing`, `crackling`, `buzzing`, `flame`, `flames`, `on fire`, `hot to the touch`, `too hot`

**Sources:**

- [UK government (BRE): Fire incidents involving solar panels (electrical arcing the likely ignition)](https://www.gov.uk/government/publications/fire-incidents-involving-solar-panels)
- [OSHA: Green Job Hazards, Solar Energy, Electrical (arc flash)](https://www.osha.gov/green-jobs/solar/electrical)

## SR-09 An earth (ground) fault or an electric shock

**When it applies:** A device shows an earth fault, ground fault, insulation or isolation fault, or a protective device trips; or someone feels a tingle or a shock from a frame, panel or box. A fault can make metal live that should not be.

**The worker is shown:**

> Stop. Do not touch the frames, panels or boxes. A fault may have made metal live. If someone has had a shock, call for help and first aid at once, and do not touch them while they may still be touching it. Go to your site supervisor or engineer.

**Triggers:** `earth fault`, `ground fault`, `insulation fault`, `isolation fault`, `insulation resistance`, `riso`, `earth leakage`, `rcd`, `gfdi`, `tingle`, `electric shock`, `got a shock`, `loose earth`, `missing earth`

**Sources:**

- [Fluke: What is a DC ground fault in a PV system?](https://www.fluke.com/en-gb/learn/blog/renewable-energy/what-is-a-dc-ground-fault-in-a-pv-system)
- [OSHA: Green Job Hazards, Solar Energy, Electrical (shock and burns when connecting panels)](https://www.osha.gov/green-jobs/solar/electrical)

**Ghost to confirm:** The first-aid sentence (call for help, do not touch a person who may still be touching something live) is common first-aid practice but none of the sources above states it; the site's own first-aid arrangements apply. Keep, reword or source it. The same goes for SR-08's line to follow the site's emergency procedure on fire or smoke.

## SR-10 A voltage above what a device is rated for

**When it applies:** The panels' voltage, or the string's, is or could be above the device's highest input voltage, or a step adds panels in series. A panel's voltage rises in the cold, so a string that fits on a warm day may not on a cold morning.

**The worker is shown:**

> Stop. Do not connect. Too high a voltage can destroy the device and start a fire, and panels give more volts when cold. Go to your site supervisor or engineer.

**Triggers:** `above the maximum`, `exceeds the maximum`, `above the rating`, `over the rating`, `higher than the rating`, `higher than the maximum`, `more panels in series`, `add a panel in series`, `panels in series`

**Sources:**

- [Victron Energy: SmartSolar MPPT 150/70 to 250/100 manual, technical specifications (absolute maximum PV voltage in the coldest conditions)](https://www.victronenergy.com/media/pg/Manual_SmartSolar_MPPT_150-70_up_to_250-100_VE.Can/en/technical-specifications.html)

## SR-11 Batteries

**When it applies:** A step has you connect, disconnect or work on battery terminals, battery cables or a battery bank; or a battery is swollen, hot, leaking, hissing or smells.

**The worker is shown:**

> Stop. Do not work on battery terminals or cables, and keep away from a battery that is swollen, hot, leaking, hissing or smells. A battery can burn, explode or give off toxic gas, and it cannot be switched off. Go to your site supervisor or engineer.

**Triggers:** `battery terminal`, `battery terminals`, `battery cable`, `battery cables`, `battery bank`, `battery fuse`, `swollen`, `bulging`, `leaking`, `hissing`, `venting`

**Sources:**

- [OSHA: Lithium-ion Battery Safety, Hazards (heat, venting gas or smoke; toxic gases)](https://www.osha.gov/lithium-ion-battery-safety/hazards)

## SR-12 Never bypass or switch off a protective device

**When it applies:** A step has you bypass, bridge, remove, tape over or switch off a fuse, breaker, isolator, RCD, earth connection, shutdown switch or other protective device so that something works.

**The worker is shown:**

> Stop. Never bypass, bridge or switch off a fuse, breaker, isolator or other safety device to make something work. Go to your site supervisor or engineer.

**Triggers:** `bypass`, `bridge the`, `jumper`, `link out`, `tape over`, `defeat`, `disable the`, `remove the fuse`, `larger fuse`, `bigger fuse`, `hold the breaker`

**Sources:**

- [HSE: Electrical safety at work, frequently asked questions (follow the maker's instructions and local safety rules)](https://www.hse.gov.uk/electricity/faq.htm)
- [OSHA: Green Job Hazards, Solar Energy, Lockout/Tagout](https://www.osha.gov/green-jobs/solar/lockout-tagout)

**Ghost to confirm:** This rule is beyond the brief's list (it grows out of 'a step that contradicts the maker's instructions'). Keep, change or drop.

## SR-13 A step that disagrees with the maker's instructions or the site's procedures

**When it applies:** A step says something different from the maker's manual, the label on the equipment or the site's own procedures, or two instructions disagree.

**The worker is shown:**

> Stop. If this step is different from the maker's instructions, the label or your site's procedures, do not do it. Go to your site supervisor or engineer.

**Triggers:** `does not match the manual`, `different from the manual`, `not in the manual`, `does not match the label`, `different from the label`, `the label says`, `the manual says`

**Sources:**

- [HSE: Electrical safety at work, frequently asked questions (follow the maker's instructions and local safety rules)](https://www.hse.gov.uk/electricity/faq.htm)
- [Staubli: MC4 branch connector assembly instructions MA250](https://www.staubli.com/content/dam/spot/PV_MA250-en.pdf)

## SR-14 When you are unsure

**When it applies:** The worker is not sure what to do, has not been trained for the step, or what they see does not look like the step says it should.

**The worker is shown:**

> Stop. If you are not sure, do not guess. It is always right to stop and ask. Go to your site supervisor or engineer.

**Triggers:** `not sure`, `unsure`, `do not know`, `don't know`, `not trained`, `never done`, `does not look like`, `doesn't look like`, `unexpected`

**Sources:**

- [HSE: Electrical safety at work, frequently asked questions (competence for the specific work)](https://www.hse.gov.uk/electricity/faq.htm)
- [OSHA: Green Job Hazards, Solar Energy](https://www.osha.gov/green-jobs/solar)
