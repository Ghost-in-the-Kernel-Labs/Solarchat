"""SC-026: a profile change proposed by the model (the schema's field, its validation, `ClaudeAnswerer.proposal`) and settled by the
chat (less say at once, more say on a yes, a new person, the turn answered again); a fake client and a scripted answerer that
proposes, never a model (TODO 2.12)."""
import io
import json
import unittest

from solarchat.answer.door import DO_NOT_KNOW_TEXT
from solarchat.leaf.contract import DEMO_BANNER, Finding, Profile, Turn
from solarchat.model import claude
from solarchat.model.claude import SCHEMA, SYSTEM_PROMPT, ClaudeAnswerer, ProfileChange
from solarchat.project import chat
from solarchat.project.chat import ROLE_QUESTION, SIGN_OFF_QUESTION, converse, read_yes
from solarchat.project.speech import Speaker
from test.test_claude import FakeClient, FakeErrors, answer_json, text_response
from test.test_cli import PACK, Scripted
from test.test_profile_chat import BATTERY, BATTERY_PACK, ENGINEER
from test.test_speech import Fake, found


CHANGE = {"role": "qualified", "add": ["battery"], "remove": [], "new_person": False}


def proposing(change: object, reply: str = "Check the label.") -> FakeClient:
    """A fake client whose one reply carries `change` as its profile_change."""
    return FakeClient([text_response(dict(answer_json([], reply, "do_not_know"), profile_change=change))])


def proposal_after(change: object, profile: Profile | None = None) -> tuple[object, Finding]:
    """The answerer's proposal and finding after one find on the good pack with this profile_change."""
    answerer = ClaudeAnswerer(proposing(change), FakeErrors, profile=profile)
    finding = answerer.find("Who?", PACK.passages)
    return answerer.proposal, finding


class TheProposal(unittest.TestCase):
    def test_a_valid_proposal_is_kept(self) -> None:
        proposal, _ = proposal_after(CHANGE, Profile("new", frozenset()))
        self.assertEqual(proposal, ProfileChange("qualified", frozenset({"battery"})))

    def test_an_unknown_role_or_sign_off_drops_the_proposal_and_never_the_reply(self) -> None:
        for change in (dict(CHANGE, role="boss"), dict(CHANGE, add=["roof"]), dict(CHANGE, remove=["roof"]), dict(CHANGE, new_person="yes"),
                       dict(CHANGE, add="battery"), {"role": "qualified"}, "qualified", 7):
            with self.subTest(change=change):
                proposal, finding = proposal_after(change)
                self.assertIsNone(proposal)
                self.assertEqual(finding, Finding())  # do_not_know: the reply was read as it always is

    def test_a_proposal_equal_to_the_profile_or_empty_is_dropped(self) -> None:
        held = Profile("qualified", frozenset({"battery"}))
        self.assertIsNone(proposal_after(CHANGE, held)[0])
        self.assertIsNone(proposal_after(dict(CHANGE, role=None, add=[]), held)[0])
        self.assertIsNone(proposal_after(dict(CHANGE, role=None, add=[], remove=["meter"]), held)[0])
        self.assertIsNone(proposal_after(None, held)[0])
        self.assertEqual(proposal_after(dict(CHANGE, add=["battery", "meter"]), held)[0], ProfileChange(None, frozenset({"meter"})))

    def test_a_sign_off_added_and_removed_is_only_removed_and_a_new_person_is_kept(self) -> None:
        held = Profile("new", frozenset({"battery"}))
        self.assertEqual(proposal_after(dict(CHANGE, role=None, add=["battery", "meter"], remove=["battery"]), held)[0],
                         ProfileChange(None, frozenset({"meter"}), frozenset({"battery"})))
        self.assertEqual(proposal_after(dict(CHANGE, role=None, add=[], new_person=True), held)[0], ProfileChange(new_person=True))

    def test_the_proposal_is_reset_on_every_find_and_a_reply_without_the_field_proposes_nothing(self) -> None:
        client = FakeClient([text_response(dict(answer_json([], "No.", "do_not_know"), profile_change=CHANGE)),
                             text_response(answer_json([], "No.", "do_not_know"))])
        answerer = ClaudeAnswerer(client, FakeErrors)
        answerer.find("Who?", PACK.passages)
        self.assertIsNotNone(answerer.proposal)
        answerer.find("Next?", PACK.passages)
        self.assertIsNone(answerer.proposal)

    def test_the_schema_requires_the_field_as_an_object_or_null_with_the_lists_built_once(self) -> None:
        self.assertIn("profile_change", SCHEMA["required"])
        self.assertFalse(SCHEMA["additionalProperties"])
        obj, null = SCHEMA["properties"]["profile_change"]["anyOf"]
        self.assertEqual(null, {"type": "null"})
        self.assertFalse(obj["additionalProperties"])
        self.assertEqual(obj["required"], ["role", "add", "remove", "new_person"])
        self.assertEqual(obj["properties"]["role"]["anyOf"][0]["enum"], list(claude.PROFILE_ROLES))
        self.assertEqual(obj["properties"]["add"]["items"]["enum"], list(claude.PROFILE_SIGN_OFFS))
        self.assertEqual(obj["properties"]["remove"]["items"]["enum"], list(claude.PROFILE_SIGN_OFFS))

    def test_the_prompt_paragraph_is_fixed_text_and_the_system_block_does_not_vary(self) -> None:
        self.assertIn("Profile. If the worker's message says who they are", SYSTEM_PROMPT)
        self.assertTrue(SYSTEM_PROMPT.index("Depth.") < SYSTEM_PROMPT.index("Profile.") < SYSTEM_PROMPT.index("Citing."))
        blocks = set()
        for change in (None, CHANGE):
            client = proposing(change)
            ClaudeAnswerer(client, FakeErrors, profile=ENGINEER).find("Who?", PACK.passages)
            blocks.add(json.dumps(client.calls[0]["system"], sort_keys=True))
        self.assertEqual(len(blocks), 1)


