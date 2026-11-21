"""The leaf holds the contract's reply and pack-status rules (docs/CONTRACT.md HAD-03, HAD-04, HAD-06)."""
import json
import unittest

from solarchat.leaf.contract import PassageRef, Reply, ReplyKind, is_demo
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


class PackStatus(unittest.TestCase):
    def test_a_demo_pack_is_demo(self) -> None:
        self.assertTrue(is_demo({"status": "demo"}))

    def test_a_library_pack_is_not_demo(self) -> None:
        self.assertFalse(is_demo({"status": "library"}))

    def test_the_seed_pack_is_demo(self) -> None:
        manifest = json.loads((ROOT / "packs" / "seed-mc4-leads" / "manifest.json").read_text())
        self.assertTrue(is_demo(manifest))
