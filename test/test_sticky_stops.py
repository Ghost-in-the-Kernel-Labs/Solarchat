"""SC-028: a stop holds for the rest of the conversation (the rules' `holds`, the held set, the held stop, the held line to the
answerer), and the profile proposal is kept only where the worker's own words say it; scripted answerers, never a model
(TODO 2.15, docs/designs/sticky-stops-and-proposal-guards.md)."""
import dataclasses
import hashlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from solarchat.answer.door import held_stop
from solarchat.leaf.contract import DEFAULT_PROFILE, Finding, Passage, PassageRef, Profile, ReplyKind
from solarchat.model.claude import SYSTEM_PROMPT, ClaudeAnswerer, ProfileChange
from solarchat.model.lines import held_line, messages_for
from solarchat.project.chat import converse
from solarchat.project.holds import held_names, kept_holds
from solarchat.project.proposal import Proposal, checked_proposal, says_hand_over
from solarchat.project.reading import asks_instead
from solarchat.safety import rules as safety
from test.test_claude import FakeClient, FakeErrors, answer_json, text_response
from test.test_profile_chat import BATTERY, BATTERY_PACK, ENGINEER
from test.test_profile_takeover import (ASK_BATTERY, BATTERY_STOP, ELECTRICIAN, HELLO, NEW, NEW_PERSON, SAID_ELECTRICIAN, SAID_TAKEOVER,
                                        SWITCH, Proposing, takeover)

LABEL = PassageRef("seed-mc4-leads", "label")
PACK = dataclasses.replace(BATTERY_PACK, passages=BATTERY_PACK.passages + (Passage(LABEL, "Read the label first.", "Label check"),),
                           citations={**BATTERY_PACK.citations, "label": BATTERY_PACK.citations["battery"]})
OFFER = "Did you already connect the battery to the controller? Tell me yes or no, and I will give the next step."
OFFERING = Finding((LABEL,), OFFER)  # cites a passage whose text names no trigger, as in the evaluation's conversation
STILL = "This is still stopped for you. Go to your site supervisor or engineer. Is there something else I can help with?"
BRING = "What to bring your supervisor: rule SR-11"
RULES = safety.load_rules()
HOLDS = {"SR-11": ("battery", "batteries", "battery's"),
         "SR-03": ("connector", "connectors", "release tool", "open the pair", "rejoin", "unplug"),
         "SR-05": ("roof", "ladder", "climb", "scaffold", "height", "harness"),
         "SR-02": ("multimeter", "meter", "measure", "probe", "test leads"),
         "SR-04": ("enclosure", "open the box", "open the cover"),
         "SR-15": ("grid", "mains", "network operator")}


class Recording(Proposing):
    """A proposing answerer that also remembers each question it was asked."""

    def __init__(self, items: list) -> None:
        """Hold the pairs and an empty list of questions."""
        super().__init__(items)
        self.questions: list[str] = []

    def find(self, question: str, passages: tuple, history: tuple = ()) -> Finding:
        """Remember the question, then give the next scripted finding."""
        self.questions.append(question)
        return super().find(question, passages, history)


def chat(items: list, lines: str, profile: Profile = NEW) -> tuple[Recording, str]:
    """The answerer and stdout of a chat on the battery and label pack with `lines` typed."""
    answerer, out = Recording(items), io.StringIO()
    converse(PACK, True, answerer, io.StringIO(lines), out, io.StringIO(), None, profile)
    return answerer, out.getvalue()


