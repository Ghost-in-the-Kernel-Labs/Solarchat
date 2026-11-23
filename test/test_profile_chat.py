"""SC-020, slice 2: the two questions the chat asks first and how they are read, --role and --signed-off, the profile line the
answerer is sent (never in the system block), and the lowered warn's first line; a fake client, scripted input, a fake
speech runner; never a model and never a real engine (TODO 1.10)."""
import contextlib
import dataclasses
import io
import json
import unittest
from unittest import mock

from solarchat.cli.main import MENU, main
from solarchat.leaf.contract import DEMO_BANNER, Finding, Passage, PassageRef, Profile, Reply, ReplyKind, Turn
from solarchat.model import claude
from solarchat.model.claude import SYSTEM_PROMPT, ClaudeAnswerer, profile_line
from solarchat.project import chat
from solarchat.project.chat import (PROFILE_WRONG, ROLE_AGAIN, ROLE_QUESTION, SIGN_OFF_QUESTION, ask_profile, converse, parse_signed_off,
                                    profile_said_back,
                                    read_role, read_signed_off, render)
from solarchat.project.speech import Speaker
from test.support import ROOT
from test.test_claude import FakeClient, FakeErrors, answer_json, text_response
from test.test_cli import PACK, Scripted
from test.test_speech import Fake, found

SEED = ROOT / "packs" / "seed-mc4-leads"
BATTERY = PassageRef("seed-mc4-leads", "battery")
BATTERY_PACK = dataclasses.replace(PACK, passages=(Passage(BATTERY, "Fit the battery terminal to the controller first.", "Battery first"),),
                                   citations={"battery": PACK.citations["step-06"]})
ENGINEER = Profile("qualified", frozenset({"battery"}))


def run(lines: str, options: tuple[str, ...] = (), voice: Fake | None = None) -> tuple[int, str]:
    """The exit code and stdout of the stub chat on the seed pack with `lines` typed and `options` added."""
    out, err = io.StringIO(), io.StringIO()
    argv = ["--pack", str(SEED), "--demo", "--answerer", "stub", *options] + (["--voice"] if voice else [])
    speaker = mock.patch("solarchat.project.chat.Speaker", lambda stderr: Speaker(stderr, voice, "linux", found)) if voice else contextlib.nullcontext()
    with speaker, contextlib.redirect_stderr(err):
        code = main(argv, io.StringIO(lines), out, err)
    return code, out.getvalue()


class TheReading(unittest.TestCase):
    def test_roles_are_read_by_words_and_the_least_say_wins(self) -> None:
        self.assertEqual(read_role("I'm the site engineer"), "qualified")
        self.assertEqual(read_role("licensed Electrician"), "qualified")
        self.assertEqual(read_role("crew member"), "crew")
        self.assertEqual(read_role("I am new to solar"), "new")
        self.assertEqual(read_role("a new engineer"), "new")
        self.assertIsNone(read_role("the boss"))
        self.assertIsNone(read_role("now"))

    def test_typos_and_run_together_words_are_read(self) -> None:
        self.assertEqual(read_role("crewmember"), "crew")
        for text in ("cre member", "cew member", "crew member"):  # Ghost's run on Windows, 2026-11-23: "member" says crew
            self.assertEqual(read_role(text), "crew", text)
        self.assertEqual(read_role("crewman"), "crew")
        self.assertEqual(read_role("licenssed eletrician"), "qualified")
        self.assertEqual(read_role("eletrician"), "qualified")
        self.assertEqual(read_role("I'm new"), "new")
        self.assertEqual(read_role("renewable engineer"), "qualified")
        self.assertIsNone(read_role("few"))
        self.assertEqual(read_signed_off("baterry"), frozenset({"battery"}))

    def test_all_every_and_not_in_the_sign_off_answer(self) -> None:
        every = frozenset({"meter", "connector", "battery", "height"})
        self.assertEqual(read_signed_off("all of these"), every)
        self.assertEqual(read_signed_off("everything"), every)
        self.assertEqual(read_signed_off("all except height"), frozenset())
        self.assertEqual(read_signed_off("all but the roof"), frozenset())
        self.assertEqual(read_signed_off("not battery"), frozenset())
        self.assertEqual(read_signed_off("none of these"), frozenset())
        self.assertEqual(read_signed_off("battery and meter"), frozenset({"meter", "battery"}))
        self.assertIsNone(read_role(""))

    def test_sign_offs_are_read_by_words_and_none_wins(self) -> None:
        self.assertEqual(read_signed_off("battery and meter"), frozenset({"battery", "meter"}))
        self.assertEqual(read_signed_off("the controller, connectors and the roof"), frozenset({"battery", "connector", "height"}))
        self.assertEqual(read_signed_off("height"), frozenset({"height"}))
        self.assertEqual(read_signed_off("none"), frozenset())
        self.assertEqual(read_signed_off("meter, none of the others"), frozenset())
        self.assertEqual(read_signed_off("whatever"), frozenset())

    def test_the_command_line_list_is_exact_and_an_unknown_name_is_refused(self) -> None:
        self.assertEqual(parse_signed_off("meter,battery"), frozenset({"meter", "battery"}))
        self.assertEqual(parse_signed_off("none"), frozenset())
        with self.assertRaisesRegex(ValueError, "roof is not one of"):
            parse_signed_off("meter,roof")

    def test_the_profile_is_said_back_in_one_line(self) -> None:
        self.assertEqual(profile_said_back(ENGINEER),
                         "You are a licensed electrician or engineer, signed off for battery and controller wiring.")
        self.assertEqual(profile_said_back(Profile("new", frozenset())), "You are new to solar, not signed off for any of them.")
        self.assertEqual(profile_said_back(Profile("crew", frozenset({"meter", "height"}))),
                         "You are a crew member, signed off for meter tests, work at height with fall protection.")


