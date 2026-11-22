"""The leaf holds the contract's reply and pack-status rules (docs/CONTRACT.md HAD-03, HAD-04, HAD-06)."""
import json
import unittest

from solarchat.leaf.contract import (DEFAULT_PROFILE, DEMO_BANNER, MAX_CITED_PASSAGES, Finding, Passage, PassageRef, Profile, Reply,
                                     ReplyKind, SafetyCoverage, SafetyLowering, SafetyRule, SafetyRuleChange, SafetyRuleSource, may_answer)
from test.support import ROOT

STEP = PassageRef("seed-mc4-leads", "step-06")


class TheReply(unittest.TestCase):
    def test_an_answer_with_a_passage_stands(self) -> None:
        self.assertEqual(Reply(ReplyKind.ANSWER, "Join plus to plus.", (STEP,)).passage_refs, (STEP,))

    def test_an_answer_with_no_passage_is_refused(self) -> None:
        with self.assertRaisesRegex(ValueError, "HAD-03"):
            Reply(ReplyKind.ANSWER, "Join plus to plus.")

    def test_do_not_know_names_no_passage(self) -> None:
        self.assertEqual(Reply(ReplyKind.DO_NOT_KNOW, "I do not know.").passage_refs, ())
        with self.assertRaisesRegex(ValueError, "HAD-03"):
            Reply(ReplyKind.DO_NOT_KNOW, "I do not know.", (STEP,))

    def test_a_stop_names_its_rule_and_nothing_else_does(self) -> None:
        self.assertEqual(Reply(ReplyKind.STOP, "Stop; call the supervisor.", safety_rule_id="live-dc").safety_rule_id, "live-dc")
        with self.assertRaisesRegex(ValueError, "HAD-04"):
            Reply(ReplyKind.STOP, "Stop; call the supervisor.")
        with self.assertRaisesRegex(ValueError, "HAD-04"):
            Reply(ReplyKind.ANSWER, "Join plus to plus.", (STEP,), safety_rule_id="live-dc")


class TheWarn(unittest.TestCase):
    """A warn (SC-015) names its rule and at least one passage; nothing else does both."""

    def test_a_warn_with_a_passage_and_a_rule_stands(self) -> None:
        warn = Reply(ReplyKind.WARN, "Never pull connectors apart under load.", (STEP,), "SR-03")
        self.assertEqual((warn.kind, warn.passage_refs, warn.safety_rule_id), (ReplyKind.WARN, (STEP,), "SR-03"))

    def test_a_warn_with_no_passage_is_refused(self) -> None:
        with self.assertRaisesRegex(ValueError, "HAD-03"):
            Reply(ReplyKind.WARN, "Never pull connectors apart under load.", (), "SR-03")

    def test_a_warn_with_no_rule_is_refused(self) -> None:
        with self.assertRaisesRegex(ValueError, "HAD-04"):
            Reply(ReplyKind.WARN, "Never pull connectors apart under load.", (STEP,))

    def test_a_stop_still_names_no_passage_and_a_do_not_know_still_names_no_rule(self) -> None:
        with self.assertRaisesRegex(ValueError, "HAD-03"):
            Reply(ReplyKind.STOP, "Stop.", (STEP,), "SR-03")
        with self.assertRaisesRegex(ValueError, "HAD-04"):
            Reply(ReplyKind.DO_NOT_KNOW, "I do not know.", (), "SR-03")

    def test_there_are_four_kinds(self) -> None:
        self.assertEqual({kind.value for kind in ReplyKind}, {"answer", "do not know", "stop", "warn"})


