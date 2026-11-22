# Handoff: what to work on next, and what is waiting on whom

Read `CLAUDE.md` first, then this. `TODO.md` is the chain in order; `docs/DONE.md` is what is finished.

## Where the project stands (2026-11-21, `main` at 48a248a)

`main` holds the stamp, decisions to SC-023, the project's ghost, the roadmap (Phases 1 to 6), the 22-pin lockfile
(the SDK and its 15 reviewed additions came in with SC-021, J-045), the package `solarchat/` with its contract
(HAD-01 to HAD-06) and module map, the demo pack `packs/seed-mc4-leads/`, the fourteen safety rules as data, and the
frozen evaluation set. Built since the pack and the rules: the answering door and the runner (1.6, J-047), the Claude
answerer, the chat command and the live evaluation run, with the model a parameter (1.16, J-048, J-049), the rule
bank's format and check with twenty hand-written rules (1.19, J-053), and the command menu `bin/solarchat` with the
local key (2.5, J-055; `solarchat --key`, SC-022 point 6). 1.17 was absorbed by SC-023 and not built (J-051). Phase 0
is closed but for 0.5, which waits on Ghost in Phase W. Built since: 2.7, speech out
(`--voice`, J-056); speech in is later and needs a dependency proposed to Ghost.

What works today, and what does not: the chat and the live run call a model only by hand, with a key
(`.venv/bin/python`); the offline stub scores 34 of 90 on `evals/v1.json`; the first live run, by Ghost on Haiku 5.5
(2026-11-21), scored 66 of 90 at an estimated $0.0151, its stop, warn and emergency cases at 0 as expected before 1.9
(J-051). No reply of the door is yet a stop or a warn: the safety rules are not applied to answers until 1.9 and 1.10,
and there is no keyword search (1.7, 1.8), no walker (2.2) and no offline shell (2.4).

What Solarchat is, in the roadmap's words (`docs/ROADMAP.md` §1 to §3, F-01 to F-15): an assistant named Hadley
that walks workers on solar sites through installing panels and finding faults, on a phone, answering only from
knowledge packs; online it calls Claude Sonnet through the Anthropic API with no tools and no connectors, and reads
photos; offline it runs on the packs, the flows and the safety rules, with at most a small model that only chooses
which passage to show.

## Next, in order

1. **TODO 1.3 is landed, with Ghost's read still open**: landed 2026-11-21 on Ghost's word with the draft's answers;
   Ghost has not yet read `docs/SAFETY-RULES.md`; SR-03 was settled by Ghost's word (J-030) and four points stay open. J-027 (renumbered from J-026 at the landing),
   reviewed by the coordinator. Fourteen rules, SR-01 to SR-14, in `solarchat/safety/rules.json`, read by
   `solarchat/safety/rules.py` as the leaf's `SafetyRule`; `docs/SAFETY-RULES.md` generated from them
   (`scripts/safety_rules_doc.py`); the pack check refuses a pack that names a rule or tells the reader to skip one.
   1.3 is in `docs/DONE.md`, marked as all but Ghost's read. Next: the four marks still open in `docs/SAFETY-RULES.md`
   (below, For Ghost 1), headed "Ghost to confirm" there, wait for the engineer's final review under F-16 (the engineer comes in at the end); a change
   of an answer is a change to `rules.json`, then `scripts/safety_rules_doc.py`.
