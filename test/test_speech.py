"""Speech out (TODO 2.7): --voice sends each reply's words to the system's speech engine on its standard input, with a fake
runner and never a real engine; the command line holds no reply text, the citations and the banner are not spoken
after the start, and a missing or failing engine leaves the chat working in text (HAD-06, F-08)."""
import base64
import contextlib
import io
import os
import subprocess
import tempfile
import unittest
from collections.abc import Callable
from unittest import mock

from solarchat.cli.main import MENU, main
from solarchat.leaf.contract import DEMO_BANNER, Finding, Reply, ReplyKind
from solarchat.project.chat import DEMO_PACK, converse, render, spoken_aloud
from solarchat.safety.rules import load_rules
from solarchat.project.speech import NO_ENGINE, WINDOWS_ENCODED, WINDOWS_SCRIPT, Speaker, engine_command
from test.support import ROOT
from test.test_cli import PACK, SKIP, STEP, Scripted

SEED = ROOT / "packs" / "seed-mc4-leads"


_FOLDER = tempfile.TemporaryDirectory()


def setUpModule() -> None:
    """No chosen voice and no stored key anywhere but a temporary folder, so a developer's own choice never changes a result."""
    os.environ["SOLARCHAT_CONFIG_DIR"] = _FOLDER.name


def tearDownModule() -> None:
    """Put the environment back and remove the folder."""
    os.environ.pop("SOLARCHAT_CONFIG_DIR", None)
    _FOLDER.cleanup()


class Fake:
    """A runner that records each call's arguments and input and gives the scripted exit code (or raises)."""

    def __init__(self, code: int = 0, error: Exception | None = None) -> None:
        """Hold what to give back: Fake(1) fails with exit code 1."""
        self.calls: list[tuple[list[str], str]] = []
        self.envs: list[dict[str, str] | None] = []
        self.code, self.error = code, error

    def __call__(self, command: list[str], *, input: str, text: bool, encoding: str, check: bool, timeout: int,
                 shell: bool = False, env: dict[str, str] | None = None) -> subprocess.CompletedProcess:
        """Record the call; refuse a shell, as subprocess is held to (subprocess.run's keywords, named)."""
        assert not shell and input is not None and check is False and text and encoding == "utf-8" and timeout > 0
        self.calls.append((command, str(input)))
        self.envs.append(env)
        if self.error:
            raise self.error
        return subprocess.CompletedProcess(command, self.code)


def found(name: str) -> str:
    """A which that finds every engine at /bin/<name>: found("say") gives "/bin/say"."""
    return f"/bin/{name}"


def voiced(lines: str, finding: Finding, runner: Fake, platform: str = "linux", which: Callable[[str], str | None] = found, demo: bool = True) -> tuple[str, str]:
    """The stdout and stderr of a conversation spoken through `runner`."""
    out, err = io.StringIO(), io.StringIO()
    converse(PACK, demo, Scripted([finding]), io.StringIO(lines), out, err, Speaker(err, runner, platform, which))
    return out.getvalue(), err.getvalue()


class TheEngine(unittest.TestCase):
    def test_each_platform_has_its_own_engine_with_no_reply_text_in_the_arguments(self) -> None:
        self.assertEqual(engine_command("darwin", found), ["/bin/say", "-f", "-"])
        self.assertEqual(engine_command("linux", found), ["/bin/espeak", "--stdin"])
        windows = engine_command("win32", found)
        self.assertEqual(windows[:4], ["/bin/powershell", "-NoProfile", "-NonInteractive", "-EncodedCommand"])
        self.assertEqual(len(windows), 5)

    def test_the_windows_script_is_a_constant_that_reads_its_own_input(self) -> None:
        self.assertEqual(base64.b64decode(WINDOWS_ENCODED).decode("utf-16-le"), WINDOWS_SCRIPT)
        self.assertIn("[Console]::In.ReadToEnd()", WINDOWS_SCRIPT)
        self.assertIn("System.Speech.Synthesis.SpeechSynthesizer", WINDOWS_SCRIPT)

    def test_no_engine_is_none(self) -> None:
        for platform in ("win32", "darwin", "linux"):
            self.assertIsNone(engine_command(platform, lambda name: None))


