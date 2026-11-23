"""Choosing the voice (TODO 2.13): `--voices` lists the installed voices, `--voice-name` keeps one beside the key, and the name
reaches the engine only as an environment variable on Windows (never in the script) or as `-v <name>` list items elsewhere.
Fake runners and a temporary config folder; no PowerShell, no real engine."""
import base64
import io
import os
import subprocess
import tempfile
import unittest
from unittest import mock

from solarchat.cli.main import MENU, main
from solarchat.project.speech import (NO_ENGINE, VOICE_VARIABLE, WINDOWS_LIST_ENCODED, WINDOWS_LIST_SCRIPT, WINDOWS_SCRIPT, Speaker,
                                      engine_command, forget_voice, list_command, save_voice, stored_voice, voice_name_command,
                                      voice_path, voices_command)
from test.support import ROOT
from test.test_speech import Fake, found

_FOLDER = tempfile.TemporaryDirectory()


def setUpModule() -> None:
    """No chosen voice and no stored key anywhere but a temporary folder."""
    os.environ["SOLARCHAT_CONFIG_DIR"] = _FOLDER.name


def tearDownModule() -> None:
    """Put the environment back and remove the folder."""
    os.environ.pop("SOLARCHAT_CONFIG_DIR", None)
    _FOLDER.cleanup()


class Lister:
    """A runner for the listing command: records the command and gives `stdout`, or raises."""

    def __init__(self, stdout: str = "", code: int = 0, error: Exception | None = None) -> None:
        """Hold what to print: Lister("a\\n") prints one line."""
        self.commands: list[list[str]] = []
        self.stdout, self.code, self.error = stdout, code, error

    def __call__(self, command: list[str], *, capture_output: bool, text: bool, encoding: str, check: bool, timeout: int,
                 shell: bool = False) -> subprocess.CompletedProcess:
        """Record the command; refuse a shell (subprocess.run's keywords, named)."""
        assert not shell and capture_output and text and check is False and timeout > 0
        self.commands.append(command)
        if self.error:
            raise self.error
        return subprocess.CompletedProcess(command, self.code, self.stdout, "")


WINDOWS_LISTING = "Microsoft David Desktop\ten-US\tMale\nMicrosoft Zira Desktop\ten-US\tFemale\n"
MAC_LISTING = "Albert              en_US    # Hello\nBad News            en_US    # Hello\n"
LINUX_LISTING = "Pty Language Age/Gender VoiceName          File          Other Languages\n 5  en-gb          M  english             en\n"


