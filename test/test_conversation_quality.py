"""SC-029: the conversation moves forward and lets the person quit or correct anywhere: "quit" at every question, a repeated answer
asked once more with a note that never reaches the system block or the history, the equipment steps for the panel, and the lowered
warn's precautions shown in full once per rule; scripted answerers, scripted input and a fake client, never a model (TODO 2.16)."""
import io
import json
import unittest

from solarchat.answer.door import DO_NOT_KNOW_TEXT
from solarchat.leaf.contract import DEMO_BANNER, Finding, Profile, Reply, ReplyKind, Turn
from solarchat.model.claude import SYSTEM_PROMPT, ClaudeAnswerer, ProfileChange
from solarchat.project import chat
from solarchat.project.chat import LOWERED_MARK, PROFILE_WRONG, ROLE_QUESTION, SIGN_OFF_QUESTION, converse, spoken
from solarchat.project.offtopic import OFF_TOPIC_TEXT, about_the_work, equipment_words
from solarchat.project.intake import HELP_QUESTION, PANEL_QUESTION, QUESTION
from solarchat.project.reading import asks_instead
from solarchat.project.repeat import RETRY_NOTE, is_repeat
from solarchat.project.shown import LOWERED_REMINDER
from solarchat.project.speech import Speaker
from test.test_claude import GOOD, FakeClient, FakeErrors, answer_json, text_response
from test.test_cli import PACK, STEP, Scripted, talk
from test.test_intake import NO_PACK, VICTRON_NAME, stub_chat
from test.test_profile_chat import ENGINEER, run
from test.test_profile_takeover import ASK_BATTERY, BATTERY_WARN, ELECTRICIAN, HELLO, SAID_ELECTRICIAN, SAID_TAKEOVER, SWITCH, takeover
from test.test_speech import Fake, found

JOIN = Finding((STEP,), "Join plus to plus.")
SEAL = Finding((STEP,), "Now seal the cable.")
WORDS = "You are signed off for battery and controller wiring:"  # the lowering's words, the precautions shown in full


class Noting(Scripted):
    """A scripted answerer with a `note` like the Claude answerer's: it remembers the note each find saw."""

    note = ""

    def __init__(self, findings: list) -> None:
        """Hold the findings and no notes seen."""
        super().__init__(findings)
        self.notes: list[str] = []

    def find(self, question: str, passages: tuple, history: tuple[Turn, ...] = ()) -> Finding:
        """Note the note, then give the next finding."""
        self.notes.append(self.note)
        return super().find(question, passages, history)


class QuitAnywhere(unittest.TestCase):
    def test_quit_at_each_of_the_opening_questions_ends_the_chat_with_nothing_recorded(self) -> None:
        for lines, asked, never in (("quit\n", ROLE_QUESTION, SIGN_OFF_QUESTION), ("xyz\nQUIT\n", chat.ROLE_AGAIN, SIGN_OFF_QUESTION),
                                    ("crew\nquit\n", SIGN_OFF_QUESTION, PROFILE_WRONG)):
            with self.subTest(lines=lines):
                code, out = run(lines)
                self.assertEqual(code, 0)
                self.assertIn(asked, out)
                for text in (never, PROFILE_WRONG, QUESTION, "Working with"):
                    self.assertNotIn(text, out)

    def test_quit_at_the_equipment_question_and_the_panel_and_help_questions_ends_the_chat(self) -> None:
        for lines, last in (("quit\n", QUESTION), ("Victron SmartSolar 75/10\nquit\n", PANEL_QUESTION), ("not sure\nquit\n", HELP_QUESTION)):
            with self.subTest(lines=lines):
                code, out, _ = stub_chat(lines)
                self.assertEqual(code, 0)
                self.assertIn(last, out)
                self.assertNotIn("Working with", out)
                self.assertNotIn(NO_PACK, out)
                self.assertNotIn(DO_NOT_KNOW_TEXT, out)

    def test_quit_at_the_switch_question_ends_the_chat_and_is_never_a_leftover_question(self) -> None:
        answerer, out = takeover([(ASK_BATTERY, ELECTRICIAN)], f"{HELLO}{SAID_ELECTRICIAN}\nquit\nWhat else?\n")
        self.assertIn(SWITCH, out)
        self.assertEqual(answerer.calls, 2)  # the opening turn and the proposing turn; nothing answered after the quit
        self.assertNotIn(chat.KEPT_PROFILE, out)
        self.assertFalse(asks_instead("quit"))

    def test_quit_at_a_new_persons_questions_ends_the_chat(self) -> None:
        answerer, out = takeover([(ASK_BATTERY, ProfileChange(new_person=True))], f"{HELLO}{SAID_TAKEOVER}\nquit\n")
        self.assertIn(ROLE_QUESTION, out)
        self.assertNotIn("Profile changed", out)
        self.assertEqual(answerer.calls, 2)

    def test_the_said_back_line_invites_a_correction_and_a_statement_changes_the_profile_through_the_proposal_path(self) -> None:
        self.assertEqual(PROFILE_WRONG, "If that is wrong, tell me what to change.")
        _, out = run("I'm a crew member\nyes\nquit\n", ("--role", "new", "--signed-off", "none"))
        self.assertIn(PROFILE_WRONG, out)
        self.assertIn("Switch to that? yes or no", out)
        self.assertIn("Profile changed: You are a crew member, not signed off for any of them.", out)

    def test_not_signed_off_removes_a_sign_off_at_once(self) -> None:
        less = ProfileChange(None, frozenset(), frozenset({"battery"}))
        _, out = takeover([(ASK_BATTERY, less)], f"{HELLO}I'm not signed off for batteries\nquit\n", ENGINEER)
        self.assertNotIn("Switch to that?", out)
        self.assertIn("Profile changed: You are a licensed electrician or engineer, not signed off for any of them.", out)