class Proposing(Scripted):
    """A scripted answerer that proposes: each find gives the next (finding, proposal) and sets `proposal`, and counts calls."""

    def __init__(self, items: list[tuple[Finding, ProfileChange | None]]) -> None:
        """Hold the (finding, proposal) pairs, the last repeated."""
        super().__init__([item[0] for item in items])
        self.proposals = list(items)
        self.proposal: ProfileChange | None = None
        self.calls = 0

    def find(self, question: str, passages: tuple, history: tuple[Turn, ...] = ()) -> Finding:
        """The next finding, with its proposal set."""
        self.calls += 1
        self.proposal = self.proposals[min(self.calls, len(self.proposals)) - 1][1]
        return super().find(question, passages, history)


ASK_BATTERY = Finding((BATTERY,), "Fit it to the controller first.")
BATTERY_STOP = f"Safety rule SR-11\n\n{DEMO_BANNER}\n\nStop. Do not work on battery terminals"
BATTERY_WARN = f"Safety rule SR-11{chat.LOWERED_MARK}"
ELECTRICIAN = ProfileChange("qualified", frozenset({"battery"}))
SWITCH = "Only switch if your supervisor has signed you off for this on this site. Switch to that? yes or no"  # SC-028: the reminder
NEW_PERSON = chat.NEW_PERSON_LINE
NEW = Profile("new", frozenset())
HELLO = "Hello\n"  # SC-028: the first turn acts on no proposal, so a test that proposes opens with a turn that does not
SAID_ELECTRICIAN = "I'm the site electrician, signed off for battery wiring"  # SC-028: a proposal needs words that say it
SAID_TAKEOVER = "My supervisor is taking over"


def takeover(items: list, lines: str, profile: Profile = NEW, speaker: Speaker | None = None) -> tuple[Proposing, str]:
    """The answerer and stdout of a chat on the battery pack with `lines` typed, the answerer proposing `items`; a chat whose
    lines open with HELLO has an opening turn that finds nothing and proposes nothing (SC-028), counted in `calls`."""
    opening = [(Finding(), None)] if lines.startswith(HELLO) else []
    answerer, out = Proposing(opening + items), io.StringIO()
    converse(BATTERY_PACK, True, answerer, io.StringIO(lines), out, io.StringIO(), speaker, profile)
    return answerer, out.getvalue()


