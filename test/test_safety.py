"""The safety rules load from the safety module's data, in sequence and complete, and docs/SAFETY-RULES.md is current (TODO 1.3, HAD-04)."""
import hashlib
import json
import re
import unittest

from scripts import safety_rules_doc
from solarchat.answer.door import answer
from solarchat.leaf.contract import Finding, PassageRef, ReplyKind, SafetyRule, SafetyRuleChange, SafetyRuleSource
from solarchat.safety import rules
from solarchat.packs.load import load_pack
from test.support import ROOT, scratch
from test.test_door import Spy

SEED = load_pack(ROOT / "packs" / "seed-mc4-leads")

GO_TO_SUPERVISOR = "Go to your site supervisor or engineer."
EMERGENCY_RULES = ("SR-08", "SR-09")
CHANGE = ("2026-11-21", "Ghost", "maintainer", "First draft.", "J-027")


# What the demo pack's own text fires today, and why each hit stands (the commit's report lists each one):
# step-12, fail-04, fail-07 and fail-10 tell the worker to part connectors (release tool, panel covered): SR-03.
# fail-04 and fail-08 name smoke or a burning smell in their own stop lists: SR-08 (a trigger cannot tell "if there is
# smoke" from "there is smoke"; matching on the worker's words is the next step). fail-08, fail-09, fail-13 are damage, always stop: SR-07.
# TODO 1.10 (J-079): `rules_fired` is text-level. SR-07, SR-08 and SR-09 read the worker's words only (`reads == "words"`),
# so the door acts on none of the SR-07 and SR-08 hits here; the new ones are Ghost's triggers "broken", "is cracked" (SR-07:
# step-02's "If the glass is broken", fail-13) and "smells burnt" (SR-08: fail-01, fail-08), which still match the pack's text.
DEMO_PACK_FIRINGS = {
    "step-02": ["SR-07"],
    "step-12": ["SR-03"],
    "fail-01": ["SR-08"],
    "fail-04": ["SR-03", "SR-08"],
    "fail-07": ["SR-03"],
    "fail-08": ["SR-07", "SR-08"],
    "fail-09": ["SR-07"],
    "fail-10": ["SR-03"],
    "fail-13": ["SR-07"],
}
# The same firings by piece of the pack in the pack format (TODO 1.4): a passage, a flow, a procedure's header or one of its
# steps, named `entry@procedure`; each old step or failure is now several, so DEMO_PACK_FIRINGS above is read by origin.
DEMO_PACK_ENTRY_FIRINGS = {
    "step-02": ["SR-07"],
    "step-02@connect-panel": ["SR-07"],
    "step-12": ["SR-03"],
    "step-12@connect-panel": ["SR-03"],
    "fail-01": ["SR-08"],
    "fail-01-stop": ["SR-08"],
    "fail-04": ["SR-03", "SR-08"],
    "fail-04-check-2": ["SR-08"],
    "fail-04-fix": ["SR-03"],
    "fail-04-stop": ["SR-08"],
    "fail-07": ["SR-03"],
    "fail-07-fix": ["SR-03"],
    "fail-08": ["SR-07", "SR-08"],
    "fail-08-causes": ["SR-08"],
    "fail-08-check-1": ["SR-08"],
    "fail-08-check-2": ["SR-08"],
    "fail-08-fix": ["SR-07", "SR-08"],
    "fail-08-stop": ["SR-08"],
    "fail-09": ["SR-07"],
    "fail-09-causes": ["SR-07"],
    "fail-09-check-1": ["SR-07"],
    "fail-09-fix": ["SR-07"],
    "fail-09-stop": ["SR-07"],
    "fail-10": ["SR-03"],
    "fail-10-fix": ["SR-03"],
    "fail-13": ["SR-07"],
    "fail-13-causes": ["SR-07"],
    "fail-13-check-1": ["SR-07"],
    "fail-13-fix": ["SR-07"],
    "fail-13-stop": ["SR-07"],
}
SEED_PACK = ROOT / "packs" / "seed-mc4-leads"
ORIGIN_ID = re.compile(r"^(step-\d+|fail-\d+)")
NOT_TEXT_FIELDS = ("id", "image", "photo", "sources", "source", "page")