class TheChosenVoice(unittest.TestCase):
    def setUp(self) -> None:
        """Each test starts with no chosen voice."""
        forget_voice()

    def test_a_voice_is_saved_read_and_forgotten_beside_the_key(self) -> None:
        self.assertIsNone(stored_voice())
        path = save_voice("  Microsoft Zira Desktop ")
        self.assertEqual(path, voice_path())
        self.assertEqual(path.parent, voice_path({"SOLARCHAT_CONFIG_DIR": _FOLDER.name}).parent)
        self.assertEqual(stored_voice(), "Microsoft Zira Desktop")
        self.assertTrue(forget_voice())
        self.assertIsNone(stored_voice())
        self.assertFalse(forget_voice())

    def test_a_bad_name_or_a_folder_in_the_repository_is_refused(self) -> None:
        for name in ("", "   ", "x" * 101, "a\nb", "a\x00b", "a\x1bb"):
            with self.assertRaises(ValueError):
                save_voice(name)
        self.assertIsNone(stored_voice())
        save_voice("x" * 100)
        with self.assertRaises(ValueError):
            save_voice("Zira", {"SOLARCHAT_CONFIG_DIR": str(ROOT / "voice-test")})
        self.assertIsNone(stored_voice({"SOLARCHAT_CONFIG_DIR": str(ROOT / "voice-test")}))

    def test_the_command_saves_forgets_and_refuses_in_words(self) -> None:
        out, err = io.StringIO(), io.StringIO()
        self.assertEqual(voice_name_command("Samantha", out, err, "darwin", Lister(), found), 0)
        self.assertEqual(out.getvalue(), "Voice set to Samantha. It is used whenever the voice is on.\n")
        self.assertEqual(stored_voice(), "Samantha")
        out = io.StringIO()
        self.assertEqual(voice_name_command("default", out, err), 0)
        self.assertIsNone(stored_voice())
        self.assertEqual(voice_name_command("", out, err), 2)
        self.assertIn("the voice was not saved", err.getvalue())

    def test_on_windows_an_unlisted_name_warns_and_is_still_saved_and_a_failed_listing_does_not_warn(self) -> None:
        out, err = io.StringIO(), io.StringIO()
        self.assertEqual(voice_name_command("Nobody", out, err, "win32", Lister(WINDOWS_LISTING), found), 0)
        self.assertIn("warning", err.getvalue())
        self.assertEqual(stored_voice(), "Nobody")
        out, err = io.StringIO(), io.StringIO()
        self.assertEqual(voice_name_command("microsoft zira desktop", out, err, "win32", Lister(WINDOWS_LISTING), found), 0)
        self.assertEqual(err.getvalue(), "")
        for broken in (Lister(code=1), Lister(error=OSError("gone")), Lister(error=subprocess.TimeoutExpired("x", 1))):
            err = io.StringIO()
            self.assertEqual(voice_name_command("Nobody", io.StringIO(), err, "win32", broken, found), 0)
            self.assertEqual(err.getvalue(), "")

    def test_with_a_chat_it_is_an_error_naming_the_two_steps(self) -> None:
        for argv in (["--voice-name", "Zira", "--demo"], ["--voice-name", "Zira", "--pack", "p"]):
            code, _, err = run_main(argv)
            self.assertEqual(code, 2)
            self.assertIn("then start the chat", err)
        self.assertIsNone(stored_voice())

    def test_the_command_line_saves_the_voice(self) -> None:
        code, out, _ = run_main(["--voice-name", "Samantha"])
        self.assertEqual((code, stored_voice()), (0, "Samantha"))
        self.assertIn("Voice set to Samantha.", out)


def run_main(argv: list[str]) -> tuple[int, str, str]:
    """The exit code, stdout and stderr of main(argv)."""
    out, err = io.StringIO(), io.StringIO()
    return main(argv, io.StringIO(""), out, err), out.getvalue(), err.getvalue()