class Repeats(unittest.TestCase):
    def test_a_repeated_answer_is_asked_once_more_with_the_note_and_the_second_reply_is_shown(self) -> None:
        answerer = Noting([JOIN, JOIN, SEAL])
        out, _ = talk(answerer, "How?\nNext?\nquit\n")
        self.assertEqual(answerer.notes, ["", "", RETRY_NOTE])
        self.assertEqual(answerer.note, "")  # set for that call alone
        self.assertEqual(out.count("Join plus to plus."), 1)
        self.assertIn("Now seal the cable.", out)
        last = answerer.histories[-1]
        self.assertEqual([turn.text for turn in last], ["How?", "Join plus to plus."])  # the retry was given the history as the second call had it
        self.assertEqual(answerer.histories[2], answerer.histories[1])

    def test_an_answer_that_differs_is_not_retried(self) -> None:
        answerer = Noting([JOIN, SEAL])
        out, _ = talk(answerer, "How?\nNext?\nquit\n")
        self.assertEqual(answerer.notes, ["", ""])
        self.assertIn("Now seal the cable.", out)

    def test_one_retry_at_most_per_turn_and_a_second_repeat_is_shown(self) -> None:
        answerer = Noting([JOIN])
        out, _ = talk(answerer, "How?\nNext?\nquit\n")
        self.assertEqual(len(answerer.notes), 3)  # the first turn, the second turn, one retry: never a fourth
        self.assertEqual(out.count("Join plus to plus."), 2)

    def test_the_next_turn_may_retry_again(self) -> None:
        answerer = Noting([JOIN, JOIN, SEAL, SEAL, JOIN])
        talk(answerer, "How?\nNext?\nAnd?\nquit\n")
        self.assertEqual(answerer.notes, ["", "", RETRY_NOTE, "", RETRY_NOTE])

    def test_the_comparison_is_on_the_spoken_text_at_85_percent(self) -> None:
        history = (Turn("user", "How?"), Turn("assistant", "Join plus to plus."))
        banner = Reply(ReplyKind.ANSWER, f"{DEMO_BANNER}\n\nJoin plus to plus.\n\nFrom: Step 6 (Pack): Manual, page 15", (STEP,))
        self.assertTrue(is_repeat(banner, spoken(banner), history))  # the banner and the "From:" lines are not compared
        near = Reply(ReplyKind.ANSWER, "Join plus to plus now.", (STEP,))
        self.assertTrue(is_repeat(near, spoken(near), history))
        far = Reply(ReplyKind.ANSWER, "Now seal the cable.", (STEP,))
        self.assertFalse(is_repeat(far, spoken(far), history))
        self.assertFalse(is_repeat(banner, spoken(banner), ()))
        self.assertFalse(is_repeat(banner, spoken(banner), (Turn("user", "How?"),)))

    def test_only_an_answer_is_checked_never_a_stop_a_warn_or_i_do_not_know(self) -> None:
        answerer, _ = takeover([(ASK_BATTERY, None)], "What do I connect first?\nAnd then?\nquit\n", ENGINEER)
        self.assertEqual(answerer.calls, 2)
        answerer = Noting([Finding()])
        talk(answerer, "A?\nB?\nquit\n")
        self.assertEqual(answerer.notes, ["", ""])

    def test_the_real_answerer_gets_the_note_in_that_calls_messages_only(self) -> None:
        reply = text_response(answer_json(["good/label"], "Join plus to plus."))
        client = FakeClient([reply, reply, text_response(answer_json(["good/label"], "Now seal the cable."))])
        answerer = ClaudeAnswerer(client, FakeErrors, profile=Profile("new", frozenset()))
        out = io.StringIO()
        converse(GOOD, False, answerer, io.StringIO("How?\nNext?\nquit\n"), out, io.StringIO())
        self.assertEqual(len(client.calls), 3)
        contents = [call["messages"][-1]["content"] for call in client.calls]
        self.assertEqual([RETRY_NOTE in content for content in contents], [False, False, True])
        self.assertTrue(contents[2].endswith(f"{RETRY_NOTE}\n\nNext?"))
        self.assertEqual(len({json.dumps(call["system"], sort_keys=True) for call in client.calls}), 1)  # the cached block never varies
        self.assertNotIn(RETRY_NOTE, json.dumps([call["system"] for call in client.calls]))
        self.assertFalse(any(RETRY_NOTE in message["content"] for message in client.calls[2]["messages"][:-1]))  # nor the kept history
        self.assertEqual(answerer.note, "")

    def test_the_prompt_keeps_the_turn_with_the_worker_and_asks_for_teach_back_at_checkpoints_and_the_block_never_varies(self) -> None:
        for words in ("End every reply with one clear thing for the worker to do or answer, so the next turn is theirs.",
                      "Before a step that could hurt someone or damage equipment, after a step that changes the wiring, or when you cannot "
                      "tell whether the last step was done, ask the worker to say in their own words what they are about to do or have just "
                      "done, and check it against the passages before going on; not on every turn."):
            self.assertIn(words, SYSTEM_PROMPT)
            self.assertLess(SYSTEM_PROMPT.index(words), SYSTEM_PROMPT.index("Depth."))  # in the Pace paragraph
        reply = text_response(answer_json(["good/label"], "Join plus to plus."))
        client = FakeClient([reply, text_response(answer_json(["good/label"], "Now seal the cable.")), reply])
        converse(GOOD, False, ClaudeAnswerer(client, FakeErrors), io.StringIO("How?\nNext?\nAnd?\nquit\n"), io.StringIO(), io.StringIO())
        self.assertGreaterEqual(len(client.calls), 3)
        self.assertEqual(len({json.dumps(call["system"], sort_keys=True) for call in client.calls}), 1)

    def test_the_prompt_says_move_on_ask_once_and_walk_through(self) -> None:
        for words in ("Never repeat your previous step.", "ask for it once", "never ask for it again", "ask your question again, once",
                      "Ask one question at a time.", "'it sounds like'", "no more than six short lines"):
            self.assertIn(words, SYSTEM_PROMPT)
        self.assertTrue(SYSTEM_PROMPT.index("Never repeat") < SYSTEM_PROMPT.index("Depth.") < SYSTEM_PROMPT.index("six short lines")
                        < SYSTEM_PROMPT.index("Profile."))