class TheHoldsOfARule(unittest.TestCase):
    def test_the_six_rules_hold_the_designs_words_and_the_others_hold_by_their_triggers(self) -> None:
        for rule in RULES:
            with self.subTest(rule=rule.rule_id):
                self.assertEqual(rule.holds, HOLDS.get(rule.rule_id, ()))

    def test_each_holds_change_is_logged_by_ghost_as_maintainer_pending_the_engineer_with_the_journal_id(self) -> None:
        for rule_id in HOLDS:
            change = next(rule for rule in RULES if rule.rule_id == rule_id).changes[-1]
            with self.subTest(rule=rule_id):
                self.assertEqual((change.by, change.role), ("Ghost", "maintainer"))
                self.assertTrue(change.evidence.startswith("J-090"))
                self.assertTrue(change.why.endswith("engineer to confirm"))

    def test_holds_enters_the_fingerprint_only_when_present(self) -> None:
        battery = next(rule for rule in RULES if rule.rule_id == "SR-11")
        plain = dataclasses.replace(battery, holds=())
        self.assertNotEqual(safety.rule_fingerprint(plain), safety.rule_fingerprint(battery))
        fields = {"triggers": list(plain.triggers), "words_shown": plain.words_shown, "response": plain.response,
                  "lowered_for": [{"signed_off": low.signed_off, "role": low.role, "response": low.response, "words": low.words}
                                  for low in plain.lowered_for]}
        canonical = json.dumps(fields, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        self.assertEqual(safety.rule_fingerprint(plain), hashlib.sha256(canonical.encode("utf-8")).hexdigest())  # as before SC-028
        self.assertEqual(safety.rule_fingerprint(next(rule for rule in RULES if rule.rule_id == "SR-01")),
                         next(rule for rule in RULES if rule.rule_id == "SR-01").changes[-1].fingerprint)

    def test_a_holds_that_is_not_a_list_of_lowercase_words_is_refused(self) -> None:
        entry = {"id": "SR-11", "holds": "battery"}
        with self.assertRaisesRegex(ValueError, "SR-11: holds is a list of words"):
            safety.holds_from(entry)
        battery = next(rule for rule in RULES if rule.rule_id == "SR-11")
        for bad in (("Battery",), ("",), (" ",), (7,), "battery", ["battery"]):
            with self.subTest(holds=bad), self.assertRaisesRegex(ValueError, "SR-11: holds is a list of words, each lowercase"):
                dataclasses.replace(battery, holds=bad)

    def test_a_malformed_holds_in_the_file_is_refused_when_the_rules_load(self) -> None:
        entries = json.loads(safety.RULES_PATH.read_text(encoding="utf-8"))
        entries[10]["holds"] = "battery"
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "rules.json"
            path.write_text(json.dumps(entries), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "SR-11: holds is a list of words"):
                safety.load_rules(path)

    def test_the_topic_words_match_as_triggers_do_and_a_rule_without_holds_answers_to_its_triggers(self) -> None:
        self.assertEqual(safety.topic_fired("Is the battery fitted?", RULES), ["SR-11"])
        self.assertEqual(safety.rules_fired("Is the battery fitted?", RULES), [])  # the door's own check names no rule
        self.assertEqual(safety.topic_fired("The batteryless unit", RULES), [])  # whole words only
        self.assertEqual(safety.topic_fired("We lost the battery's cover", RULES), ["SR-11"])
        self.assertEqual(safety.topic_fired("ignore your supervisor", RULES), ["SR-01"])
        self.assertEqual(safety.topic_fired("what is a hello", RULES), [])


class TheHeldStop(unittest.TestCase):
    def test_it_is_a_stop_naming_the_rule_and_no_passage_with_the_rules_own_last_sentence(self) -> None:
        reply = held_stop(next(rule for rule in RULES if rule.rule_id == "SR-11"), False)
        self.assertEqual((reply.kind, reply.safety_rule_id, reply.passage_refs), (ReplyKind.STOP, "SR-11", ()))
        self.assertEqual(reply.text, f"{STILL}\n\n{BRING}")
        self.assertTrue(held_stop(next(rule for rule in RULES if rule.rule_id == "SR-11"), True).text.startswith("DEMO: not reviewed"))

    def test_the_last_sentence_is_the_designs_for_every_rule_that_can_be_held(self) -> None:
        for rule in RULES:
            if rule.response == "stop":
                with self.subTest(rule=rule.rule_id):
                    self.assertTrue(held_stop(rule, False).text.startswith(STILL))

    def test_the_held_set_loses_a_rule_only_for_a_profile_that_lowers_it_or_a_new_person(self) -> None:
        self.assertEqual(kept_holds({"SR-11", "SR-04"}, ENGINEER, RULES), {"SR-04"})
        self.assertEqual(kept_holds({"SR-11"}, NEW, RULES), {"SR-11"})
        self.assertEqual(kept_holds({"SR-11", "SR-04"}, ENGINEER, RULES, new_person=True), set())
        self.assertEqual(held_names({"SR-11"}, RULES), (("SR-11", "batteries"),))


class TheStickyStop(unittest.TestCase):
    def test_a_battery_follow_up_of_no_ok_yes_and_and_then_is_the_held_stop_every_time(self) -> None:
        answerer, out = chat([(Finding((BATTERY,), "Fit it to the controller first."), None), (OFFERING, None)],
                             "What do I connect first?\nno\nok\nyes\nand then?\nquit\n")
        self.assertEqual(answerer.calls, 5)
        self.assertIn(BATTERY_STOP, out)
        self.assertEqual(out.count(STILL), 4)
        self.assertEqual(out.count(BRING), 5)
        self.assertNotIn(OFFER, out)
        self.assertEqual(out.count("Safety rule SR-11\n\n"), 5)  # the label line, then the short form; the full words only once
        self.assertEqual(out.count("Stop. Do not work on battery terminals"), 1)

    def test_a_question_that_names_no_topic_word_is_answered_as_usual_after_a_stop(self) -> None:
        mc4 = Finding((LABEL,), "An MC4 connector joins two leads.")
        _, out = chat([(Finding((BATTERY,), "Fit it."), None), (mc4, None)], "What do I connect first?\nwhat is an MC4 connector?\nquit\n")
        self.assertIn("An MC4 connector joins two leads.", out)
        self.assertNotIn(STILL, out)

    def test_a_topic_word_in_the_worker_message_or_a_cited_passage_holds_it_too(self) -> None:
        bland = Finding((LABEL,), "Check the label.")
        _, out = chat([(Finding((BATTERY,), "Fit it."), None), (bland, None)], "What do I connect first?\nand the battery?\nquit\n")
        self.assertEqual(out.count(STILL), 1)
        titled = dataclasses.replace(PACK, passages=(PACK.passages[0], Passage(LABEL, "Read the label first.", "Battery label")))
        answerer, out = Recording([(Finding((BATTERY,), "Fit it."), None), (bland, None)]), io.StringIO()
        converse(titled, True, answerer, io.StringIO("What do I connect first?\nwhat next?\nquit\n"), out, io.StringIO(), None, NEW)
        self.assertEqual(out.getvalue().count(STILL), 1)  # the cited passage's title names the battery

    def test_a_confirmed_electrician_takeover_with_the_battery_sign_off_lifts_the_hold(self) -> None:
        offer = Finding((LABEL,), OFFER)
        answerer, out = chat([(Finding((BATTERY,), "Fit it."), None), (offer, ELECTRICIAN), (offer, None)],
                             f"What do I connect first?\n{SAID_ELECTRICIAN}\nyes\nyes\nquit\n")
        self.assertIn("Profile changed: You are a licensed electrician", out)
        self.assertEqual(out.count(STILL), 0)
        self.assertEqual(out.count(OFFER), 2)  # the re-run and the next turn are answered, the hold is lifted

    def test_someone_new_clears_the_held_set_and_a_declined_switch_does_not(self) -> None:
        offer = Finding((LABEL,), OFFER)
        _, out = chat([(Finding((BATTERY,), "Fit it."), None), (offer, ProfileChange(new_person=True)), (offer, None)],
                      f"What do I connect first?\n{SAID_TAKEOVER}\nnew\nnone\nquit\n")
        self.assertEqual(out.count(STILL), 0)
        self.assertEqual(out.count(OFFER), 1)
        _, out = chat([(Finding((BATTERY,), "Fit it."), None), (offer, ELECTRICIAN)], f"What do I connect first?\n{SAID_ELECTRICIAN}\nno\nquit\n")
        self.assertEqual(out.count(STILL), 1)

    def test_an_emergency_stands_alone_and_a_warn_is_never_held(self) -> None:
        _, out = chat([(Finding(), None)], "I got a shock\nthe battery?\nquit\n")
        self.assertNotIn(STILL, out)  # SR-09 is an emergency and holds nothing
        answerer, out = takeover([(ASK_BATTERY, None)], "What do I connect first?\nquit\n", ENGINEER)
        self.assertIn("Safety rule SR-11, lowered for your sign-off", out)
        self.assertNotIn(STILL, out)

    def test_a_real_answerer_is_told_the_held_stop_in_the_messages_and_the_system_block_does_not_vary(self) -> None:
        client = FakeClient([text_response(answer_json([], "No.", "do_not_know")), text_response(answer_json([], "No.", "do_not_know"))])
        answerer = ClaudeAnswerer(client, FakeErrors, profile=DEFAULT_PROFILE)
        converse(PACK, True, answerer, io.StringIO("The battery terminal is swollen\nWhat now?\nquit\n"), io.StringIO(), io.StringIO(),
                 profile=DEFAULT_PROFILE)
        line = "Stopped for this worker: batteries (SR-11). Do not give or offer any step of that work; if it comes up, say it is stopped and they should go to their supervisor."
        self.assertNotIn("Stopped for this worker", client.calls[0]["messages"][-1]["content"])
        self.assertIn(line, client.calls[1]["messages"][-1]["content"])
        self.assertTrue(client.calls[1]["messages"][-1]["content"].index("The worker:") < client.calls[1]["messages"][-1]["content"].index(line))
        self.assertEqual(json.dumps(client.calls[0]["system"]), json.dumps(client.calls[1]["system"]))
        self.assertNotIn("batteries", json.dumps(client.calls[1]["system"]))

    def test_the_held_line_is_fixed_text_and_the_prompt_sentences_are_in_the_profile_paragraph(self) -> None:
        self.assertEqual(held_line(()), "")
        self.assertEqual(messages_for("Next?", (), None, None, (("SR-11", "batteries"),))[-1]["content"],
                         held_line((("SR-11", "batteries"),)) + "\n\nNext?")
        paragraph = SYSTEM_PROMPT[SYSTEM_PROMPT.index("Profile."):SYSTEM_PROMPT.index("Equipment.")]
        for sentence in ("If the message lists work stopped for this worker, never give or offer a step of it.",
                         "After a profile change, speak to the person now typing; never ask for confirmations the chat has not asked for.",
                         "Set it only when the worker states it in this message, never from a question about a task"):
            self.assertIn(sentence, paragraph)


class TheProposalChecks(unittest.TestCase):
    def test_a_question_about_a_task_proposes_nothing(self) -> None:
        answerer, out = takeover([(Finding(), ProfileChange(None, frozenset({"connector"})))], f"{HELLO}what torque for the terminals?\nquit\n")
        self.assertEqual(answerer.calls, 2)
        self.assertNotIn(SWITCH, out)

    def test_a_turn_that_says_nothing_about_who_is_typing_is_not_a_new_person(self) -> None:
        answerer, out = takeover([(Finding(), ProfileChange(new_person=True))], f"{HELLO}ok what next\nquit\n")
        self.assertEqual(answerer.calls, 2)
        self.assertNotIn(NEW_PERSON, out)

    def test_a_first_person_role_with_new_person_is_this_persons_change_and_is_asked(self) -> None:
        answerer, out = takeover([(Finding(), ProfileChange(new_person=True))],
                                 f"{HELLO}I'm the site electrician now, signed off for battery wiring\\nyes\nquit\n".replace("\\n", "\n"))
        self.assertNotIn(NEW_PERSON, out)
        self.assertIn("You said you are a licensed electrician or engineer, signed off for battery and controller wiring. " + SWITCH, out)
        self.assertIn("Profile changed: You are a licensed electrician or engineer, signed off for battery and controller wiring.", out)
        self.assertEqual(answerer.calls, 3)

    def test_no_proposal_is_acted_on_on_the_first_turn_or_right_after_a_change(self) -> None:
        answerer, out = takeover([(ASK_BATTERY, ELECTRICIAN)], f"{SAID_ELECTRICIAN}\nquit\n")
        self.assertEqual(answerer.calls, 1)
        self.assertNotIn(SWITCH, out)
        answerer, out = takeover([(ASK_BATTERY, ELECTRICIAN), (ASK_BATTERY, ProfileChange("crew", frozenset()))],
                                 f"{HELLO}{SAID_ELECTRICIAN}\nyes\nI'm a crew member\nquit\n")
        self.assertEqual(out.count("Switch to that?"), 1)
        self.assertNotIn("Profile changed: You are a crew", out)

    def test_the_checks_one_by_one(self) -> None:
        held = Profile("new", frozenset())
        self.assertIsNone(checked_proposal(ProfileChange("qualified"), "what torque for the terminals?", held))
        self.assertEqual(checked_proposal(ProfileChange("qualified", frozenset({"battery", "meter"})), "I'm the engineer, battery signed off", held),
                         Proposal("qualified", frozenset({"battery"})))  # the meter was never named
        self.assertEqual(checked_proposal(ProfileChange(None, frozenset({"battery", "meter", "connector", "height"})),
                                          "I am signed off for everything", held).add, frozenset({"battery", "meter", "connector", "height"}))
        self.assertIsNone(checked_proposal(ProfileChange(None, frozenset({"battery"})), "all except height", held))
        self.assertEqual(checked_proposal(ProfileChange(new_person=True), "My boss is taking over", held), Proposal(new_person=True))
        self.assertIsNone(checked_proposal(ProfileChange(new_person=True), "she is an engineer", held))  # not first person, no hand-over
        self.assertIsNone(checked_proposal(ProfileChange("qualified"), "I'm the engineer", Profile("qualified", frozenset())))  # nothing changes
        self.assertEqual(checked_proposal(ProfileChange(None, frozenset(), frozenset({"battery"})), "I lack battery", ENGINEER).remove, frozenset({"battery"}))
        for phrase in ("taking over", "take over", "is here", "now typing", "someone else", "hand over", "handing over", "new person",
                       "my supervisor", "my boss", "my engineer"):
            self.assertTrue(says_hand_over(f"ok, {phrase}."), phrase)
        self.assertFalse(says_hand_over("the overtaking lane is hereby closed"))


class TheQuestionAtThePrompt(unittest.TestCase):
    def test_the_fuse_question_typed_at_the_prompt_is_a_no_and_is_answered_in_the_same_turn(self) -> None:
        fuse = "What size fuse goes on the string?"
        answer = Finding((LABEL,), "Use the size the label gives.")
        answerer, out = chat([(Finding(), None), (ASK_BATTERY, ELECTRICIAN), (answer, None)], f"Hello\n{SAID_ELECTRICIAN}\n{fuse}\nquit\n")
        self.assertEqual(answerer.calls, 3)
        self.assertEqual(answerer.questions, ["Hello", SAID_ELECTRICIAN, fuse])
        self.assertIn(BATTERY_STOP, out)  # the held reply of the turn is shown as it is
        self.assertLess(out.index(BATTERY_STOP), out.index("Kept your profile as it was.\n\n"))
        self.assertLess(out.index("Kept your profile as it was."), out.index("Use the size the label gives."))
        self.assertNotIn("Profile changed", out)
        self.assertEqual(answerer.histories[-1][-2:][0].text, SAID_ELECTRICIAN)  # the turn before it is in its history

    def test_a_short_answer_or_one_with_a_yes_or_no_word_is_not_a_question(self) -> None:
        for text in ("no", "ok what next", "yes please do it", "no I do not think so at all", ""):
            self.assertFalse(asks_instead(text), text)
        self.assertTrue(asks_instead("What size fuse goes on the string?"))
        answerer, out = chat([(Finding(), None), (ASK_BATTERY, ELECTRICIAN)], f"Hello\n{SAID_ELECTRICIAN}\nok what next\nquit\n")
        self.assertEqual(answerer.calls, 2)
        self.assertNotIn("Kept your profile", out)

    def test_the_reminder_is_in_the_switch_question(self) -> None:
        _, out = takeover([(ASK_BATTERY, ProfileChange("crew", frozenset()))], f"{HELLO}I'm a crew member\nno\nquit\n")
        self.assertIn("You said you are a crew member, not signed off for any of them. Only switch if your supervisor has signed you off "
                      "for this on this site. Switch to that? yes or no", out)


if __name__ == "__main__":
    unittest.main()