2. **The demo of Monday 2026-11-23** (SC-010, its plan amended by SC-018 and by J-054, Ghost 2026-11-21): the demo is
   run from a local clone on Windows (README, "Running the demo on Windows"): `solarchat --help`, `solarchat --key`, the
   chat on the seed pack with `--demo`, and `scripts/eval.py` scoring the answerer on the evaluation set. Done of the
   chain: 1.3 the safety rules, 1.4 the seed pack, 1.5 the frozen set, 1.6 the door and the runner, 1.16 the model
   answerer, 1.19 the bank's format, 2.5 the command menu and local key. Open, in order: 1.7 the index, 1.8 keyword
   search, 1.9 the safety rules in the answers, 1.10 the safety rules on the worker's words, 1.20 to 1.24 the bank run,
   the model roles, drafting, harm triage and guards (SC-023), then 1.25 Tune-up pass 1 (renumbered from 1.15, 1.18).
   Each goes to a fresh worker of its grade with the brief of `docs/when/hand-out-a-task.md`, saved on its own branch
   and landed by the coordinator after Ghost's word; 1.3 and 1.6 went to the strong grade.
3. **Phase 2** (SC-018: old 1.5 to 1.8 moved down): 2.1 demo mode, 2.2 the walker (`solarchat/walker`, a module Ghost
   approved, its folder not yet written), 2.3 the safety rules in the walker (whole-word matching on the step's text is
   settled, HAD-04), 2.4 the offline shell, and 2.8 (2.7 speech out is built, J-056)
   Tune-up pass 2. 2.5 and 2.7 are the free numbers J-054 used; `docs/ROADMAP.md` still holds its own 2.5 (switching
   packs on and off) and 2.7 (a site-safety pack) under those numbers (For Ghost 20). 1.25 Tune-up pass 1 carries the
   next human maintainability pass (SC-011: Ghost-Core's toolkit under `scripts/` a few files at a time, each with
   its proof that nothing changed; then the tests).

## Settled by Ghost

- 2026-11-20: prefix SC, the python stack, floor grade mid; SC-002 to SC-005 (J-002); the online model, photos,
  speech (J-006, F-07 to F-09); offline the small model only chooses, online first, an app and a website (J-008);
  the manner and the name Hadley (J-009, J-010); no connectors, pictures per step (J-011); demo packs may carry web
  pictures with provenance (J-012, SC-007); the model-name check removed (J-007, SC-006).
- 2026-11-21: the users are workers on sites, not homeowners (J-013); no mutation run (J-015, SC-008); the package
  `solarchat`, the five modules, the prefix HAD and the contract keeping its name (J-018); the repository's default
  branch set to `main` and the old branches deleted (J-019); run Tune-up pass 0 (J-019);
  a tune-up commit every twenty-five commits, not eight (SC-009, J-020); the pack format's procedures, linear
  flows and installation_type (J-022); Monday's demo as an offline walk-through with a labelled demo mode, and the
  walker module (SC-010, J-024); the human maintainability standard (SC-011, J-024).
- 2026-11-21: only checked documentation goes into a field pack, and handing it over is the approval; no approval
  record, a pack is `field` or `demo` (SC-013, J-028; renamed from `library` by SC-017).