class TheDoNotKnowWords(unittest.TestCase):
    def test_they_are_plain_and_name_where_to_go_next(self) -> None:
        self.assertEqual(DO_NOT_KNOW_TEXT, "I don't know this one: it isn't in the manuals I have for this equipment. Don't guess. "
                         "If you are not sure what to do, stop and ask your site supervisor or engineer before you go on.")
        out, _ = talk(Scripted([Finding()]), "What is the price?\nquit\n")
        self.assertIn(DO_NOT_KNOW_TEXT, out)
        self.assertNotIn("packs switched on", out)
        self.assertIn("Don't guess", out)  # it warns: SR-14's own words, restated (SC-029)


class Flagging(Scripted):
    """A scripted answerer that says whether the model flagged the question off topic: `off_topic` is read by the chat as the Claude answerer's is."""

    def __init__(self, flag: bool) -> None:
        """Hold the flag and give "I do not know" to everything."""
        super().__init__([Finding()])
        self.off_topic = flag


class TheOffTopicFlag(unittest.TestCase):
    def test_weather_flagged_off_topic_gets_the_plain_line_with_the_banner_and_no_warning(self) -> None:
        out, _ = talk(Flagging(True), "What is the weather like?\nquit\n")
        self.assertIn(f"{DEMO_BANNER}\n\n{OFF_TOPIC_TEXT}", out)
        self.assertNotIn(DO_NOT_KNOW_TEXT, out)
        self.assertNotIn("Don't guess", out)

    def test_a_work_question_flagged_off_topic_keeps_the_warning_because_the_word_check_wins(self) -> None:
        for question in ("how do I wire the inverter?", "Which Victron setting?", "What does the light mean?", "Is the battery hot?"):
            with self.subTest(question=question):
                out, _ = talk(Flagging(True), f"{question}\nquit\n")
                self.assertIn(DO_NOT_KNOW_TEXT, out)
                self.assertNotIn(OFF_TOPIC_TEXT, out)

    def test_not_flagged_or_a_stub_answerer_keeps_the_warning(self) -> None:
        out, _ = talk(Flagging(False), "What is the weather like?\nquit\n")
        self.assertIn(DO_NOT_KNOW_TEXT, out)
        _, out, _ = stub_chat("What is the weather like?\nquit\n", ("--equipment", "none"))
        self.assertIn(DO_NOT_KNOW_TEXT, out)
        self.assertNotIn(OFF_TOPIC_TEXT, out)

    def test_only_an_i_do_not_know_is_replaced(self) -> None:
        out, _ = talk(type("Both", (Scripted,), {"off_topic": True})([JOIN]), "What is the weather like?\nquit\n")
        self.assertIn("Join plus to plus.", out)
        self.assertNotIn(OFF_TOPIC_TEXT, out)

    def test_the_word_check_reads_rules_equipment_names_and_work_words(self) -> None:
        equipment = PACK.equipment
        for text in ("my smartsolar is blank", "an EcoFlow question", "can I use a bigger fuse", "I got a shock"):
            self.assertTrue(about_the_work(text, equipment, chat.load_rules()), text)
        for text in ("What is the weather like?", "who won the match", "how much does it cost"):
            self.assertFalse(about_the_work(text, equipment, chat.load_rules()), text)
        self.assertNotIn("any", equipment_words(equipment))
        self.assertNotIn("the", equipment_words(equipment))

    def test_the_real_answerer_keeps_the_last_flag_resets_it_and_the_system_block_never_varies(self) -> None:
        flagged = text_response(dict(answer_json([], "No.", "do_not_know"), off_topic=True))
        plain = text_response(answer_json([], "No.", "do_not_know"))
        client = FakeClient([flagged, plain, flagged])
        answerer = ClaudeAnswerer(client, FakeErrors)
        answerer.find("What is the weather like?", GOOD.passages)
        self.assertTrue(answerer.off_topic)
        answerer.find("Which label?", GOOD.passages)
        self.assertFalse(answerer.off_topic)  # reset, and absent from the reply
        out = io.StringIO()
        converse(GOOD, False, ClaudeAnswerer(FakeClient([flagged]), FakeErrors), io.StringIO("What is the weather like?\nquit\n"), out, io.StringIO())
        self.assertIn(OFF_TOPIC_TEXT, out.getvalue())
        self.assertEqual(len({json.dumps(call["system"], sort_keys=True) for call in client.calls}), 1)
        self.assertIn("off_topic", SYSTEM_PROMPT)
        self.assertIn("When in doubt, false.", SYSTEM_PROMPT)