def pack_strings(value: object) -> list[str]:
    """Every text in a pack item, its lists and nested items included, without ids, image paths or sources:
    {"id": "a", "text": "x", "checks": [{"text": "y"}]} gives ["x", "y"]."""
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [text for entry in value for text in pack_strings(entry)]
    if isinstance(value, dict):
        return [text for key, entry in value.items() if key not in NOT_TEXT_FIELDS for text in pack_strings(entry)]
    return []


def seed_pack_entries() -> list[tuple[str, dict]]:
    """Each piece of the seed pack's text with its name: its passages and flows by id, each procedure's header (without its
    steps) by id, and each step as "step-12@connect-panel"."""
    entries: list[tuple[str, dict]] = []
    for file_name in ("passages.json", "flows.json"):
        entries += [(item["id"], item) for item in json.loads((SEED_PACK / file_name).read_text())]
    for procedure in json.loads((SEED_PACK / "procedures.json").read_text()):
        entries.append((procedure["id"], {key: value for key, value in procedure.items() if key != "steps"}))
        entries += [(f"{step['id']}@{procedure['id']}", step) for step in procedure["steps"]]
    return entries


def rules_fired_by_entry() -> dict[str, list[str]]:
    """The rules each piece of the seed pack fires, only the pieces that fire one: {"fail-04-fix": ["SR-03"], ...}."""
    fired = {}
    for entry_name, entry in seed_pack_entries():
        entry_rules = sorted({rule_id for text in pack_strings(entry) for rule_id in rules.rules_fired(text)})
        if entry_rules:
            fired[entry_name] = entry_rules
    return fired


def write_rules(rule_entries: list[dict]) -> object:
    """A scratch rules file holding rule_entries, e.g. /tmp/ghost-core-abc/rules.json, for the loader to read."""
    rules_path = scratch() / "rules.json"
    rules_path.write_text(json.dumps(rule_entries))
    return rules_path


class TheRules(unittest.TestCase):
    def test_the_rules_load(self) -> None:
        self.assertGreaterEqual(len(rules.load_rules()), 8)

    def test_ids_are_in_sequence_and_unique(self) -> None:
        rule_ids = [rule.rule_id for rule in rules.load_rules()]
        self.assertEqual(rule_ids, [f"SR-{rule_number:02d}" for rule_number in range(1, len(rule_ids) + 1)])

    def test_every_rule_has_words_triggers_and_a_source(self) -> None:
        for rule in rules.load_rules():
            with self.subTest(rule=rule.rule_id):
                # SR-03 is a warn: its words let the walk continue, so they neither say Stop nor send the worker away (J-036)
                self.assertTrue(rule.words_shown.startswith("Stop") or rule.rule_id in ("SR-01", "SR-03"))
                self.assertTrue(rule.words_shown.endswith(GO_TO_SUPERVISOR) or rule.rule_id == "SR-03")
                self.assertTrue(rule.triggers)
                self.assertTrue(rule.sources)

    def test_sr_01_is_the_procedures_first_rule(self) -> None:
        first_rule = rules.load_rules()[0]
        self.assertEqual(first_rule.rule_id, "SR-01")
        self.assertIn("site's own safety procedures", first_rule.title)
        self.assertIn("come first", first_rule.words_shown)

    def test_a_trigger_is_never_shared_by_two_rules(self) -> None:
        all_triggers = [trigger for rule in rules.load_rules() for trigger in rule.triggers]
        self.assertEqual(sorted(set(trigger for trigger in all_triggers if all_triggers.count(trigger) > 1)), [])


class TheResponses(unittest.TestCase):
    """Each rule's response is SC-015's starting value, SR-03 at a warn on Ghost's word."""

    def test_sr_03_is_a_warn_and_sr_08_and_sr_09_are_emergencies_and_the_rest_stop(self) -> None:
        responses = {rule.rule_id: rule.response for rule in rules.load_rules()}
        self.assertEqual(responses["SR-03"], "warn")
        for rule_id, response in responses.items():
            with self.subTest(rule=rule_id):
                expected = "warn" if rule_id == "SR-03" else "emergency" if rule_id in EMERGENCY_RULES else "stop"
                self.assertEqual(response, expected)

    def test_sr_03_logs_ghosts_warn_as_maintainer_and_pending_review(self) -> None:
        warn_entry, words_entry = rules.load_rules()[2].changes[-2:]
        self.assertEqual((warn_entry.by, warn_entry.role), ("Ghost", "maintainer"))
        self.assertEqual(warn_entry.why, "connecting is daily work; parting under load is the hazard; pending engineer review")
        self.assertEqual((words_entry.by, words_entry.role, words_entry.evidence), ("Ghost", "maintainer", "J-036"))
        self.assertIn("pending engineer review", words_entry.why)

    def test_every_rule_logs_version_1_and_the_audits_change_first(self) -> None:
        for rule in rules.load_rules():
            with self.subTest(rule=rule.rule_id):
                self.assertEqual(rule.changes[0].evidence, "J-027; the sources listed on this rule")
                self.assertEqual(rule.changes[1].evidence, "docs/audits/2026-11-21-safety-rules.md; J-030")
                self.assertTrue(all(change.role != "electrical engineer" for change in rule.changes))


