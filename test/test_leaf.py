"""The leaf holds the contract's reply and pack-status rules (docs/CONTRACT.md HAD-03, HAD-04, HAD-06)."""
import json
import unittest

from solarchat.leaf.contract import PassageRef, Reply, ReplyKind, may_answer
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
