"""scripts/worker_venv.py: a worker's `.venv/` is a real directory of links to the shared venv's entries; each refusal
leaves the clone as it was. Every case runs in temporary folders with a fake source venv, never the real one."""
import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from scripts import worker_venv


class TheWorkerVenv(unittest.TestCase):
    def setUp(self) -> None:
        """A fake main checkout (its .venv holds bin, lib and pyvenv.cfg) and an empty clone beside it, in a temporary folder."""
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.root = Path(folder.name) / "main"
        self.clone = Path(folder.name) / "clone"
        for name in ("bin", "lib"):
            (self.root / ".venv" / name).mkdir(parents=True)
        (self.root / ".venv" / "pyvenv.cfg").write_text("home = /usr/bin\n")
        self.clone.mkdir()

    def run_main(self, argv: list[str]) -> tuple[int, str, str]:
        """The exit code, stdout and stderr of the script against the fake root: run_main([str(self.clone)]) gives (0, ..., "")."""
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = worker_venv.main(argv, self.root)
        return code, out.getvalue(), err.getvalue()

    def test_the_clone_gets_a_real_directory_with_one_link_per_entry(self) -> None:
        code, out, _ = self.run_main([str(self.clone)])
        target = self.clone / ".venv"
        self.assertEqual(code, 0)
        self.assertIn("made", out)
        self.assertTrue(target.is_dir() and not target.is_symlink())
        self.assertEqual(sorted(p.name for p in target.iterdir()), ["bin", "lib", "pyvenv.cfg"])
        for name in ("bin", "lib", "pyvenv.cfg"):
            self.assertTrue((target / name).is_symlink())
            self.assertEqual((target / name).resolve(), (self.root / ".venv" / name).resolve())

    def test_a_correct_one_already_there_is_fine_and_unchanged(self) -> None:
        self.run_main([str(self.clone)])
        code, out, _ = self.run_main([str(self.clone)])
        self.assertEqual(code, 0)
        self.assertIn("already in place", out)

    def test_a_missing_source_venv_is_refused(self) -> None:
        (self.root / ".venv" / "pyvenv.cfg").unlink()
        for each in ("bin", "lib"):
            (self.root / ".venv" / each).rmdir()
        (self.root / ".venv").rmdir()
        code, _, err = self.run_main([str(self.clone)])
        self.assertEqual(code, 1)
        self.assertIn("not a real directory", err)
        self.assertFalse((self.clone / ".venv").exists())

    def test_the_checkout_itself_is_refused(self) -> None:
        code, _, err = self.run_main([str(self.root)])
        self.assertEqual(code, 1)
        self.assertIn("this checkout itself", err)

    def test_a_clone_that_is_not_a_folder_is_refused(self) -> None:
        code, _, err = self.run_main([str(self.clone / "nowhere")])
        self.assertEqual(code, 1)
        self.assertIn("not a folder", err)

    def test_a_symlink_to_the_venv_is_refused_and_left_alone(self) -> None:
        (self.clone / ".venv").symlink_to(self.root / ".venv")
        code, _, err = self.run_main([str(self.clone)])
        self.assertEqual(code, 1)
        self.assertIn("is not a directory of links", err)
        self.assertTrue((self.clone / ".venv").is_symlink())

    def test_a_real_directory_of_other_content_is_refused_and_left_alone(self) -> None:
        (self.clone / ".venv").mkdir()
        (self.clone / ".venv" / "mine.txt").write_text("keep")
        code, _, _ = self.run_main([str(self.clone)])
        self.assertEqual(code, 1)
        self.assertEqual((self.clone / ".venv" / "mine.txt").read_text(), "keep")

    def test_a_directory_missing_one_link_is_refused(self) -> None:
        self.run_main([str(self.clone)])
        (self.clone / ".venv" / "lib").unlink()
        code, _, _ = self.run_main([str(self.clone)])
        self.assertEqual(code, 1)
        self.assertFalse((self.clone / ".venv" / "lib").exists())

    def test_a_link_to_another_place_is_refused(self) -> None:
        self.run_main([str(self.clone)])
        (self.clone / ".venv" / "lib").unlink()
        (self.clone / ".venv" / "lib").symlink_to(self.clone)
        code, _, _ = self.run_main([str(self.clone)])
        self.assertEqual(code, 1)

    def test_the_arguments_and_the_help(self) -> None:
        self.assertEqual(self.run_main([])[0], 2)
        code, out, _ = self.run_main(["--help"])
        self.assertEqual(code, 0)
        self.assertEqual(out.strip(), worker_venv.__doc__.strip())
        self.assertFalse((self.clone / ".venv").exists())


if __name__ == "__main__":
    unittest.main()