class TheWords(unittest.TestCase):
    def test_the_chat_and_the_answerer_use_the_same_words_for_roles_and_sign_offs(self) -> None:
        self.assertEqual(chat.ROLE_WORDS, claude.ROLE_WORDS)
        self.assertEqual(chat.SIGN_OFF_WORDS, claude.SIGN_OFF_WORDS)


class TheQuestions(unittest.TestCase):
    def test_both_are_asked_after_the_banner_and_before_the_first_prompt_and_the_profile_is_said_back(self) -> None:
        code, out = run("I'm the site engineer\nbattery and meter\nquit\n")
        self.assertEqual(code, 0)
        self.assertTrue(out.startswith(DEMO_BANNER))
        positions = [out.index(text) for text in ("Ask a question", ROLE_QUESTION, SIGN_OFF_QUESTION, "You are a licensed")]
        self.assertEqual(positions, sorted(positions))
        self.assertIn(f"You are a licensed electrician or engineer, signed off for meter tests, battery and controller wiring.\n{PROFILE_WRONG}\n\n> ", out)
        self.assertNotIn(ROLE_AGAIN, out)

    def test_ghosts_own_answers_give_the_profile_he_meant(self) -> None:
        every = frozenset({"meter", "connector", "battery", "height"})
        for text, role in (("crewmember\nall of these\n", "crew"), ("xyz\nlicenssed eletrician\nall of these\n", "qualified")):
            with self.subTest(text=text):
                self.assertEqual(ask_profile(io.StringIO(text), io.StringIO()), Profile(role, every))

    def test_a_role_answer_naming_none_is_asked_once_more(self) -> None:
        _, out = run("hello\ncrew\nnone\nquit\n")
        self.assertEqual(out.count(ROLE_AGAIN), 1)
        self.assertIn("You are a crew member, not signed off for any of them.", out)

    def test_a_second_miss_is_new_to_solar_and_the_third_line_is_the_sign_off_answer(self) -> None:
        _, out = run("hello\nthe boss\nbattery\nquit\n")
        self.assertIn("You are new to solar, signed off for battery and controller wiring.", out)

    def test_none_and_an_unknown_answer_are_no_sign_offs(self) -> None:
        for answer in ("none", "no idea"):
            with self.subTest(answer=answer):
                self.assertIn("not signed off for any of them", run(f"engineer\n{answer}\nquit\n")[1])

    def test_the_end_of_input_ends_the_chat_after_the_questions_with_a_new_profile(self) -> None:
        code, out = run("")
        self.assertEqual(code, 0)
        self.assertIn("You are new to solar, not signed off for any of them.", out)

    def test_the_questions_and_the_line_said_back_are_spoken_with_voice(self) -> None:
        fake = Fake()
        run("engineer\nbattery\nquit\n", voice=fake)
        said = [text for _, text in fake.calls]
        self.assertEqual(said, [DEMO_BANNER, ROLE_QUESTION, SIGN_OFF_QUESTION,
                                "You are a licensed electrician or engineer, signed off for battery and controller wiring.",
                                PROFILE_WRONG])


class TheOptions(unittest.TestCase):
    def test_both_options_skip_both_questions(self) -> None:
        code, out = run("quit\n", ("--role", "qualified", "--signed-off", "battery"))
        self.assertEqual(code, 0)
        self.assertNotIn(ROLE_QUESTION, out)
        self.assertNotIn(SIGN_OFF_QUESTION, out)
        self.assertIn("You are a licensed electrician or engineer, signed off for battery and controller wiring.", out)

    def test_one_option_skips_only_its_own_question(self) -> None:
        _, out = run("meter\nquit\n", ("--role", "crew"))
        self.assertNotIn(ROLE_QUESTION, out)
        self.assertIn("You are a crew member, signed off for meter tests.", out)
        _, out = run("engineer\nquit\n", ("--signed-off", "none"))
        self.assertNotIn(SIGN_OFF_QUESTION, out)
        self.assertIn(ROLE_QUESTION, out)
        self.assertIn("You are a licensed electrician or engineer, not signed off", out)

    def test_an_unknown_role_or_sign_off_exits_2_and_the_menu_names_both_options(self) -> None:
        self.assertEqual(run("", ("--role", "boss"))[0], 2)
        self.assertEqual(run("", ("--signed-off", "meter,roof"))[0], 2)
        self.assertIn("--role new|crew|qualified", MENU)
        self.assertIn("--signed-off", MENU)

    def test_demo_alone_still_starts_the_chat_and_asks_the_questions(self) -> None:
        out, err = io.StringIO(), io.StringIO()
        with mock.patch("solarchat.project.chat.Speaker", lambda stderr: Speaker(stderr, Fake(), "linux", found)):
            code = main(["--demo", "--answerer", "stub"], io.StringIO("engineer\nnone\nWhere?\nquit\n"), out, err)
        self.assertEqual(code, 0)
        self.assertIn(ROLE_QUESTION, out.getvalue())
        self.assertIn("I do not know", out.getvalue())


