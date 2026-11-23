"""The command menu and the local key (TODO 2.5; SC-022 point 6): the key file is written in the config folder and
nowhere else, a folder inside the repository is refused, no output holds the key, the menu names every option, and the
stored key reaches the client. No network. The fake key is built at run time so the key scan has nothing to read."""
import contextlib
import io
import os
import stat
import unittest
from pathlib import Path
from unittest import mock

from solarchat.cli.main import MENU, build_parser, main
from solarchat.model import claude
from solarchat.model.key import config_dir, resolve_key
from test.support import ROOT, no_key

FAKE = "".join(["not", "-a-", "real", "-key-", "0123456789"])


def run(argv: list[str], stdin: str = "") -> tuple[int, str, str]:
    """The exit code, stdout and stderr of one command: run(["help"])[0] gives 0."""
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stderr(err):
        code = main(argv, io.StringIO(stdin), out, err)
    return code, out.getvalue(), err.getvalue()


class TheMenu(unittest.TestCase):
    def test_no_arguments_help_and_dash_dash_help_print_the_same_menu_and_need_no_pack(self) -> None:
        for argv in ([], ["help"], ["--help"]):
            self.assertEqual(run(argv), (0, MENU, ""))

    def test_the_menu_names_every_option_the_parser_has_and_says_it_is_typed_at_a_prompt(self) -> None:
        options = {o for action in build_parser()._actions for o in action.option_strings if o.startswith("--")}
        for option in options:
            self.assertIn(option, MENU)
        self.assertIn("prompt", MENU)
        self.assertNotIn("hidden", MENU)

    def test_the_chat_without_a_pack_exits_2_and_names_pack(self) -> None:
        code, _, err = run(["--voice"])
        self.assertEqual(code, 2)
        self.assertIn("--pack", err)


class TheKey(unittest.TestCase):
    def test_the_key_is_written_only_in_the_config_folder_owner_only_and_never_printed(self) -> None:
        with no_key() as folder:
            before = set(os.listdir(ROOT))
            code, out, err = run(["--key", FAKE])
            self.assertEqual(code, 0)
            self.assertEqual(os.listdir(folder), ["key"])
            self.assertEqual((Path(folder) / "key").read_text().strip(), FAKE)
            if os.name != "nt":
                self.assertEqual(stat.S_IMODE((Path(folder) / "key").stat().st_mode), 0o600)
            self.assertEqual(set(os.listdir(ROOT)), before)
            self.assertIn(str(Path(folder).resolve()), out)
            self.assertNotIn(FAKE, out + err)
            self.assertNotIn(FAKE[:8], out + err)

    def test_a_key_given_with_no_value_is_read_from_the_input_visibly_and_never_printed_back(self) -> None:
        with no_key() as folder:
            code, out, err = run(["--key"], FAKE + "\n")
            self.assertEqual((code, (Path(folder) / "key").read_text().strip()), (0, FAKE))
        self.assertIn("Anthropic key", out)
        self.assertNotIn(FAKE, out + err)

    def test_the_chat_with_no_key_asks_for_it_stores_it_and_starts(self) -> None:
        pack = str(ROOT / "packs" / "seed-mc4-leads")
        with no_key() as folder, mock.patch.dict("sys.modules", {"anthropic": mock.Mock()}):
            code, out, err = run(["--pack", pack, "--demo", "--role", "new", "--signed-off", "none"], FAKE + "\nquit\n")
            self.assertEqual((code, (Path(folder) / "key").read_text().strip()), (0, FAKE))
        self.assertIn("Ask a question", out)
        self.assertNotIn(FAKE, out + err)

    def test_the_chat_with_no_key_and_an_empty_input_exits_2_naming_the_command(self) -> None:
        with no_key() as folder:
            code, _, err = run(["--pack", str(ROOT / "packs" / "seed-mc4-leads"), "--demo"], "\n")
            self.assertEqual((code, os.listdir(folder)), (2, []))
        self.assertIn("solarchat --key", err)

    def test_an_empty_or_spaced_key_is_refused_and_not_echoed(self) -> None:
        with no_key() as folder:
            code, out, err = run(["--key", "two words"])
            self.assertEqual((code, os.listdir(folder)), (2, []))
            self.assertNotIn("two words", out + err)

    def test_a_config_folder_inside_the_repository_is_refused_and_nothing_is_written(self) -> None:
        inside = str(ROOT / "build" / "key-test-folder")
        with mock.patch.dict(os.environ, {"SOLARCHAT_CONFIG_DIR": inside}):
            code, out, err = run(["--key", FAKE])
            self.assertEqual(code, 2)
            self.assertIn("inside the repository", err)
            self.assertNotIn(FAKE, out + err)
            self.assertFalse(Path(inside).exists())
            self.assertEqual(run(["--forget-key"])[0], 2)
        with self.assertRaises(ValueError):
            config_dir({"SOLARCHAT_CONFIG_DIR": str(ROOT)})

    def test_forget_key_deletes_it_and_says_so_when_there_is_none(self) -> None:
        with no_key() as folder:
            run(["--key", FAKE])
            code, out, err = run(["--forget-key"])
            self.assertEqual((code, os.listdir(folder)), (0, []))
            self.assertNotIn(FAKE, out + err)
            self.assertIn("No stored key", run(["--forget-key"])[1])

    def test_the_environment_key_comes_first_then_the_stored_one(self) -> None:
        with no_key():
            self.assertIsNone(resolve_key())
            run(["--key", FAKE])
            self.assertEqual(resolve_key(), FAKE)
            with mock.patch.dict(os.environ, {"ANTHROPIC_API_KEY": "from-env"}):
                self.assertEqual(resolve_key(), "from-env")

    def test_the_stored_key_reaches_the_client_and_with_none_the_chat_exits_2_naming_the_command(self) -> None:
        seen: dict = {}

        sdk = mock.Mock(Anthropic=lambda **options: seen.update(options))
        with no_key():
            code, _, err = run(["--pack", str(ROOT / "packs" / "seed-mc4-leads"), "--demo"])
            self.assertEqual(code, 2)
            self.assertIn("solarchat --key", err)
            run(["--key", FAKE])
            with mock.patch.dict("sys.modules", {"anthropic": sdk}):
                claude.default_client()
        self.assertEqual(seen, {"api_key": FAKE})


if __name__ == "__main__":
    unittest.main()