class TheChangeLog(unittest.TestCase):
    def test_every_rules_latest_fingerprint_is_the_sha256_of_its_triggers_words_and_response(self) -> None:
        for rule in rules.load_rules():
            with self.subTest(rule=rule.rule_id):
                fields = {"triggers": list(rule.triggers), "words_shown": rule.words_shown, "response": rule.response}
                if rule.lowered_for:  # SC-020: a rule with lowerings has them in its fingerprint; the others keep theirs
                    fields["lowered_for"] = [{"signed_off": low.signed_off, "role": low.role, "response": low.response,
                                              "words": low.words} for low in rule.lowered_for]
                if rule.reads != "both":  # TODO 1.10: a rule that reads the words only has it in its fingerprint
                    fields["reads"] = rule.reads
                canonical = json.dumps(fields, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
                self.assertEqual(rule.changes[-1].fingerprint, hashlib.sha256(canonical.encode("utf-8")).hexdigest())
                self.assertEqual(rules.rule_fingerprint(rule), rule.changes[-1].fingerprint)

    def test_only_the_triggers_the_words_and_the_response_move_the_fingerprint(self) -> None:
        rule = rules.load_rules()[0]
        retitled = SafetyRule(rule.rule_id, "Another title", rule.applies_when, rule.triggers, rule.words_shown,
                              rule.sources, rule.response, rule.changes)
        self.assertEqual(rules.rule_fingerprint(retitled), rules.rule_fingerprint(rule))
        louder = SafetyRule(rule.rule_id, rule.title, rule.applies_when, rule.triggers, rule.words_shown,
                            rule.sources, "emergency", rule.changes)
        self.assertNotEqual(rules.rule_fingerprint(louder), rules.rule_fingerprint(rule))

    def test_a_change_to_a_trigger_with_no_new_entry_is_refused(self) -> None:
        rule_entries = self.entries()
        rule_entries[4]["triggers"] = rule_entries[4]["triggers"] + ["a new trigger"]
        with self.assertRaisesRegex(ValueError, "SR-05: the rule changed since its last change entry"):
            rules.load_rules(write_rules(rule_entries))

    def test_a_change_to_the_words_or_the_response_with_no_new_entry_is_refused(self) -> None:
        for field, value in (("words_shown", "Stop. Different words. " + GO_TO_SUPERVISOR), ("response", "emergency")):
            rule_entries = self.entries()
            rule_entries[3][field] = value
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "SR-04: the rule changed since"):
                rules.load_rules(write_rules(rule_entries))

    def test_a_latest_entry_with_no_fingerprint_is_refused(self) -> None:
        rule_entries = self.entries()
        del rule_entries[0]["changes"][-1]["fingerprint"]
        with self.assertRaisesRegex(ValueError, "SR-01: the rule changed since its last change entry"):
            rules.load_rules(write_rules(rule_entries))

    def test_a_rule_with_no_changes_is_refused(self) -> None:
        rule_entries = self.entries()
        rule_entries[1]["changes"] = []
        with self.assertRaisesRegex(ValueError, "SR-02: a rule has at least one change"):
            rules.load_rules(write_rules(rule_entries))
        del rule_entries[1]["changes"]
        with self.assertRaisesRegex(ValueError, "SR-02: a rule has at least one change"):
            rules.load_rules(write_rules(rule_entries))

    def test_an_entry_missing_a_field_is_refused(self) -> None:
        for field in ("date", "by", "role", "why", "evidence"):
            rule_entries = self.entries()
            del rule_entries[2]["changes"][0][field]
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, f"SR-03: change 1 is missing '{field}'"):
                rules.load_rules(write_rules(rule_entries))

    def test_an_entry_with_an_empty_field_or_a_bad_date_is_refused(self) -> None:
        rule_entries = self.entries()
        rule_entries[2]["changes"][0]["why"] = "  "
        with self.assertRaisesRegex(ValueError, "SR-03: change 1 has an empty 'why'"):
            rules.load_rules(write_rules(rule_entries))
        rule_entries = self.entries()
        rule_entries[2]["changes"][0]["date"] = "21 November"
        with self.assertRaisesRegex(ValueError, "SR-03: change 1 has a date that is not ISO"):
            rules.load_rules(write_rules(rule_entries))

    def test_a_bad_or_missing_response_is_refused(self) -> None:
        rule_entries = self.entries()
        rule_entries[5]["response"] = "halt"
        with self.assertRaisesRegex(ValueError, "SR-06: response 'halt' is not one of warn, stop, emergency"):
            rules.load_rules(write_rules(rule_entries))
        del rule_entries[5]["response"]
        with self.assertRaisesRegex(ValueError, "SR-06: response '' is not one of"):
            rules.load_rules(write_rules(rule_entries))

    def test_the_leaf_refuses_a_rule_with_a_bad_response_or_no_changes(self) -> None:
        source = (SafetyRuleSource("HSE", "https://www.hse.gov.uk/"),)
        words = "Stop. " + GO_TO_SUPERVISOR
        with self.assertRaisesRegex(ValueError, "SC-015"):
            SafetyRule("SR-01", "t", "a", ("roof",), words, source, "halt", (SafetyRuleChange(*CHANGE),))
        with self.assertRaisesRegex(ValueError, "SC-016"):
            SafetyRule("SR-01", "t", "a", ("roof",), words, source, "stop", ())
        self.assertEqual(SafetyRule("SR-01", "t", "a", ("roof",), words, source, "warn", (SafetyRuleChange(*CHANGE),)).response, "warn")

    def entries(self) -> list[dict]:
        """The real rules.json entries, to be altered into a planted break."""
        return json.loads(rules.RULES_PATH.read_text())


