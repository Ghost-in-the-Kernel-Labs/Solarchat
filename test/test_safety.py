"""The safety rules load from the safety module's data, in sequence and complete, and docs/SAFETY-RULES.md is current (TODO 1.3, HAD-04)."""
import json
import unittest

from scripts import safety_rules_doc
from solarchat.leaf.contract import SafetyRule, SafetyRuleSource
from solarchat.safety import rules
from test.support import ROOT, scratch

GO_TO_SUPERVISOR = "Go to your site supervisor or engineer."


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