class TheSpokenReply(unittest.TestCase):
    def test_the_arguments_hold_no_reply_text_and_the_input_holds_it_without_the_citations(self) -> None:
        fake = Fake()
        text = "Push the leads together; $(Remove-Item x) is only words."
        out, _ = voiced("How do I join them?\nquit\n", Finding((STEP,), text), fake)
        self.assertIn("From: ", out)
        speech = [call for call in fake.calls if call[1] == text]
        self.assertEqual(len(speech), 1)
        command, said = speech[0]
        self.assertEqual(command, ["/bin/espeak", "--stdin"])
        self.assertNotIn("From:", said)
        self.assertFalse(any("Push the leads" in part for call in fake.calls for part in call[0]))

    def test_on_windows_the_reply_is_neither_in_the_command_line_nor_in_the_script(self) -> None:
        fake = Fake()
        voiced("How?\nquit\n", Finding((STEP,), "Join plus to plus."), fake, "win32")
        command, said = fake.calls[-1]
        self.assertEqual(said, "Join plus to plus.")
        self.assertNotIn("Join plus", " ".join(command))
        self.assertNotIn("Join plus", WINDOWS_SCRIPT)

    def test_the_banner_stays_on_screen_for_every_reply_and_is_spoken_once_at_the_start(self) -> None:
        fake = Fake()
        out, err = io.StringIO(), io.StringIO()
        with mock.patch("solarchat.project.chat.Speaker", lambda stderr: Speaker(stderr, fake, "linux", found)):
            code = main(["--pack", str(SEED), "--demo", "--answerer", "stub", "--voice", *SKIP], io.StringIO("A?\nB?\nquit\n"), out, err)
        self.assertEqual(code, 0)
        self.assertEqual(out.getvalue().count(DEMO_BANNER), 3)
        self.assertEqual(len(fake.calls), 5)  # the banner, the profile said back and how to correct it, and the two replies
        self.assertEqual(fake.calls[0][1], DEMO_BANNER)
        self.assertEqual(fake.calls[1][1], "You are new to solar, not signed off for any of them.")
        self.assertEqual(fake.calls[2][1], "If that is wrong, type quit and start again.")
        self.assertEqual(sum(DEMO_BANNER in said for _, said in fake.calls), 1)

    def test_a_warn_speaks_the_rules_words_and_an_answer_does_not(self) -> None:
        warn = Reply(ReplyKind.WARN, "Cover the panel first.\n\nFrom: Step 6", (STEP,), "SR-03")
        self.assertTrue(spoken_aloud(warn).startswith("Safety rule SR-03: "))
        self.assertTrue(spoken_aloud(warn).endswith("Cover the panel first."))
        self.assertNotIn("From:", spoken_aloud(warn))
        self.assertEqual(spoken_aloud(Reply(ReplyKind.ANSWER, f"{DEMO_BANNER}\n\nJoin.", (STEP,))), "Join.")

    def test_without_voice_nothing_is_spoken(self) -> None:
        fake = Fake()
        out, err = io.StringIO(), io.StringIO()
        converse(PACK, True, Scripted([Finding((STEP,), "Join.")]), io.StringIO("A?\nquit\n"), out, err)
        self.assertEqual(fake.calls, [])


class TheMissingEngine(unittest.TestCase):
    def test_no_engine_gives_one_line_on_stderr_and_the_chat_goes_on_in_text(self) -> None:
        fake = Fake()
        out, err = voiced("A?\nB?\nquit\n", Finding((STEP,), "Join."), fake, which=lambda name: None)
        self.assertEqual(err, NO_ENGINE + "\n")
        self.assertEqual(out.count("Join."), 2)
        self.assertEqual(fake.calls, [])

    def test_through_the_command_a_missing_engine_leaves_the_chat_working(self) -> None:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stderr(err), mock.patch("shutil.which", lambda name: None):
            code = main(["--pack", str(SEED), "--demo", "--answerer", "stub", "--voice", *SKIP], io.StringIO("A?\nquit\n"), out, err)
        self.assertEqual(code, 0)
        self.assertEqual(err.getvalue().count(NO_ENGINE), 1)
        self.assertIn("I do not know", out.getvalue())

    def test_an_engine_that_fails_is_one_line_then_quiet_and_the_chat_goes_on(self) -> None:
        for fake in (Fake(1), Fake(error=OSError("gone")), Fake(error=subprocess.TimeoutExpired("x", 1))):
            out, err = voiced("A?\nB?\nquit\n", Finding((STEP,), "Join."), fake)
            self.assertEqual(len(fake.calls), 1)  # the first attempt, then no more
            self.assertEqual(err.count("the chat goes on in text"), 1)
            self.assertEqual(out.count("Join."), 2)