class TheMatching(unittest.TestCase):
    def test_a_trigger_matches_only_a_whole_word(self) -> None:
        self.assertEqual(rules.rules_fired("The undamaged cable can deliver power. It is alive and waterproof."), [])
        self.assertEqual(rules.rules_fired("This is a damaged connector."), ["SR-07"])
        self.assertEqual(rules.rules_fired("Do not climb the ladder."), ["SR-05"])
        self.assertEqual(rules.rules_fired("Do not climb the ladders."), [])

    def test_matching_ignores_case(self) -> None:
        self.assertEqual(rules.rules_fired("CLIMB THE LADDER"), ["SR-05"])
        self.assertEqual(rules.rules_fired("Smoke"), ["SR-08"])

    def test_a_phrase_matches_as_a_whole_and_across_a_line_break(self) -> None:
        self.assertEqual(rules.rules_fired("then open the pairs with the tool"), ["SR-03"])
        self.assertEqual(rules.rules_fired("then open\nthe   pairs"), ["SR-03"])
        self.assertEqual(rules.rules_fired("open the pair"), [])
        self.assertEqual(rules.rules_fired("pull the connectors"), [])

    def test_rules_come_back_in_rule_order_once_each(self) -> None:
        self.assertEqual(rules.rules_fired("smoke, sparks and a pylon; smoke again; broken panel"), ["SR-06", "SR-07", "SR-08"])

    def test_text_that_only_tells_what_to_look_for_fires_nothing(self) -> None:
        self.assertEqual(rules.rules_fired("Look for cracked, melted or scorched connectors and a live view of the panel."), [])
        self.assertEqual(rules.rules_fired("Connect the panel, plug the leads in and join the pairs until each clicks."), [])

    def test_every_trigger_fires_its_own_rule_and_no_other(self) -> None:
        for rule in rules.load_rules():
            for trigger in rule.triggers:
                with self.subTest(trigger=trigger):
                    self.assertEqual(rules.rules_fired(f"x {trigger.upper()}, y"), [rule.rule_id])