class TheEquipmentSteps(unittest.TestCase):
    def test_a_controller_with_no_panel_asks_for_the_panel_once(self) -> None:
        _, out, _ = stub_chat("Victron SmartSolar 75/10\nnot sure\nquit\n")
        self.assertEqual(out.count(PANEL_QUESTION), 1)
        self.assertIn(f"Working with: {VICTRON_NAME}. If that is wrong, say so at any point.", out)
        self.assertLess(out.index(PANEL_QUESTION), out.index("Working with"))

    def test_a_panel_answer_is_read_as_the_first_answer_is(self) -> None:
        _, out, _ = stub_chat("Victron SmartSolar 75/10\na crystalline panel\nquit\n")
        self.assertIn(f"Working with: {VICTRON_NAME}; Crystalline silicon panels with MC4 leads (the general steps).", out)

    def test_a_panel_named_with_the_controller_or_no_controller_asks_nothing_more(self) -> None:
        for lines in ("Victron SmartSolar and a crystalline panel\nquit\n", "EcoFlow R600\nquit\n", "a Solarex 300\nquit\n"):
            with self.subTest(lines=lines):
                self.assertNotIn(PANEL_QUESTION, stub_chat(lines)[1])

    def test_not_sure_gets_the_helping_question_then_the_no_match_line(self) -> None:
        _, out, _ = stub_chat("not sure\nnot sure\nquit\n")
        self.assertEqual(out.count(HELP_QUESTION), 1)
        self.assertLess(out.index(HELP_QUESTION), out.index(NO_PACK))
        self.assertNotIn(PANEL_QUESTION, out)

    def test_a_name_found_by_the_helping_question_is_a_match_and_asks_for_the_panel(self) -> None:
        _, out, _ = stub_chat("don't know\nVictron\nnot sure\nquit\n")
        self.assertLess(out.index(HELP_QUESTION), out.index(PANEL_QUESTION))
        self.assertIn(f"Working with: {VICTRON_NAME}.", out)

    def test_a_wrong_name_is_the_no_match_line_at_once(self) -> None:
        _, out, _ = stub_chat("a Solarex 300\nquit\n")
        self.assertNotIn(HELP_QUESTION, out)
        self.assertIn(NO_PACK, out)

    def test_the_equipment_option_skips_all_of_it(self) -> None:
        _, out, _ = stub_chat("quit\n", ("--equipment", "victron-smartsolar-mppt"))
        self.assertNotIn(PANEL_QUESTION, out)