class PackStatus(unittest.TestCase):
    def test_a_field_pack_answers_in_either_mode(self) -> None:
        for demo_mode in (False, True):
            self.assertTrue(may_answer({"status": "field"}, demo_mode))

    def test_a_demo_pack_answers_only_in_demo_mode(self) -> None:
        self.assertTrue(may_answer({"status": "demo"}, True))
        self.assertFalse(may_answer({"status": "demo"}, False))

    def test_a_status_it_does_not_know_never_answers(self) -> None:
        unknown = [{}, {"status": ""}, {"status": "library"}, {"status": "Library"}, {"status": "Field"}, {"status": "admitted"}, {"status": None}, {"status": 1}]
        for manifest in unknown:
            for demo_mode in (False, True):
                self.assertFalse(may_answer(manifest, demo_mode), (manifest, demo_mode))

    def test_the_seed_pack_answers_only_in_demo_mode(self) -> None:
        manifest = json.loads((ROOT / "packs" / "seed-mc4-leads" / "manifest.json").read_text())
        self.assertTrue(may_answer(manifest, True))
        self.assertFalse(may_answer(manifest, False))


class TheAnsweringTypes(unittest.TestCase):
    def test_a_passage_without_a_title_stays_valid(self) -> None:
        self.assertEqual(Passage(STEP, "Join plus to plus.").title, "")
        self.assertEqual(Passage(STEP, "Join plus to plus.", "Join the leads").title, "Join the leads")

    def test_an_empty_finding_is_i_do_not_know(self) -> None:
        self.assertEqual((Finding().refs, Finding().text, Finding().score), ((), "", 0.0))

    def test_a_finding_with_refs_and_text_stands(self) -> None:
        self.assertEqual(Finding((STEP,), "Join plus to plus.", 4.5).score, 4.5)

    def test_refs_without_text_or_text_without_refs_are_refused(self) -> None:
        with self.assertRaises(ValueError):
            Finding((STEP,), "")
        with self.assertRaises(ValueError):
            Finding((), "Join plus to plus.")

    def test_the_constants_say_what_the_decision_says(self) -> None:
        self.assertEqual(MAX_CITED_PASSAGES, 3)
        self.assertEqual(DEMO_BANNER, "DEMO: not reviewed by an engineer, do not use on a site")


class TheSafetyCoverage(unittest.TestCase):
    """SC-024: a declaration is refused at construction when incomplete."""

    DECLARED = {"by": "Ghost", "role": "maintainer", "date": "2026-11-22", "evidence": "J-072"}

    def test_a_whole_declaration_stands_with_or_without_declared(self) -> None:
        self.assertEqual(SafetyCoverage("SR-02", "warn", ("a", "b"), self.DECLARED).passages, ("a", "b"))
        self.assertIsNone(SafetyCoverage("SR-03", "stop", ("a",)).declared)
        self.assertEqual(SafetyCoverage("SR-08", "emergency", ("a",)).response, "emergency")

    def test_each_incomplete_declaration_is_refused(self) -> None:
        for arguments in (("SR-2", "warn", ("a",)), ("SR-02", "halt", ("a",)), ("SR-02", "emergency", ("a",)),
                          ("SR-08", "warn", ("a",)), ("SR-09", "stop", ("a",)), ("SR-02", "warn", ()), ("SR-02", "warn", (" ",)),
                          ("SR-02", "warn", ("a",), {"by": "Ghost"}), ("SR-02", "warn", ("a",), {**self.DECLARED, "role": ""})):
            with self.subTest(arguments=arguments), self.assertRaisesRegex(ValueError, "SC-0(24|16)"):
                SafetyCoverage(*arguments)


class TheProfile(unittest.TestCase):
    """SC-020: a profile is a role and the sign-offs, refused at construction otherwise."""

    def test_each_role_and_each_sign_off_stands(self) -> None:
        for role in ("new", "crew", "qualified"):
            self.assertEqual(Profile(role, frozenset()).role, role)
        everything = frozenset({"meter", "connector", "battery", "height"})
        self.assertEqual(Profile("qualified", everything).signed_off, everything)

    def test_the_default_is_the_newest_contractor_signed_off_for_nothing(self) -> None:
        self.assertEqual(DEFAULT_PROFILE, Profile("new", frozenset()))

    def test_an_unknown_role_or_sign_off_or_a_signed_off_that_is_not_a_frozenset_is_refused(self) -> None:
        for arguments in (("boss", frozenset()), ("", frozenset()), ("new", frozenset({"roof"})),
                          ("qualified", frozenset({"meter", "welding"})), ("new", ["meter"]), ("new", {"meter"}), ("new", None)):
            with self.subTest(arguments=arguments), self.assertRaisesRegex(ValueError, "SC-020"):
                Profile(*arguments)


