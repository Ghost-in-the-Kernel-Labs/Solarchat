"""The battery-wiring passages of the seed pack (J-080): SR-11 fires on them when cited, and a battery sign-off lowers it (SC-016, SC-020)."""
import unittest

from solarchat.answer.door import answer
from solarchat.leaf.contract import DEFAULT_PROFILE, Finding, PassageRef, Profile, Reply, ReplyKind
from solarchat.safety.rules import load_rules
from test.test_door import SEED, Spy

RULES = {rule.rule_id: rule for rule in load_rules()}
TERMINALS = PassageRef("seed-mc4-leads", "battery-terminals")
QUESTION = "Which way round does the battery cable go on the controller?"


def ask(profile: Profile) -> Reply:
    """The reply to QUESTION when the answerer cites battery-terminals, in the demo pack, under the profile."""
    return answer(QUESTION, (SEED,), True, Spy(Finding((TERMINALS,), "The battery has two screw terminals.")), profile=profile)


class TheBatteryPassagesFireSR11WhenCited(unittest.TestCase):
    def test_a_new_worker_is_stopped_by_sr_11(self) -> None:
        reply = ask(DEFAULT_PROFILE)
        self.assertEqual((reply.kind, reply.safety_rule_id), (ReplyKind.STOP, "SR-11"))
        self.assertIn("rule SR-11", reply.text)
        self.assertIn("Stop. Do not work on battery terminals", reply.text)

    def test_a_battery_sign_off_gets_the_lowered_warn_with_the_passage(self) -> None:
        reply = ask(Profile("qualified", frozenset({"battery"})))
        self.assertEqual((reply.kind, reply.safety_rule_id), (ReplyKind.WARN, "SR-11"))
        self.assertEqual(reply.passage_refs, (TERMINALS,))
        self.assertIn(RULES["SR-11"].lowered_for[0].words, reply.text)
        self.assertIn("Charge controller: the battery terminals", reply.text)

    def test_the_seed_pack_holds_the_four_passages_cited_to_s4_with_a_printed_page(self) -> None:
        by_id = {passage.ref.passage_id for passage in SEED.passages}
        for passage_id, page in (("battery-terminals", "13"), ("battery-connect", "13"), ("battery-torque", "13"), ("battery-fuse", "11")):
            self.assertIn(passage_id, by_id)
            self.assertEqual(SEED.citations[passage_id], [{"source": "S10", "page": page}])