class TheLoweredWarn(unittest.TestCase):
    def test_the_first_label_says_signed_off_and_never_lowered(self) -> None:
        self.assertEqual(LOWERED_MARK, " (you are signed off for this work)")
        _, out = takeover([(ASK_BATTERY, None)], "What do I connect first?\nquit\n", ENGINEER)
        self.assertIn("Safety rule SR-11 (you are signed off for this work)", out)
        self.assertNotIn("lowered", out)

    def test_the_precautions_are_in_full_once_then_the_short_reminder_and_a_takeover_shows_them_again(self) -> None:
        lines = f"What do I connect first?\nAnd then?\n{SAID_TAKEOVER}\nelectrician\nbattery\nquit\n"
        _, out = takeover([(ASK_BATTERY, None), (ASK_BATTERY, None), (ASK_BATTERY, ProfileChange(new_person=True)), (ASK_BATTERY, None)],
                          lines, ENGINEER)
        self.assertEqual(out.count(BATTERY_WARN), 3)
        self.assertEqual(out.count(WORDS), 2)  # the first turn, and the turn after the takeover
        self.assertEqual(out.count(LOWERED_REMINDER), 1)  # the second turn
        second = out.split(BATTERY_WARN)[2]
        self.assertTrue(second.startswith(f"\n\n{DEMO_BANNER}\n\n{LOWERED_REMINDER}\n\nFit it to the controller first."))
        self.assertLess(out.index(WORDS), out.index(LOWERED_REMINDER))

    def test_a_confirmed_change_shows_them_in_full_again(self) -> None:
        change = ProfileChange("qualified", frozenset({"meter"}))
        lines = "What do I connect first?\nAnd then?\nI'm the site electrician, signed off for meter tests\nyes\nquit\n"
        _, out = takeover([(ASK_BATTERY, None), (ASK_BATTERY, None), (ASK_BATTERY, change), (ASK_BATTERY, None)], lines, ENGINEER)
        self.assertEqual(out.count(WORDS), 2)
        self.assertEqual(out.count(LOWERED_REMINDER), 1)

    def test_a_stop_for_another_profile_is_not_shortened_and_the_reminder_is_spoken_with_voice(self) -> None:
        fake = Fake()
        takeover([(ASK_BATTERY, None)], "What do I connect first?\nAnd then?\nquit\n", ENGINEER, Speaker(io.StringIO(), fake, "linux", found))
        said = [text for _, text in fake.calls]
        self.assertTrue(said[0].startswith(f"Safety rule SR-11{LOWERED_MARK}\n\n{WORDS}"))
        self.assertTrue(said[1].startswith(f"Safety rule SR-11{LOWERED_MARK}\n\n{LOWERED_REMINDER}"))


if __name__ == "__main__":
    unittest.main()