class TheYes(unittest.TestCase):
    def test_only_the_six_words_are_a_yes_and_a_no_word_wins(self) -> None:
        for text in ("yes", "Y", "Yeah", "yep!", "correct", "confirm", "yes please"):
            self.assertTrue(read_yes(text), text)
        for text in ("no", "", "maybe", "sure", "ok", "yes, no", "yesterday", "I don't know, yes", "n"):
            self.assertFalse(read_yes(text), text)


class TheTakeover(unittest.TestCase):
    def test_no_proposal_is_one_call_and_no_question(self) -> None:
        answerer, out = takeover([(ASK_BATTERY, None)], "What do I connect first?\nquit\n")
        self.assertEqual(answerer.calls, 1)
        self.assertNotIn(SWITCH, out)
        self.assertNotIn("Profile changed", out)

    def test_sr_11_stops_a_new_worker_then_warns_after_a_yes_and_stops_after_a_no(self) -> None:
        _, out = takeover([(ASK_BATTERY, None)], "What do I connect first?\nquit\n")
        self.assertIn(BATTERY_STOP, out)
        answerer, out = takeover([(ASK_BATTERY, ELECTRICIAN)], f"{HELLO}{SAID_ELECTRICIAN}\nyes\nquit\n")
        self.assertEqual(answerer.calls, 3)
        self.assertIn("You said you are a licensed electrician or engineer, signed off for battery and controller wiring. " + SWITCH, out)
        self.assertLess(out.index("Profile changed: You are a licensed electrician or engineer, signed off for battery and controller wiring."),
                        out.index(BATTERY_WARN))
        self.assertNotIn(BATTERY_STOP, out)  # the held reply was never shown, and the re-run is the warn
        answerer, out = takeover([(ASK_BATTERY, ELECTRICIAN)], f"{HELLO}{SAID_ELECTRICIAN}\nno\nquit\n")
        self.assertEqual(answerer.calls, 2)
        self.assertIn(BATTERY_STOP, out)
        self.assertNotIn("Profile changed", out)

    def test_the_new_profile_holds_for_the_next_turn_and_the_history_keeps_the_said_back_line(self) -> None:
        answerer, out = takeover([(ASK_BATTERY, ELECTRICIAN), (ASK_BATTERY, None)], f"{HELLO}{SAID_ELECTRICIAN}\nyes\nAnd then?\nquit\n")
        self.assertEqual(out.count(BATTERY_WARN), 2)
        self.assertEqual(out.count(SWITCH), 1)
        line = "Profile changed: You are a licensed electrician or engineer, signed off for battery and controller wiring."
        last = answerer.histories[-1]
        self.assertEqual([turn.role for turn in last], ["user", "assistant", "user", "assistant", "assistant"])
        self.assertEqual(last[2].text, SAID_ELECTRICIAN)
        self.assertEqual(last[3].text, line)
        self.assertTrue(last[4].text.startswith("You are signed off for battery"))
        self.assertEqual(answerer.histories[2], answerer.histories[1])  # the re-run is given the history as the first call had it

    def test_less_say_is_applied_at_once_with_no_question_and_the_turn_re_run(self) -> None:
        less = ProfileChange("new", frozenset(), frozenset({"battery"}))
        answerer, out = takeover([(ASK_BATTERY, less)], f"{HELLO}I'm new to solar, not signed off for battery wiring\nquit\n", ENGINEER)
        self.assertEqual(answerer.calls, 3)
        self.assertNotIn(SWITCH, out)
        self.assertIn("Profile changed: You are new to solar, not signed off for any of them.", out)
        self.assertIn(BATTERY_STOP, out)  # a rule the old profile lowered now stops
        self.assertNotIn(BATTERY_WARN, out)

    def test_a_mixed_change_is_more_say_and_is_asked(self) -> None:
        mixed = ProfileChange("qualified", frozenset(), frozenset({"battery"}))
        answerer, out = takeover([(ASK_BATTERY, mixed)], f"{HELLO}I'm the engineer\nno\nquit\n", Profile("crew", frozenset({"battery"})))
        self.assertIn(SWITCH, out)
        self.assertEqual(answerer.calls, 2)

    def test_a_declined_proposal_is_not_asked_again_but_a_different_one_is(self) -> None:
        other = ProfileChange("crew", frozenset())
        answerer, out = takeover([(ASK_BATTERY, ELECTRICIAN), (ASK_BATTERY, ELECTRICIAN), (ASK_BATTERY, other)],
                                 f"{HELLO}{SAID_ELECTRICIAN}\nno\n{SAID_ELECTRICIAN}\nI'm a crew member\nno\nquit\n")
        self.assertEqual(out.count(SWITCH), 2)
        self.assertEqual(out.count(BATTERY_STOP), 3)  # each reply is the door's own stop, so the held check leaves it alone (SC-028)
        self.assertEqual(answerer.calls, 4)

    def test_a_new_person_re_asks_both_questions_and_their_answers_replace_the_profile(self) -> None:
        someone = ProfileChange(new_person=True)
        answerer, out = takeover([(ASK_BATTERY, someone)], f"{HELLO}{SAID_TAKEOVER}\nelectrician\nbattery\nquit\n")
        self.assertEqual(answerer.calls, 3)
        for text in (NEW_PERSON, ROLE_QUESTION, SIGN_OFF_QUESTION, "Profile changed: You are a licensed electrician"):
            self.assertIn(text, out)
        self.assertNotIn(BATTERY_STOP, out)
        self.assertIn(BATTERY_WARN, out)
        self.assertNotIn(SWITCH, out)

    def test_a_new_person_who_asks_nothing_is_invited_to_ask_not_told_i_do_not_know(self) -> None:
        answerer, out = takeover([(Finding(), ProfileChange(new_person=True)), (Finding(), None)],
                                 f"{HELLO}{SAID_TAKEOVER}\nelectrician\nbattery\nquit\n")
        self.assertEqual(answerer.calls, 3)
        self.assertIn("Profile changed: You are a licensed electrician", out)
        self.assertIn(chat.GO_AHEAD, out)
        self.assertNotIn(DO_NOT_KNOW_TEXT, out.split("Profile changed")[1])

    def test_a_new_person_may_end_up_with_less_say_than_before(self) -> None:
        answerer, out = takeover([(ASK_BATTERY, ProfileChange(new_person=True))], f"{HELLO}Someone else is here\nnew\nnone\nquit\n", ENGINEER)
        self.assertIn(BATTERY_STOP, out)
        self.assertEqual(answerer.calls, 3)

    def test_one_question_per_turn_the_re_run_proposal_is_not_asked(self) -> None:
        answerer, out = takeover([(ASK_BATTERY, ELECTRICIAN), (ASK_BATTERY, ProfileChange("crew", frozenset({"meter"})))],
                                 f"{HELLO}{SAID_ELECTRICIAN}\nyes\nquit\n")
        self.assertEqual(out.count(SWITCH), 1)
        self.assertEqual(answerer.calls, 3)

    def test_the_question_and_the_changed_line_are_spoken_with_voice(self) -> None:
        fake = Fake()
        takeover([(ASK_BATTERY, ELECTRICIAN)], f"{HELLO}{SAID_ELECTRICIAN}\nyes\nquit\n", speaker=Speaker(io.StringIO(), fake, "linux", found))
        said = [text for _, text in fake.calls]
        self.assertTrue(any(text.endswith(SWITCH) for text in said))
        self.assertTrue(any(text.startswith("Profile changed: You are a licensed") for text in said))

    def test_a_real_answerer_is_given_the_new_profile_for_the_next_call_and_the_same_system_block(self) -> None:
        client = FakeClient([text_response(answer_json([], "No.", "do_not_know")),
                             text_response(dict(answer_json([], "No.", "do_not_know"), profile_change=CHANGE)),
                             text_response(answer_json([], "No.", "do_not_know"))])
        answerer = ClaudeAnswerer(client, FakeErrors, profile=Profile("new", frozenset()))
        converse(PACK, True, answerer, io.StringIO("Hello\nI'm the electrician, battery signed\nyes\nquit\n"), io.StringIO(), io.StringIO(),
                 profile=Profile("new", frozenset()))
        self.assertEqual(len(client.calls), 3)
        self.assertTrue(client.calls[1]["messages"][-1]["content"].startswith("The worker: new to solar"))
        self.assertTrue(client.calls[2]["messages"][-1]["content"].startswith("The worker: licensed electrician"))
        self.assertEqual(json.dumps(client.calls[1]["system"]), json.dumps(client.calls[2]["system"]))


if __name__ == "__main__":
    unittest.main()
