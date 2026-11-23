"""`solarchat --has-key` (TODO 2.11): exit 0 when a key would be found, 1 when not, never the key; and the Windows setup
script's text, which cannot be run here (J-082)."""
import os
import unittest
from pathlib import Path
from unittest import mock

from test.support import no_key
from test.test_key import FAKE, run

ROOT = Path(__file__).resolve().parents[1]
SETUP = ROOT / "setup.cmd"


class HasKey(unittest.TestCase):
    def test_no_key_exits_1_and_says_how_to_set_one(self) -> None:
        with no_key():
            code, out, err = run(["--has-key"])
        self.assertEqual(code, 1)
        self.assertIn("solarchat --key", out)

    def test_a_stored_key_exits_0_and_is_not_shown(self) -> None:
        with no_key() as folder:
            run(["--key", FAKE])
            code, out, err = run(["--has-key"])
            self.assertEqual(code, 0)
            self.assertIn(str(Path(folder).resolve() / "key"), out)
        self.assertNotIn(FAKE, out + err)

    def test_the_environment_key_exits_0_and_is_not_shown(self) -> None:
        with no_key(), mock.patch.dict(os.environ, {"ANTHROPIC_API_KEY": FAKE}):
            code, out, err = run(["--has-key"])
        self.assertEqual(code, 0)
        self.assertIn("ANTHROPIC_API_KEY", out)
        self.assertNotIn(FAKE, out + err)

    def test_a_refused_folder_exits_2(self) -> None:
        with mock.patch.dict(os.environ, {"ANTHROPIC_API_KEY": "", "SOLARCHAT_CONFIG_DIR": str(ROOT / "build" / "x")}):
            self.assertEqual(run(["--has-key"])[0], 2)


class SetupScript(unittest.TestCase):
    def test_the_script_uses_crlf_and_no_setx(self) -> None:
        data = SETUP.read_bytes()
        self.assertEqual(data.count(b"\n"), data.count(b"\r\n"), "every line ends in CRLF")
        self.assertNotIn(b"setx", data.lower())

    def test_the_install_is_hash_checked_and_binary_only(self) -> None:
        text = SETUP.read_text(encoding="utf-8")
        self.assertIn("--require-hashes", text)
        self.assertIn("--only-binary :all:", text)
        self.assertIn("requirements.lock", text)

    def test_the_key_is_not_called_hidden(self) -> None:
        self.assertNotIn("hidden", SETUP.read_text(encoding="utf-8"))

    def test_it_asks_has_key_before_it_asks_for_the_key(self) -> None:
        text = SETUP.read_text(encoding="utf-8")
        self.assertLess(text.index("--has-key"), text.index("solarchat.cmd\" --key"))

    def test_the_launcher_runs_setup_when_there_is_no_venv_and_stays_crlf(self) -> None:
        data = (ROOT / "bin" / "solarchat.cmd").read_bytes()
        self.assertEqual(data.count(b"\n"), data.count(b"\r\n"))
        self.assertIn(b"setup.cmd", data)
        self.assertIn(b"import anthropic", data)
        self.assertIn(b"%*", data)
        self.assertLess(data.index(b"setup.cmd"), data.index(b"%*"))

    def test_gitattributes_keeps_the_scripts_in_their_line_endings(self) -> None:
        text = (ROOT / ".gitattributes").read_text()
        for line in ("*.cmd text eol=crlf", "bin/solarchat text eol=lf", "*.sh text eol=lf"):
            self.assertIn(line, text)


if __name__ == "__main__":
    unittest.main()