class TheVoiceList(unittest.TestCase):
    def setUp(self) -> None:
        """Each test starts with no chosen voice."""
        forget_voice()

    def test_each_platform_builds_its_own_listing_command(self) -> None:
        self.assertEqual(list_command("darwin", found), ["/bin/say", "-v", "?"])
        self.assertEqual(list_command("linux", found), ["/bin/espeak", "--voices"])
        windows = list_command("win32", found)
        self.assertEqual(windows, ["/bin/powershell", "-NoProfile", "-NonInteractive", "-EncodedCommand", WINDOWS_LIST_ENCODED])
        self.assertEqual(base64.b64decode(WINDOWS_LIST_ENCODED).decode("utf-16-le"), WINDOWS_LIST_SCRIPT)
        self.assertIn("GetInstalledVoices()", WINDOWS_LIST_SCRIPT)
        for platform in ("win32", "darwin", "linux"):
            self.assertIsNone(list_command(platform, lambda name: None))

    def test_the_list_marks_the_chosen_voice_and_says_how_to_choose(self) -> None:
        for platform, listing, name, marked in (("win32", WINDOWS_LISTING, "Microsoft Zira Desktop", "Microsoft Zira Desktop (en-US, Female) (chosen)"),
                                                ("darwin", MAC_LISTING, "Bad News", "Bad News            en_US    # Hello (chosen)"),
                                                ("linux", LINUX_LISTING, "english", " 5  en-gb          M  english             en (chosen)")):
            save_voice(name)
            runner, out, err = Lister(listing), io.StringIO(), io.StringIO()
            self.assertEqual(voices_command(out, err, platform, runner, found), 0)
            lines = out.getvalue().splitlines()
            self.assertEqual([line for line in lines if "(chosen)" in line], [marked])
            self.assertEqual(lines[-1], 'Choose one with: solarchat --voice-name "<name>"')
            self.assertEqual(runner.commands, [list_command(platform, found)])

    def test_with_none_chosen_nothing_is_marked(self) -> None:
        out = io.StringIO()
        self.assertEqual(voices_command(out, io.StringIO(), "win32", Lister(WINDOWS_LISTING), found), 0)
        self.assertNotIn("(chosen)", out.getvalue())

    def test_no_engine_is_exit_1_with_the_one_line_and_a_failed_listing_is_exit_1(self) -> None:
        for platform in ("win32", "darwin", "linux"):
            out, err = io.StringIO(), io.StringIO()
            self.assertEqual(voices_command(out, err, platform, Lister(), lambda name: None), 1)
            self.assertEqual((out.getvalue(), err.getvalue()), ("", NO_ENGINE + "\n"))
        err = io.StringIO()
        self.assertEqual(voices_command(io.StringIO(), err, "linux", Lister(code=1), found), 1)
        self.assertIn("could not be listed", err.getvalue())

    def test_through_the_command_with_no_engine(self) -> None:
        out, err = io.StringIO(), io.StringIO()
        with mock.patch("shutil.which", lambda name: None), mock.patch("sys.platform", "linux"):
            self.assertEqual(main(["--voices"], io.StringIO(""), out, err), 1)
        self.assertEqual(err.getvalue(), NO_ENGINE + "\n")


class TheVoiceInUse(unittest.TestCase):
    def setUp(self) -> None:
        """Each test starts with no chosen voice."""
        forget_voice()

    def test_the_windows_script_is_the_same_whatever_voice_is_chosen_and_the_name_arrives_only_in_the_environment(self) -> None:
        evil = '"; Remove-Item x; "'
        plain = engine_command("win32", found)
        self.assertEqual(engine_command("win32", found, evil), plain)
        self.assertIn(f"$env:{VOICE_VARIABLE}", WINDOWS_SCRIPT)
        self.assertIn("SelectVoice($env:SOLARCHAT_VOICE_NAME)", WINDOWS_SCRIPT)
        fake = Fake()
        Speaker(io.StringIO(), fake, "win32", found, voice=evil).say("Hello.")
        command, said = fake.calls[0]
        self.assertEqual(command, plain)
        self.assertEqual(said, "Hello.")
        self.assertEqual(fake.envs[0][VOICE_VARIABLE], evil)
        self.assertFalse(any(evil in part for part in command))
        self.assertNotIn(evil, WINDOWS_SCRIPT)

    def test_with_no_voice_chosen_the_environment_is_not_passed(self) -> None:
        fake = Fake()
        Speaker(io.StringIO(), fake, "win32", found).say("Hello.")
        self.assertEqual(fake.envs, [None])

    def test_mac_and_linux_take_the_name_as_separate_list_items(self) -> None:
        self.assertEqual(engine_command("darwin", found, "Bad News"), ["/bin/say", "-v", "Bad News", "-f", "-"])
        self.assertEqual(engine_command("linux", found, "en-us"), ["/bin/espeak", "-v", "en-us", "--stdin"])

    def test_the_speaker_reads_the_stored_voice_once_when_it_starts(self) -> None:
        save_voice("Samantha")
        fake = Fake()
        speaker = Speaker(io.StringIO(), fake, "darwin", found)
        save_voice("Alex")
        speaker.say("Hello.")
        self.assertEqual(fake.calls[0][0], ["/bin/say", "-v", "Samantha", "-f", "-"])

class TheMenu(unittest.TestCase):
    def test_the_voice_options_are_in_the_menu(self) -> None:
        self.assertIn("--voices", MENU)
        self.assertIn("--voice-name", MENU)


if __name__ == "__main__":
    unittest.main()