class TheDemoPack(unittest.TestCase):
    def test_which_demo_text_fires_which_rule(self) -> None:
        self.assertEqual(rules_fired_by_entry(), DEMO_PACK_ENTRY_FIRINGS)

    def test_the_same_text_fires_the_same_rules_as_before_the_pack_format(self) -> None:
        by_origin: dict[str, set[str]] = {}
        for entry_name, entry_rules in rules_fired_by_entry().items():
            origin = ORIGIN_ID.match(entry_name)
            by_origin.setdefault(origin.group(1) if origin else entry_name, set()).update(entry_rules)
        self.assertEqual({origin: sorted(origin_rules) for origin, origin_rules in by_origin.items()}, DEMO_PACK_FIRINGS)


    def test_the_door_does_not_act_on_step_02s_text_level_hit_of_a_words_only_rule(self) -> None:
        step_02 = PassageRef("seed-mc4-leads", "step-02")
        self.assertEqual(rules.rules_fired(next(p.text for p in SEED.passages if p.ref == step_02)), ["SR-07"])
        reply = answer("What should I look at on the panel before I connect anything?", (SEED,), True,
                       Spy(Finding((step_02,), "Look at the glass, the cable covers and the connectors.")))
        self.assertEqual((reply.kind, reply.safety_rule_id), (ReplyKind.ANSWER, None))


class TheLoader(unittest.TestCase):
    def entries(self) -> list[dict]:
        """The real rules.json entries, to be altered into a planted break."""
        return json.loads(rules.RULES_PATH.read_text())

    def test_a_gap_in_the_ids_is_refused(self) -> None:
        rule_entries = self.entries()
        del rule_entries[1]
        with self.assertRaisesRegex(ValueError, "rule 2 is SR-03, not SR-02"):
            rules.load_rules(write_rules(rule_entries))

    def test_a_rule_with_no_source_is_refused(self) -> None:
        rule_entries = self.entries()
        rule_entries[2]["sources"] = []
        with self.assertRaisesRegex(ValueError, "SR-03: a rule has at least one source"):
            rules.load_rules(write_rules(rule_entries))

    def test_a_first_rule_that_is_not_procedures_first_is_refused(self) -> None:
        rule_entries = self.entries()
        rule_entries[0]["title"] = "Something else"
        with self.assertRaisesRegex(ValueError, "SR-01 is the rule"):
            rules.load_rules(write_rules(rule_entries))

    def test_an_empty_file_is_refused(self) -> None:
        with self.assertRaisesRegex(ValueError, "no safety rules"):
            rules.load_rules(write_rules([]))

    def test_the_leaf_refuses_an_uppercase_trigger_and_a_bad_id(self) -> None:
        source = (SafetyRuleSource("HSE", "https://www.hse.gov.uk/"),)
        logged = (SafetyRuleChange(*CHANGE),)
        with self.assertRaisesRegex(ValueError, "lowercase"):
            SafetyRule("SR-01", "t", "a", ("Roof",), "Stop. " + GO_TO_SUPERVISOR, source, "stop", logged)
        with self.assertRaisesRegex(ValueError, "SR- and two digits"):
            SafetyRule("live-dc", "t", "a", ("roof",), "Stop. " + GO_TO_SUPERVISOR, source, "stop", logged)


class TheDocument(unittest.TestCase):
    def test_it_shows_each_rules_response_and_latest_change(self) -> None:
        document_text = (ROOT / "docs" / "SAFETY-RULES.md").read_text()
        for rule in rules.load_rules():
            with self.subTest(rule=rule.rule_id):
                section = document_text.split(f"## {rule.rule_id} ", 1)[1].split("\n## ", 1)[0]
                self.assertIn(f"**Response:** {rule.response}", section)
                self.assertIn(f"**Latest change:** {rule.changes[-1].date}, {rule.changes[-1].by}", section)

    def test_the_document_is_current(self) -> None:
        self.assertEqual(safety_rules_doc.main(["--check"]), 0, "run: python3 -I scripts/safety_rules_doc.py")

    def test_it_opens_with_procedures_first_and_outside_every_pack(self) -> None:
        document_text = (ROOT / "docs" / "SAFETY-RULES.md").read_text()
        opening = document_text.split("## The rules at a glance", 1)[0]
        self.assertIn("The site's own safety procedures come first", opening)
        self.assertIn("outside every pack", opening)

    def test_it_lists_every_rule_with_its_words_and_sources(self) -> None:
        document_text = (ROOT / "docs" / "SAFETY-RULES.md").read_text()
        for rule in rules.load_rules():
            with self.subTest(rule=rule.rule_id):
                self.assertIn(f"## {rule.rule_id} {rule.title}", document_text)
                self.assertIn(f"> {rule.words_shown}", document_text)
                self.assertIn(rule.sources[0].url, document_text)