class TheOption(unittest.TestCase):

    def test_voice_is_in_the_menu(self) -> None:
        self.assertIn("--voice", MENU)


class TheRuleWordsOnce(unittest.TestCase):
    def door_reply(self, kind: ReplyKind, rule_id: str, rest: str) -> Reply:
        """A reply as the door builds it since 1.9: the rule's words inside the text, then `rest`."""
        words = {rule.rule_id: rule for rule in load_rules()}[rule_id].words_shown
        return Reply(kind, f"{words}\n\n{rest}\n\nFrom: Step 6", () if kind is ReplyKind.STOP else (STEP,), rule_id)

    def check_once(self, reply: Reply, rule_id: str) -> None:
        """The rule's words once in the display and once in the speech: check_once(warn, "SR-03") passes when they are."""
        words = {rule.rule_id: rule for rule in load_rules()}[rule_id].words_shown
        self.assertEqual(render(reply).count(words), 1)
        self.assertTrue(render(reply).startswith(f"Safety rule {rule_id}\n\n"))
        self.assertEqual(spoken_aloud(reply).count(words), 1)
        self.assertNotIn("From:", spoken_aloud(reply))

    def test_a_warn_shows_and_speaks_the_rules_words_once(self) -> None:
        self.check_once(self.door_reply(ReplyKind.WARN, "SR-03", "Join plus to plus."), "SR-03")

    def test_a_stop_shows_and_speaks_the_rules_words_once(self) -> None:
        self.check_once(self.door_reply(ReplyKind.STOP, "SR-07", "What to bring your supervisor: the part."), "SR-07")


class TheDemoCommand(unittest.TestCase):
    def run_demo(self, argv: list[str]) -> mock._Call:
        """The arguments start_chat got when main runs `argv`, with start_chat faked (no model, no engine)."""
        with mock.patch("solarchat.cli.main.start_chat", return_value=0) as start:
            self.assertEqual(main(argv, io.StringIO(""), io.StringIO(), io.StringIO()), 0)
        return start.call_args

    def test_demo_alone_chats_on_the_seed_pack_with_the_voice_on(self) -> None:
        args = self.run_demo(["--demo"]).args
        self.assertEqual(args[0], str(SEED))
        self.assertTrue(args[1])  # demo
        self.assertTrue(args[7])  # voice

    def test_demo_with_no_voice_is_silent(self) -> None:
        self.assertFalse(self.run_demo(["--demo", "--no-voice"]).args[7])

    def test_voice_without_demo_still_turns_it_on_and_no_voice_wins(self) -> None:
        self.assertTrue(self.run_demo(["--pack", "p", "--voice"]).args[7])
        self.assertFalse(self.run_demo(["--pack", "p", "--voice", "--no-voice"]).args[7])
        self.assertFalse(self.run_demo(["--pack", "p"]).args[7])

    def test_a_pack_given_wins_over_the_default(self) -> None:
        args = self.run_demo(["--pack", "packs/other", "--demo"]).args
        self.assertEqual(args[0], "packs/other")
        self.assertTrue(args[7])

    def test_the_default_pack_is_absolute_and_exists(self) -> None:
        self.assertTrue(DEMO_PACK.is_absolute())
        self.assertTrue(DEMO_PACK.is_dir())
        self.assertEqual(DEMO_PACK, SEED)

    def test_demo_alone_reaches_the_chat_for_real_and_speaks_through_the_fake(self) -> None:
        fake = Fake()
        out, err = io.StringIO(), io.StringIO()
        with mock.patch("solarchat.project.chat.Speaker", lambda stderr: Speaker(stderr, fake, "linux", found)):
            code = main(["--demo", "--answerer", "stub"], io.StringIO("A?\nquit\n"), out, err)
        self.assertEqual(code, 0)
        self.assertEqual(fake.calls[0][1], DEMO_BANNER)

    def test_no_voice_is_in_the_menu_and_the_menu_leads_with_demo(self) -> None:
        self.assertIn("--no-voice", MENU)
        self.assertIn("solarchat --demo ", MENU.split("Commands:")[1].split("\n")[6])

    def test_options_without_pack_or_demo_still_exit_2(self) -> None:
        err = io.StringIO()
        self.assertEqual(main(["--voice"], io.StringIO(""), io.StringIO(), err), 2)


if __name__ == "__main__":
    unittest.main()
