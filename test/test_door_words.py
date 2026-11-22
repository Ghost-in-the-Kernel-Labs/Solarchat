"""The safety rules on the worker's own words (TODO 1.10, docs/designs/worker-words.md; HAD-03, HAD-04, SC-015, SC-016, SC-020)."""
import json
import unittest

from solarchat.answer.door import DO_NOT_KNOW_TEXT, answer
from solarchat.answer.stub import NoAnswer
from solarchat.leaf.contract import DEFAULT_PROFILE, Finding, PassageRef, Profile, ReplyKind, Turn
from solarchat.safety.rules import load_rules, rules_fired
from test.support import ROOT
from test.test_door import GOOD, SEED, VOLTAGE, Spy, one

RULES = {rule.rule_id: rule for rule in load_rules()}
SET = json.loads((ROOT / "evals" / "v1.json").read_text(encoding="utf-8"))["cases"]
CHECK_2 = PassageRef("seed-mc4-leads", "fail-04-check-2")


class TheWordsGiveTheStopWithNoPassage(unittest.TestCase):
    def test_an_emergency_in_the_words_is_given_when_the_answerer_cites_nothing(self) -> None:
        reply = answer("I got a shock from the lead", (GOOD,), False, NoAnswer())
        self.assertEqual((reply.kind, reply.safety_rule_id, reply.passage_refs, reply.text),
                         (ReplyKind.STOP, "SR-09", (), RULES["SR-09"].words_shown))

    def test_an_emergency_in_the_words_is_given_when_the_answerer_breaks_the_contract(self) -> None:
        reply = answer("The connector is sparking", (GOOD,), False, one(PassageRef("good", "invented")))
        self.assertEqual((reply.kind, reply.safety_rule_id), (ReplyKind.STOP, "SR-08"))

    def test_a_stop_in_the_words_names_its_rule_and_no_passage(self) -> None:
        reply = answer("The cable is frayed", (GOOD,), False, NoAnswer())
        self.assertEqual((reply.kind, reply.safety_rule_id, reply.passage_refs), (ReplyKind.STOP, "SR-07", ()))
        self.assertEqual(reply.text, RULES["SR-07"].words_shown + "\n\nWhat to bring your supervisor: rule SR-07")

    def test_a_calm_question_is_still_i_do_not_know_with_no_citation(self) -> None:
        reply = answer("Where is the Voc?", (GOOD,), False, NoAnswer())
        self.assertEqual((reply.kind, reply.text), (ReplyKind.DO_NOT_KNOW, DO_NOT_KNOW_TEXT))

    def test_only_this_turns_question_is_read_never_the_history(self) -> None:
        history = (Turn("user", "The connector is sparking"), Turn("assistant", "Stop. Step back: smoke and sparks."))
        reply = answer("Where is the Voc?", (GOOD,), False, one(VOLTAGE), history=history)
        self.assertEqual((reply.kind, reply.safety_rule_id), (ReplyKind.ANSWER, None))

    def test_the_most_severe_of_words_and_passage_wins_then_the_lowest_id(self) -> None:
        reply = answer("The cable is frayed and I see sparks", (GOOD,), False, one(VOLTAGE))
        self.assertEqual(reply.safety_rule_id, "SR-08")


class AnEmergencyFiresOnTheWordsOnly(unittest.TestCase):
    def test_a_passage_that_lists_smoke_does_not_fire_sr_08_but_the_same_word_in_the_question_does(self) -> None:
        listed = answer("What are the warning signs to watch for after swapping plus and minus?", (SEED,), True, Spy(Finding((CHECK_2,), "Watch.")))
        self.assertEqual((listed.kind, listed.safety_rule_id), (ReplyKind.ANSWER, None))
        reported = answer("There is smoke", (SEED,), True, Spy(Finding((CHECK_2,), "Watch.")))
        self.assertEqual((reported.kind, reported.safety_rule_id), (ReplyKind.STOP, "SR-08"))

    def test_the_real_passage_of_mns_03_fires_no_rule_by_its_text(self) -> None:
        text = next(passage.text for passage in SEED.passages if passage.ref == CHECK_2)
        self.assertIn("smoke", text)
        self.assertEqual([rule_id for rule_id in rules_fired(text) if RULES[rule_id].response != "emergency"], [])

    def test_the_two_emergency_rules_are_the_ones_chosen_by_response_not_by_id(self) -> None:
        self.assertEqual([rule.rule_id for rule in RULES.values() if rule.response == "emergency"], ["SR-08", "SR-09"])


class AWarnFiredByTheWordsAlone(unittest.TestCase):
    QUESTION = "Can I pull connectors apart to move the panel?"

    def test_with_a_cited_passage_it_is_the_answer_with_the_warns_words_before_it(self) -> None:
        reply = answer(self.QUESTION, (GOOD,), False, one(VOLTAGE))
        self.assertEqual((reply.kind, reply.safety_rule_id, reply.passage_refs), (ReplyKind.WARN, "SR-03", (VOLTAGE,)))
        self.assertTrue(reply.text.startswith(RULES["SR-03"].words_shown + "\n\nVoc must be lower.\n\nFrom: "))

    def test_with_no_passage_cited_it_is_an_i_do_not_know_that_carries_the_warns_words_and_names_no_rule(self) -> None:
        reply = answer(self.QUESTION, (GOOD,), False, NoAnswer())
        self.assertEqual((reply.kind, reply.safety_rule_id, reply.passage_refs), (ReplyKind.DO_NOT_KNOW, None, ()))
        self.assertEqual(reply.text, RULES["SR-03"].words_shown + "\n\n" + DO_NOT_KNOW_TEXT)