class TheLowerings(unittest.TestCase):
    """SC-020: a rule's lowered_for is refused at construction when it breaks the decision."""

    def rule(self, response: str = "stop", lowerings: tuple = ()) -> SafetyRule:
        """A rule of this response holding these lowerings: self.rule("stop", (SafetyLowering("warn", "w", signed_off="meter"),))."""
        return SafetyRule("SR-02", "t", "a", ("probe",), "Stop. Go to your site supervisor or engineer.",
                          (SafetyRuleSource("HSE", "https://www.hse.gov.uk/"),), response,
                          (SafetyRuleChange("2026-11-22", "Ghost", "maintainer", "w.", "J-074"),), lowered_for=lowerings)

    def test_a_rule_has_no_lowerings_by_default(self) -> None:
        self.assertEqual(self.rule().lowered_for, ())

    def test_a_stop_may_lower_to_warn_for_a_sign_off_or_a_role(self) -> None:
        by_sign_off = SafetyLowering("warn", "You are signed off.", signed_off="meter")
        by_role = SafetyLowering("warn", "You are qualified.", role="qualified")
        self.assertEqual(self.rule("stop", (by_sign_off, by_role)).lowered_for, (by_sign_off, by_role))

    def test_an_emergency_never_carries_a_lowering(self) -> None:
        with self.assertRaisesRegex(ValueError, "an emergency never carries lowered_for"):
            self.rule("emergency", (SafetyLowering("warn", "w", signed_off="meter"),))
        with self.assertRaisesRegex(ValueError, "an emergency never carries lowered_for"):
            self.rule("emergency", (SafetyLowering("stop", "w", signed_off="meter"),))

    def test_a_lowering_that_is_not_lower_than_its_rule_is_refused(self) -> None:
        for rule_response, lowered in (("stop", "stop"), ("stop", "emergency"), ("warn", "warn"), ("warn", "stop"), ("stop", "halt")):
            with self.subTest(rule=rule_response, lowering=lowered), self.assertRaisesRegex(ValueError, "not lower than the rule's"):
                self.rule(rule_response, (SafetyLowering(lowered, "w", signed_off="meter"),))

    def test_a_lowering_names_exactly_one_known_sign_off_or_role(self) -> None:
        for lowering, message in ((SafetyLowering("warn", "w"), "exactly one"),
                                  (SafetyLowering("warn", "w", signed_off="meter", role="qualified"), "exactly one"),
                                  (SafetyLowering("warn", "w", signed_off="roof"), "signed_off 'roof'"),
                                  (SafetyLowering("warn", "w", role="boss"), "role 'boss'"),
                                  (SafetyLowering("warn", " ", signed_off="meter"), "has words"),
                                  ({"response": "warn"}, "lowerings only")):
            with self.subTest(lowering=lowering), self.assertRaisesRegex(ValueError, message):
                self.rule("stop", (lowering,))

    def test_a_lowering_matches_the_sign_off_or_the_role_and_nothing_else(self) -> None:
        meter, qualified = SafetyLowering("warn", "w", signed_off="meter"), SafetyLowering("warn", "w", role="qualified")
        self.assertTrue(meter.matches(Profile("new", frozenset({"meter"}))))
        self.assertFalse(meter.matches(Profile("qualified", frozenset({"battery"}))))
        self.assertFalse(meter.matches(DEFAULT_PROFILE))
        self.assertTrue(qualified.matches(Profile("qualified", frozenset())))
        self.assertFalse(qualified.matches(Profile("crew", frozenset({"meter"}))))