class TheAnswerer(unittest.TestCase):
    def client_for(self, profile: Profile | None) -> FakeClient:
        """The fake client after one find with `profile` on the good pack."""
        client = FakeClient([text_response(answer_json([], "No.", "do_not_know"))])
        ClaudeAnswerer(client, FakeErrors, profile=profile).find("Which label?", PACK.passages, (Turn("user", "Hi"),))
        return client

    def test_the_profile_line_begins_the_last_message_and_is_not_in_the_system_block(self) -> None:
        call = self.client_for(ENGINEER).calls[0]
        self.assertEqual(call["messages"][-1]["content"],
                         "The worker: licensed electrician or engineer; signed off for: battery and controller wiring.\n\nWhich label?")
        self.assertEqual(call["messages"][0], {"role": "user", "content": "Hi"})
        self.assertNotIn("The worker:", json.dumps(call["system"]))

    def test_the_system_block_is_the_same_bytes_for_two_profiles_and_for_none(self) -> None:
        blocks = {json.dumps(self.client_for(profile).calls[0]["system"], sort_keys=True)
                  for profile in (None, Profile("new", frozenset()), ENGINEER, Profile("crew", frozenset({"meter", "height"})))}
        self.assertEqual(len(blocks), 1)

    def test_no_profile_adds_nothing_and_none_is_said_as_none(self) -> None:
        self.assertEqual(self.client_for(None).calls[0]["messages"][-1]["content"], "Which label?")
        self.assertEqual(profile_line(Profile("new", frozenset())), "The worker: new to solar; signed off for: none.")

    def test_the_prompt_has_the_depth_paragraph_after_pace(self) -> None:
        pace, depth = SYSTEM_PROMPT.index("Pace."), SYSTEM_PROMPT.index("Depth.")
        self.assertTrue(pace < depth < SYSTEM_PROMPT.index("Citing."))
        self.assertIn("which way round it goes", SYSTEM_PROMPT)

    def test_the_chat_gives_the_fake_client_the_profile_it_asked_for(self) -> None:
        client = FakeClient([text_response(answer_json([], "No.", "do_not_know"))])
        out, err = io.StringIO(), io.StringIO()
        with mock.patch("solarchat.model.claude.default_client", lambda: client), contextlib.redirect_stderr(err), \
                mock.patch.dict("os.environ", {"ANTHROPIC_API_KEY": "set-for-the-test"}):
            code = main(["--pack", str(SEED), "--demo", "--no-voice"], io.StringIO("I'm the site engineer\nbattery\nWhat now?\nquit\n"), out, err)
        self.assertEqual(code, 0)
        self.assertEqual(client.calls[0]["messages"][-1]["content"],
                         "The worker: licensed electrician or engineer; signed off for: battery and controller wiring.\n\nWhat now?")


class TheLoweredWarn(unittest.TestCase):
    def talk(self, profile: Profile) -> str:
        """The chat's stdout when a battery passage is cited, for this profile."""
        out = io.StringIO()
        converse(BATTERY_PACK, True, Scripted([Finding((BATTERY,), "Fit it to the controller first.")]),
                 io.StringIO("What do I connect first?\nquit\n"), out, io.StringIO(), profile=profile)
        return out.getvalue()

    def test_a_battery_sign_off_lowers_sr_11_and_the_first_line_says_so(self) -> None:
        shown = self.talk(ENGINEER)
        self.assertIn(f"Safety rule SR-11, lowered for your sign-off\n\n{DEMO_BANNER}\n\nYou are signed off for battery and controller wiring:", shown)
        self.assertIn("Fit it to the controller first.", shown)
        self.assertEqual(shown.count("You are signed off for battery and controller wiring:"), 1)

    def test_without_the_sign_off_it_is_the_stop_with_no_such_line(self) -> None:
        for profile in (Profile("new", frozenset()), Profile("qualified", frozenset({"meter"}))):
            shown = self.talk(profile)
            with self.subTest(profile=profile):
                self.assertIn(f"Safety rule SR-11\n\n{DEMO_BANNER}\n\nStop. Do not work on battery terminals", shown)
                self.assertNotIn("lowered", shown)

    def test_render_adds_the_line_only_to_a_warn_the_profile_lowered(self) -> None:
        warn = Reply(ReplyKind.WARN, "Cover the panel first.", (BATTERY,), "SR-03")
        self.assertEqual(render(warn, ENGINEER), render(warn))


if __name__ == "__main__":
    unittest.main()