class TheProfileLowersARuleFiredByTheWords(unittest.TestCase):
    QUESTION = "How do I clean the battery terminals?"
    BATTERY = Profile("qualified", frozenset({"battery"}))

    def test_sr_11_stops_by_default_and_warns_for_the_battery_sign_off(self) -> None:
        stop = answer(self.QUESTION, (GOOD,), False, one(VOLTAGE), profile=DEFAULT_PROFILE)
        self.assertEqual((stop.kind, stop.safety_rule_id), (ReplyKind.STOP, "SR-11"))
        warn = answer(self.QUESTION, (GOOD,), False, one(VOLTAGE), profile=self.BATTERY)
        self.assertEqual((warn.kind, warn.safety_rule_id), (ReplyKind.WARN, "SR-11"))
        self.assertTrue(warn.text.startswith(RULES["SR-11"].lowered_for[0].words))

    def test_a_lowered_rule_fired_with_no_passage_is_not_a_stop(self) -> None:
        reply = answer(self.QUESTION, (GOOD,), False, NoAnswer(), profile=self.BATTERY)
        self.assertEqual((reply.kind, reply.safety_rule_id), (ReplyKind.DO_NOT_KNOW, None))
        self.assertTrue(reply.text.endswith(DO_NOT_KNOW_TEXT))

    def test_an_emergency_in_the_words_is_never_lowered(self) -> None:
        everything = Profile("qualified", frozenset({"meter", "connector", "battery", "height"}))
        reply = answer("I got a shock", (GOOD,), False, NoAnswer(), profile=everything)
        self.assertEqual((reply.kind, reply.safety_rule_id), (ReplyKind.STOP, "SR-09"))


class TheThreeTriggerChanges(unittest.TestCase):
    def test_sr_08_fires_on_smells_burnt_and_burnt_smell(self) -> None:
        for words in ("It is hot and smells burnt", "There is a burnt smell"):
            self.assertIn("SR-08", rules_fired(words))

    def test_sr_07_fires_on_a_broken_or_cracked_glass(self) -> None:
        for words in ("The glass is broken", "the glass is cracked", "My panel is cracked"):
            self.assertIn("SR-07", rules_fired(words))

    def test_sr_14_no_longer_fires_on_a_question_that_says_i_do_not_know_but_still_on_unsure(self) -> None:
        for words in ("I don't know which lead is positive", "I do not know which lead is positive"):
            self.assertNotIn("SR-14", rules_fired(words))
        for words in ("I am unsure", "I am not trained for this", "I have never done this"):
            self.assertIn("SR-14", rules_fired(words))

    def test_each_change_is_logged_by_ghost_on_2026_11_22_with_its_evidence(self) -> None:
        for rule_id in ("SR-07", "SR-08", "SR-14"):
            latest = RULES[rule_id].changes[-1]
            self.assertEqual((latest.date, latest.by, latest.role, latest.evidence),
                             ("2026-11-22", "Ghost", "maintainer", "J-075; docs/designs/worker-words.md"))
            self.assertTrue(latest.why.endswith("engineer to confirm."))


class TheFrozenSetsStopAndEmergencyCases(unittest.TestCase):
    def test_each_fires_its_rule_from_the_words_alone_with_the_stub(self) -> None:
        cases = [case for case in SET if case["class"] in ("stop", "emergency")]
        self.assertEqual(len(cases), 16)
        for case in cases:
            with self.subTest(case=case["id"]):
                reply = answer(case["question"], (SEED,), True, NoAnswer())
                self.assertEqual((reply.kind, reply.safety_rule_id), (ReplyKind.STOP, case["rule"]))

    def test_no_must_not_stop_case_stops_with_the_stub_under_its_profile(self) -> None:
        profiles = {"mns-09": Profile("qualified", frozenset({"meter"}))}
        for case in [case for case in SET if case["class"] == "must-not-stop"]:
            with self.subTest(case=case["id"]):
                reply = answer(case["question"], (SEED,), True, NoAnswer(), profile=profiles.get(case["id"], DEFAULT_PROFILE))
                self.assertNotEqual(reply.kind, ReplyKind.STOP)

    def test_mns_03_with_its_real_passage_cited_is_an_answer(self) -> None:
        case = next(case for case in SET if case["id"] == "mns-03")
        reply = answer(case["question"], (SEED,), True, Spy(Finding((CHECK_2,), "Watch for heat.")))
        self.assertEqual((reply.kind, reply.safety_rule_id), (ReplyKind.ANSWER, None))

    def test_mns_09_with_the_meter_sign_off_is_not_a_stop_whether_or_not_a_passage_is_cited(self) -> None:
        case = next(case for case in SET if case["id"] == "mns-09")
        profile = Profile("qualified", frozenset({"meter"}))
        for finder in (NoAnswer(), one(VOLTAGE)):
            self.assertNotEqual(answer(case["question"], (SEED,), True, finder, profile=profile).kind, ReplyKind.STOP)
