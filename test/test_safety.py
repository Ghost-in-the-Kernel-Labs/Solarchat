"""The safety rules load from the safety module's data, in sequence and complete, and docs/SAFETY-RULES.md is current (TODO 1.3, HAD-04)."""
import json
import unittest

from scripts import safety_rules_doc
from solarchat.leaf.contract import SafetyRule, SafetyRuleSource
from solarchat.safety import rules
from test.support import ROOT, scratch

GO_TO_SUPERVISOR = "Go to your site supervisor or engineer."


# What the demo pack's own text fires today, and why each hit stands (the commit's report lists each one):
# step-12, fail-04, fail-07 and fail-10 tell the worker to part connectors (release tool, panel covered): SR-03.
# fail-04 and fail-08 name smoke or a burning smell in their own stop lists: SR-08 (a trigger cannot tell "if there is
# smoke" from "there is smoke"; matching on the worker's words is the next step). fail-08, fail-09, fail-13 are damage, always stop: SR-07.
DEMO_PACK_FIRINGS = {
    "step-12": ["SR-03"],
    "fail-04": ["SR-03", "SR-08"],
    "fail-07": ["SR-03"],
    "fail-08": ["SR-07", "SR-08"],
    "fail-09": ["SR-07"],
    "fail-10": ["SR-03"],
    "fail-13": ["SR-07"],
}
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
                self.assertTrue(rule.words_shown.startswith("Stop") or rule.rule_id == "SR-01")
                self.assertTrue(rule.words_shown.endswith(GO_TO_SUPERVISOR))
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
        fired = {}
        for file_name in ("steps.json", "failures.json"):
            for item in json.loads((ROOT / "packs" / "seed-mc4-leads" / file_name).read_text()):
                item_rules = sorted({rule_id for text in pack_strings(item) for rule_id in rules.rules_fired(text)})
                if item_rules:
                    fired[item["id"]] = item_rules
        self.assertEqual(fired, DEMO_PACK_FIRINGS)


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
        with self.assertRaisesRegex(ValueError, "lowercase"):
            SafetyRule("SR-01", "t", "a", ("Roof",), "Stop. " + GO_TO_SUPERVISOR, source)
        with self.assertRaisesRegex(ValueError, "SR- and two digits"):
            SafetyRule("live-dc", "t", "a", ("roof",), "Stop. " + GO_TO_SUPERVISOR, source)


class TheDocument(unittest.TestCase):
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