- 2026-11-21: the next goal is a chatbot that can be interrogated automatically with a question set: Phase 1 now runs
  the seed pack, the evaluation set, the answering door and its runner, the index, keyword search and the safety rules in
  the answers; the walker, demo mode and offline shell open Phase 2; Monday's demo shows the runner scoring the offline
  bot (SC-018, J-037; it amends SC-010's plan).
- 2026-11-21: tuning the conversational bot by a sampled rule bank read as a trend, harm triage content first, the
  ledger in git; 1.17 absorbed; the live ratchet dropped (SC-023, J-051).
- 2026-11-21: the demo runs from a local clone on Windows; a developer's own machine may hold a key outside the clone
  (SC-022 point 6); a command menu and `solarchat --key`; speech out first, speech in later (J-054; TODO 2.5, 2.7).
- 2026-11-22: the module map confirmed: `project` may import `answer` and `model` (`docs/modules.json`; asked in chat
  at TODO 1.16, J-048; confirmed, J-065).
- The wording of SC-002 to SC-008 is the agent's, for Ghost to confirm.

## For Ghost: waiting on you

1. **The safety rules** (TODO 1.3, landed 2026-11-21 on Ghost's word with the draft's answers; Ghost has not yet read
   `docs/SAFETY-RULES.md`): SR-03 is resolved (Ghost, 2026-11-21: connecting is daily work, not a stop; the rule is now
   "never pull connectors apart under load", J-030). Four points stay open, the marks headed "Ghost to confirm" in
   `docs/SAFETY-RULES.md` (generated from `rules.json`'s `ghost_to_confirm`; under F-16 they wait for the
   engineer's final review, and 1.11 renames the field): SR-02, is measuring a voltage a stop for the newest contractor (the draft: yes); SR-06, the
   overhead-lines rule (beyond the brief; it now gives the 10 ft distance and carries the audit's finding, perimeter
   lines, service drops and OSHA's Fort Riley 2018 citation); SR-08 and SR-09, the emergency and first-aid sentences
   the cited sources do not state; SR-12, the never-bypass rule (beyond the brief). Triggers now match whole words and
   phrases only (HAD-04, `rules_fired`); step 2 of the fix (response types, matching on the worker's words) is a later
   design decision. Also: four sources were cited from search results without the page being read (J-027), and the two
   new OSHA regulation addresses (1910.333, 1926.1408) were not opened (osha.gov refuses this environment).
2. **Page citations** (SC-012, landed on `main` in 3e40d86; the branch `agent/page-citations` is merged and safe to
   delete): the seed pack's citations of its document sources carry a page, and 89 of them were `"unknown"`: S3 Trina installation manual 35, S7 PVEL/HelioVolta safety guide 22, S5 Victron
   troubleshooting chapter 19, S4 Victron installation chapter 10, S6 BRE fire report 3 (S8's 15 citations use page 15,
   from its title). The pack is now in the pack format (1.4, J-038), where a citation is written on every passage, flow
   and procedure that holds it, so the same 89 places in the manuals are counted as 187 citations: S3 71, S7 47, S5 38,
   S4 21, S6 10. A person finds each page in the manual; the check counts the unknown pages and prints the total
   (`python3 -I scripts/checks/packs.py <pack>`), and `test/test_packs.py` runs it over the seed pack (1.4, J-038).
3. Read the demo pack with an engineer's eye before anyone relies on it. The worker flagged claims it could not
   source: fail-04 (reversed leads can damage some devices), step-07's stop (battery not yet wired), step-09 (the
   gentle pull), fail-03 (some shortfall from the label is normal), fail-08's fire wording. Sources S3 and S8 were
   read from third-party mirrors and want official copies.
4. The demo pack fits a small kit (a charge controller, a power station, covering the panel) better than a large
   site. A second demo pack, stringing modules on a utility site, would be nearer the users of F-01.
5. `CLAUDE.md`'s three rules still state Core C-033 without SC-007's narrowing, which is why the worker kept to
   openly licensed pictures. Say whether `CLAUDE.md` should name SC-007.
6. Whether the deploying company may be named in the repository (the agent has not written its name).
7. The app's stack (roadmap 5.1): one web client that is both the website and an installable app, or a native app.
8. Which make and model the first real pack covers (roadmap 6.2); Ghost named First Solar as the most troublesome.
9. A trademark search on the name Hadley before it reaches an app store.
10. Ghost-Core's `docs/GHOST-IN-THE-KERNEL.md` opening is a condensed rewrite of the manifesto (J-023); the fix is
   Core's, in a session with push access to it.
11. A stop hook asks for a push whenever a branch is ahead of origin (2026-11-21: it fired on a branch restarted
   from `main`); a hook is outside what an agent may change (`docs/when/coordinate.md`), so it is reported here.
12. `scripts/ship.sh` is stamped without its executable bit (run it as `bash scripts/ship.sh`); a mode change to a
   gate file is yours.
13. **The coordinator's conditional** (2026-11-21, Ghost's ask): `CLAUDE.md` sends the coordinator to
   `docs/when/coordinate.md`, "Who does each item", the assignment rule of C-026, C-027 and C-036 in
   seven steps. The wording is the agent's, and two steps go past the ghost's text for your confirmation: a raise above
   the score writes its reason in the journal, and a strong Cost line on an item scored lower says why. Ghost-Core's
   template could carry the same section (a Core change, in a session with push access to it). Landed on `main` in
   da53935 (renumbered from a second 12, J-031); confirm the two steps.
14. SC-013 (landed on your word, 2026-11-21): handing documentation to the person who loads the packs is the approval; a pack's `status` is `field` or `demo` (renamed from `library`, SC-017), no approval record exists, and a `field` pack with an unknown page is refused. Confirm the wording; the seed pack is `demo` with its 187 unknown-page citations (89 places in the manuals, J-038).
15. **The reference library** (SC-014, J-029, landed on your ask; extended 2026-11-21): `library/sources/` holds source documents, not packs, each with its licence quoted and a hash. OSHA regulations from eCFR (17 U.S.C. 105 and the GPO notice): 29 CFR 1910 Subparts S, D (walking-working surfaces) and I (PPE), 1910.269, 1910.147, 1910.179 and 1910.180 (one folder), 1926 Subparts K and M, 1926.1407 to 1926.1411 and 1926.1417. NIOSH 2009-113 (92 pages; its own "public domain" line) and Solar Victoria's PV audit checklist (CC BY 4.0). **Eight OSHA web pages you pasted by hand** (the seven solar pages and Lithium-ion Hazards; osha.gov refuses automated clients): no original is kept, `text.txt` is your paste without its two header lines, `sha256` is of that text, and each `note` says so; the licence evidence is 17 U.S.C. 105. **Originals dropped, text and sha256 kept:** the NIOSH PDF (its credits mark five photo sources with (c)) and the Solar Victoria HTML (flag images; the site's licence excludes images). The eCFR licence statement is the GPO's (ecfr.gov's own pages sit behind a bot check). **California FACE solar fatality reports: not added, not checked.** The FACE page (cdph.ca.gov/Programs/CCDPHP/DEODC/OHB/FACE/Pages/Solar.aspx) could not be fetched from this environment (a TLS certificate error through the proxy, and a 503 from the fetch tool), so neither its report list nor its terms of use or copyright statement was read. California state works are not automatically public domain: please open the page, and add a report only if the site allows copying or the report states it was funded by a NIOSH cooperative agreement. The safety rules' sources now carry library ids in their titles (SR-03, SR-05, SR-06, SR-11, and the 1910.333 and 1926.1408 links).
16. **The plan aligned with your vision of 2026-11-21: answered** (J-031 proposed it, J-032 records your answers; "go
   with your recommendations on all seven", 2026-11-21). In force: **SC-015** warn and help by default (SR-03 at `warn`
   on your word, SR-08 and SR-09 at `emergency`, the rest at `stop`; you may confirm precision fixes, matching bugs and
   not safety judgements, before an engineer is named, logged as "maintainer"); **SC-016** each safety rule's change log;
   facts **F-16** (an electrical engineer QAs the bot) and **F-17** (your field-manual vision); **SC-017** the pack status
   `library` renamed `field`, so "library" means only `library/sources/`. The leaf change (`ReplyKind.WARN`,
   `SafetyRule.response`) is approved. Built: the code for
   SC-015 and SC-016 (J-034: `ReplyKind.WARN`, each rule's `response` and change log, the fingerprint check), then the
   `field` rename. **Ghost's further word, the same day (J-033): the engineer comes in at the
   end; nothing waits on them before then.** The electrical engineer is unknown and reviews the bot once, at the end of
   the project (F-16, P-20, TODO 6.4); what is decided now on Ghost's word is logged under SC-016 with the role
   "maintainer", pending engineer, and the engineer confirms or reverses each at that review. The evaluation
   set (then 1.9, now 1.5, SC-018) is back in Phase 1; the review packet (TODO 1.14) will gather what the engineer must judge. No open item remains for you here.
17. **The answering door and the runner, designed: SC-019, in force, answered by you on 2026-11-21 in chat** (J-040, J-042;
   the design is `docs/designs/answering-door.md`, its section 10 the questions). "Go with your recommendations, sign-off
   question for meters." All ten went as recommended: (1) the new module `answer`, and the model client in its own module
   `model` in Phase 3; (2) the leaf change; (3) the fast loop holds the record as a per-case ratchet; (4) mns-03 is the
   worker-words item's, not 1.13's; (5) 2.6, the safety rules matched on the worker's words, moved up to 1.10, right after
   1.9 (old 1.10 Tune-up pass 1 is now 1.15); (6) no accuracy threshold before a baseline, yours to set after 1.8 and at 3.4;
   (7) the search threshold tuned on the frozen set, for version 1, a held-out set a later item; (8) the most severe
   response, then the lowest id; (9) the known failures mns-03, mns-06 and mns-09 in `evals/known-failures.json`;
   (10) `docs/designs/` as the home of designs. The meters, your addition, widened the same day to a session profile: SC-020, three or four short questions at the start of a session (role; signed off for meter tests, connector work, work at height), a rule alone may lower its response for a profile and never an emergency, the profile may change how much is explained and never which steps or stops, self-declared with the company's override, recorded per session for the engineer; its design is 1.10's first step and still open (how the profile is held, how rules name their lowerings, the side file's shape, whether the meter triggers split from SR-02). Answered; nothing waits on you here.
18. **Tuning the conversational bot: SC-023, in force, answered by you on 2026-11-21 in chat** (J-050 proposed it,
   J-051 records your answer; the design is `docs/designs/rule-bank-and-triage.md`). "I'll go with the other agent's
   recommendations": all nine went as section 10 recommends, 1.17 is closed as absorbed, and SC-019's live ratchet is
   dropped. On the coordinator's question, the ledger (60 runs), the triage records and the trend page enter git, and
   transcripts stay under `build/`. TODO 1.19 to 1.24 are in Phase 1, before its tune-up pass, now 1.25. Answered;
   nothing waits on you here.

19. **Tune-up commit 1's four questions: answered** (J-052 asked; J-058 records Ghost's answer of 2026-11-21, "go with
    your recommendations on all four"): (a) `scripts/next_id.py` reading agent branches is **not built**: the journal
    check refuses a gap, so a worker given an id past main's would fail its own fast loop; the coordinator renumbers at
    landing instead, and Ghost chooses between that and a renumbering script (For Ghost 21). (b) The worker `.venv`
    script is being built; the safety-rule change-entry script waits until a rule next changes. (c) Declined: no
    `Waits on: none outside` kind. (d) Recorded in `theGhost.md`'s header: a wording fix or added point in place on
    Ghost's word, a change of substance a new superseding decision.
20. **Two items held the same numbers: settled by the coordinator** (J-057 found it, J-058): the roadmap's 2.5 and 2.7
    are now 2.9 and 2.10, and the roadmap lists the demo's 2.5 and 2.7, which took those numbers by the coordinator's
    mistake (only `TODO.md` and `docs/DONE.md` were searched). No plan text changed; say if you want other numbers.
21. **Journal ids across branches, and ruff: answered** (J-062, Ghost, 2026-11-22: "go with your recommendations"): the
    coordinator renumbers a branch's journal entry by hand at landing, and no renumbering script is written; `ruff
    check .` now runs in the fast checks (`stacks/python/gate.sh --fast`), so lint is caught at each landing.
22. **SR-08's sentence ("do not touch the connector; cover the panel or turn off the switch"): S6 and S7 do not state it** (J-066):
    S6 (BRE) and S7 (PVEL/HelioVolta) have no page saying do not touch or pull apart a hot, burnt or arcing connector, and none
    saying cover the panel or open a switch for one. S6's pages 12 and 17 say the opposite of a solution: DC cables upstream of an
    isolator cannot easily be isolated, and a safe emergency method of isolating there is still to be researched (that is the
    caveat of (c), S6 page 12). S7 page 4 and the footnote of page 6 say connectors are only safely unplugged or opened when not
    under load. S3 (Trina manual) supports half, for work on modules and not for a fire: page 3 (do not disconnect under load;
    cover with an opaque cover if needed), page 14 (use a DC switch before disconnecting), page 15 (do not touch live parts of
    cables and connectors; cover the front when repairing). Page numbers are printed and PDF alike. Ghost's choices: keep SR-08
    without the sentence (current state), or word one from S3 only and limit it to what S3 says, or accept it as unsourced
    guidance flagged "engineer to confirm". The quotes are in the worker's report. S6 was not added to the library: its page 3
    allows distribution only entire and unamended, with no Open Government Licence statement in the PDF; S7 is copyrighted.
23. **SC-024, proposed: a pack is the first safety authority for its make and model; the general rules are the default
    where it is silent** (J-067; your direction of 2026-11-22). It reverses HAD-04 and part of SC-020, so nothing is built
    until you confirm or strike each part of its entry: (1) a pack declares, per general rule, which of its own passages
    cover that hazard; an undeclared rule stays in force (silence is never guessed from the text); (2) each covering
    passage cites the manual's page, never "unknown"; (3) an emergency floor: SR-08 and SR-09 still give the emergency
    response, with the pack's words beside them; (4) the reply cites the pack's passage; (5) only a `field` pack, or a
    `demo` pack on your word; (6) the engineer's packet lists every covered rule. Recommended: all six.

Audit advisories (tune-up step 2): the python gate runs no audit step, so none are listed. An audit tool
(`pip-audit` or the like) would be a new dependency, Ghost's to approve; until then the review's layers 1, 2 and 4
stand alone (`docs/DEPENDENCY-REVIEW.md`).

## Trials: questions settled by a run, not an argument

(none yet; roadmap 3.7 and 5.1 name the first two. The first live run, 66 of 90 on Haiku 5.5, is one nondeterministic run, an observation and no trial.)

## What to distrust

- The demo pack is `demo`, not `field` (SC-013, SC-017) and was written to a provisional layout before 1.2 and 1.3 existed, then converted to the pack format by 1.4 (J-038). Its
  drawings were looked at once, rendered together; its text was not read in full by the coordinator.
- The project's ghost and the roadmap are the agent's drafts from Ghost's words, landed for Ghost to correct.
- A session's venv: `python3.12 -m venv .venv && .venv/bin/pip install --only-binary :all: --require-hashes -r requirements.lock`.
- Branches left on origin, safe to delete (this session's proxy refuses a branch deletion, HTTP 403; each was landed
  by squash or by a rewritten commit, so git's own "merged" test says no, and the content is on `main`):
  `agent/words-1-1` (1.1), `agent/pack-format-1-2` (1.2), `agent/safety-rules-1-3` (1.3), `agent/page-citations`
  (SC-012), `agent/coordinator-conditional` (da53935), `agent/roadmap-vision` (marked "not for main"; its SC-015,
  SC-016, F-16 and F-17 landed with J-032), `agent/tune-up-commit-1` (J-052), `agent/rule-bank-1-19` (J-053),
  `agent/cli-key-2-5` (J-054, J-055), `worktree-agent-a80dd423575285e3d` (SDK, J-045) and `claude/quirky-pascal-nr458d`
  (level with `main`). The 2.7 branch is not on origin yet. The remote's name is
  `Ghost-in-the-Kernel-Labs/Solarchat`; a fresh clone may still name it in lower case, which works through GitHub's
  redirect.
- Branches deleted earlier, kept here for the record: `claude/audience-f01`, `claude/gate-0-2`, `agent/seed-pack`.
