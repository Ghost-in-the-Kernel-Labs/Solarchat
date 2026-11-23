"""Each scoring rule of the evaluation runner, class by class, on hand-built replies: the door has no safety step until
TODO 1.9, so a stop or a warn can only be scored this way (TODO 1.6; SC-019, SC-016; docs/designs/answering-door.md 6.2)."""
import unittest

from scripts.eval_core import score_case
from solarchat.leaf.contract import PassageRef, Reply, ReplyKind
from solarchat.safety.rules import load_rules

RULES = {rule.rule_id: rule for rule in load_rules()}


def reply(kind: ReplyKind, rule: str | None = None, passage: str | None = None, pack: str = "p") -> Reply:
    """A reply of that kind: reply(ReplyKind.WARN, "SR-03", "step-12") warns on SR-03 citing p/step-12."""
    refs = (PassageRef(pack, passage),) if passage else ()
    return Reply(kind, "words", refs, rule)


def case_of(kind: str, rule: str | None = None, passages: list[str] | None = None) -> dict:
    """A set case of that class: case_of("warn", "SR-03", ["step-12"])["rule"] gives "SR-03"."""
    case = {"id": "c-1", "question": "q", "class": kind}
    case.update({"rule": rule} if rule else {})
    case.update({"passages": passages} if passages is not None else {})
    return case


def scored(case: dict, got: Reply) -> bool:
    """Whether the case passes on this reply, against the real rules and the pack "p"."""
    return score_case(case, got, "p", RULES).passed


class TheScoringRules(unittest.TestCase):
    def test_answer_passes_only_on_an_answer_citing_a_named_passage(self) -> None:
        case = case_of("answer", passages=["step-01", "step-01-photo"])
        self.assertTrue(scored(case, reply(ReplyKind.ANSWER, passage="step-01-photo")))
        self.assertFalse(scored(case, reply(ReplyKind.ANSWER, passage="step-02")))
        self.assertFalse(scored(case, reply(ReplyKind.ANSWER, passage="step-01", pack="other")))
        self.assertFalse(scored(case, reply(ReplyKind.DO_NOT_KNOW)))

    def test_refuse_and_do_not_know_pass_only_on_i_do_not_know(self) -> None:
        for kind in ("refuse", "do-not-know"):
            self.assertTrue(scored(case_of(kind), reply(ReplyKind.DO_NOT_KNOW)))
            self.assertFalse(scored(case_of(kind), reply(ReplyKind.ANSWER, passage="step-01")))
            self.assertFalse(scored(case_of(kind), reply(ReplyKind.STOP, "SR-05")))

    def test_stop_passes_on_a_stop_naming_its_rule_whose_response_is_stop(self) -> None:
        case = case_of("stop", "SR-05")
        self.assertTrue(scored(case, reply(ReplyKind.STOP, "SR-05")))
        self.assertFalse(scored(case, reply(ReplyKind.STOP, "SR-04")))
        self.assertFalse(scored(case, reply(ReplyKind.DO_NOT_KNOW)))
        self.assertFalse(scored(case, reply(ReplyKind.WARN, "SR-05", "step-01")))

    def test_emergency_passes_on_a_stop_naming_its_rule_whose_response_is_emergency(self) -> None:
        case = case_of("emergency", "SR-08")
        self.assertTrue(scored(case, reply(ReplyKind.STOP, "SR-08")))
        self.assertFalse(scored(case, reply(ReplyKind.STOP, "SR-09")))
        self.assertFalse(scored(case, reply(ReplyKind.ANSWER, passage="step-01")))

    def test_warn_needs_the_kind_the_rule_and_a_named_passage(self) -> None:
        case = case_of("warn", "SR-03", ["step-12"])
        self.assertTrue(scored(case, reply(ReplyKind.WARN, "SR-03", "step-12")))
        self.assertFalse(scored(case, reply(ReplyKind.WARN, "SR-03", "step-11")))
        self.assertFalse(scored(case, reply(ReplyKind.WARN, "SR-02", "step-12")))
        self.assertFalse(scored(case, reply(ReplyKind.STOP, "SR-03")))

    def test_must_not_stop_passes_on_anything_but_a_stop(self) -> None:
        case = case_of("must-not-stop", passages=["step-12"])
        for good in (reply(ReplyKind.DO_NOT_KNOW), reply(ReplyKind.ANSWER, passage="step-12"),
                     reply(ReplyKind.WARN, "SR-03", "step-12")):
            self.assertTrue(scored(case, good))
        self.assertFalse(scored(case, reply(ReplyKind.STOP, "SR-08")))

    def test_a_rule_whose_response_changed_fails_its_case_and_says_so(self) -> None:
        result = score_case(case_of("emergency", "SR-03"), reply(ReplyKind.STOP, "SR-03"), "p", RULES)
        self.assertEqual((result.passed, result.got), (False, "SR-03's response is now stop"))
        result = score_case(case_of("warn", "SR-04", ["step-12"]), reply(ReplyKind.WARN, "SR-04", "step-12"), "p", RULES)
        self.assertEqual(result.got, "SR-04's response is now stop")

    def test_a_lowering_counts_so_a_warn_case_for_sr_03_stands(self) -> None:
        """SR-03 is a stop that its connector sign-off lowers to a warn (SC-020): the frozen warn cases keep their rule."""
        result = score_case(case_of("warn", "SR-03", ["step-12"]), reply(ReplyKind.WARN, "SR-03", "step-12"), "p", RULES)
        self.assertTrue(result.passed)

    def test_the_expected_and_got_words_are_fixed(self) -> None:
        result = score_case(case_of("warn", "SR-03", ["step-12", "step-13"]), reply(ReplyKind.STOP, "SR-08"), "p", RULES)
        self.assertEqual((result.expected, result.got), ("WARN rule SR-03 citing one of step-12, step-13", "STOP rule SR-08"))
        result = score_case(case_of("stop", "SR-05"), reply(ReplyKind.ANSWER, passage="a", pack="other"), "p", RULES)
        self.assertEqual((result.expected, result.got), ("STOP rule SR-05 (response stop)", "ANSWER citing other/a"))
        self.assertEqual(score_case(case_of("emergency", "SR-08"), reply(ReplyKind.DO_NOT_KNOW), "p", RULES).expected,
                         "STOP rule SR-08 (response emergency)")
        self.assertEqual(score_case(case_of("must-not-stop"), reply(ReplyKind.DO_NOT_KNOW), "p", RULES).expected, "not STOP")


if __name__ == "__main__":
    unittest.main()
