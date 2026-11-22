"""SC-020: a rule's lowered_for is data in rules.json, is in the fingerprint, and only Ghost's three table rows carry one (TODO 1.10, slice 1)."""
import hashlib
import json
import unittest

from solarchat.safety import rules
from test.test_safety import write_rules


class TheLowerings(unittest.TestCase):
    """SC-020: lowered_for is data in rules.json, in the fingerprint, and only Ghost's three table rows are there."""

    def entries(self) -> list[dict]:
        """The real rules.json entries, to be altered into a planted break."""
        return json.loads(rules.RULES_PATH.read_text())

    def test_exactly_three_rules_lower_each_to_warn_for_its_one_sign_off(self) -> None:
        lowered = {rule.rule_id: [(low.signed_off, low.role, low.response) for low in rule.lowered_for]
                   for rule in rules.load_rules() if rule.lowered_for}
        self.assertEqual(lowered, {"SR-02": [("meter", None, "warn")], "SR-05": [("height", None, "warn")],
                                   "SR-11": [("battery", None, "warn")]})

    def test_each_lowered_rule_logs_the_lowering_as_its_latest_change(self) -> None:
        for rule in rules.load_rules():
            if rule.lowered_for:
                latest = rule.changes[-1]
                with self.subTest(rule=rule.rule_id):
                    self.assertEqual((latest.date, latest.by, latest.role, latest.evidence),
                                     ("2026-11-22", "Ghost", "maintainer", "J-074; docs/designs/session-profile.md"))
                    self.assertTrue(latest.why.startswith(f"{rule.rule_id} lowered to warn for a "))
                    self.assertTrue(latest.why.endswith("sign-off (SC-020); engineer to confirm"))

    def test_the_lowering_of_sr_02_is_sc_020s_own_words(self) -> None:
        sr_02 = {rule.rule_id: rule for rule in rules.load_rules()}["SR-02"]
        self.assertEqual(sr_02.lowered_for[0].words, "You are signed off for meter tests: use a meter and test leads rated for the "
                         "string's DC voltage, measure at the connectors, never across a loaded circuit.")

    def test_a_lowering_added_or_changed_with_no_new_entry_is_refused(self) -> None:
        added = self.entries()
        added[3]["lowered_for"] = [{"signed_off": "meter", "response": "warn", "words": "You are signed off for meter tests."}]
        with self.assertRaisesRegex(ValueError, "SR-04: the rule changed since its last change entry"):
            rules.load_rules(write_rules(added))
        changed = self.entries()
        changed[1]["lowered_for"][0]["words"] = "Other words."
        with self.assertRaisesRegex(ValueError, "SR-02: the rule changed since its last change entry"):
            rules.load_rules(write_rules(changed))
        removed = self.entries()
        del removed[1]["lowered_for"]
        with self.assertRaisesRegex(ValueError, "SR-02: the rule changed since its last change entry"):
            rules.load_rules(write_rules(removed))

    def test_a_rule_with_no_lowerings_keeps_the_fingerprint_it_had_before_sc_020(self) -> None:
        entries = self.entries()
        self.assertNotIn("lowered_for", entries[0])
        rule = rules.rule_from_entry(entries[0])
        canonical = json.dumps({"triggers": list(rule.triggers), "words_shown": rule.words_shown, "response": rule.response},
                               sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        self.assertEqual(rules.rule_fingerprint(rule), hashlib.sha256(canonical.encode("utf-8")).hexdigest())

    def test_an_emergency_with_lowered_for_is_refused_by_the_loader(self) -> None:
        entries = self.entries()
        entries[7]["lowered_for"] = [{"signed_off": "meter", "response": "warn", "words": "w"}]
        with self.assertRaisesRegex(ValueError, "SR-08: an emergency never carries lowered_for"):
            rules.load_rules(write_rules(entries))

    def test_a_lowering_not_lower_or_naming_nothing_known_is_refused_by_the_loader(self) -> None:
        for lowering, message in (({"signed_off": "meter", "response": "stop", "words": "w"}, "not lower than"),
                                  ({"signed_off": "roof", "response": "warn", "words": "w"}, "signed_off 'roof'"),
                                  ({"role": "boss", "response": "warn", "words": "w"}, "role 'boss'"),
                                  ({"signed_off": "meter", "role": "qualified", "response": "warn", "words": "w"}, "exactly one")):
            entries = self.entries()
            entries[3]["lowered_for"] = [lowering]
            with self.subTest(lowering=lowering), self.assertRaisesRegex(ValueError, message):
                rules.load_rules(write_rules(entries))


class TheReadsField(unittest.TestCase):
    """TODO 1.10: `reads` is data in rules.json, in the fingerprint only when it is not "both", and only SR-07, SR-08 and SR-09 read the words only."""

    def entries(self) -> list[dict]:
        """The real rules.json entries, to be altered into a planted break."""
        return json.loads(rules.RULES_PATH.read_text())

    def test_only_sr_07_sr_08_and_sr_09_read_the_words_only(self) -> None:
        self.assertEqual({rule.rule_id for rule in rules.load_rules() if rule.reads == "words"}, {"SR-07", "SR-08", "SR-09"})
        self.assertEqual({rule.rule_id for rule in rules.load_rules() if rule.reads == "both"}, {f"SR-{n:02d}" for n in (1, 2, 3, 4, 5, 6, 10, 11, 12, 13, 14)})

    def test_reads_changed_with_no_new_entry_is_refused(self) -> None:
        removed = self.entries()
        del removed[6]["reads"]
        with self.assertRaisesRegex(ValueError, "SR-07: the rule changed since its last change entry"):
            rules.load_rules(write_rules(removed))
        added = self.entries()
        added[3]["reads"] = "words"
        with self.assertRaisesRegex(ValueError, "SR-04: the rule changed since its last change entry"):
            rules.load_rules(write_rules(added))

    def test_a_bad_reads_value_is_refused_by_the_loader(self) -> None:
        bad = self.entries()
        bad[6]["reads"] = "passages"
        with self.assertRaisesRegex(ValueError, "SR-07: reads 'passages' is not one of both, words"):
            rules.load_rules(write_rules(bad))

    def test_a_rule_that_reads_both_keeps_the_fingerprint_it_had_and_one_that_reads_words_adds_reads(self) -> None:
        rule = rules.rule_from_entry(self.entries()[6])
        fields = {"triggers": list(rule.triggers), "words_shown": rule.words_shown, "response": rule.response}
        plain = json.dumps(fields, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        with_reads = json.dumps({**fields, "reads": "words"}, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        self.assertEqual(rules.rule_fingerprint(rule), hashlib.sha256(with_reads.encode("utf-8")).hexdigest())
        self.assertNotEqual(rules.rule_fingerprint(rule), hashlib.sha256(plain.encode("utf-8")).hexdigest())
