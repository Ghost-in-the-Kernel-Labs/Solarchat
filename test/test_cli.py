"""The chat command driven through stdin and stdout: the banner, the quit words, the history kept, the citations, a rule's
words, and the exits, with the stub answerer or a fake; no network (TODO 1.16; SC-019 amended, SC-010, HAD-06, SC-022)."""
import contextlib
import io
import os
import unittest
from unittest import mock

from solarchat.answer.door import DO_NOT_KNOW_TEXT
from solarchat.cli.main import main
from solarchat.leaf.contract import DEMO_BANNER, Finding, PassageRef, Reply, ReplyKind, Turn
from solarchat.model.claude import ModelError
from solarchat.project.chat import converse, render, spoken
from solarchat.packs.load import load_pack
from test.support import ROOT

SEED = ROOT / "packs" / "seed-mc4-leads"
STEP = PassageRef("seed-mc4-leads", "step-06")
PACK = load_pack(SEED)


def chat(lines: str, options: list[str] | None = None) -> tuple[int, str, str]:
    """The chat's exit code, stdout and stderr when `lines` is typed: chat("quit\\n")[0] gives 0 with the stub answerer."""
    out, err = io.StringIO(), io.StringIO()
    argv = ["--pack", str(SEED), "--demo", "--answerer", "stub"] if options is None else options
    with contextlib.redirect_stderr(err):  # argparse writes a usage error to the process's stderr
        code = main(argv, io.StringIO(lines), out, err)
    return code, out.getvalue(), err.getvalue()


class Scripted:
    """An answerer that gives scripted findings, one per call, and remembers the history it was given: Scripted([Finding()])
    finds Finding() until it runs out, then repeats the last."""

    name = "scripted"

    def __init__(self, findings: list) -> None:
        """Hold the findings (or an exception to raise) to give in order."""
        self.findings = list(findings)
        self.histories: list[tuple[Turn, ...]] = []

    def find(self, question: str, passages: tuple, history: tuple[Turn, ...] = ()) -> Finding:
        """Record the history, then give the next scripted finding or raise the scripted exception."""
        self.histories.append(history)
        item = self.findings.pop(0) if len(self.findings) > 1 else self.findings[0]
        if isinstance(item, Exception):
            raise item
        return item


def talk(answerer: Scripted, lines: str, demo: bool = True) -> tuple[str, str]:
    """The stdout and stderr of a conversation with this answerer on the seed pack."""
    out, err = io.StringIO(), io.StringIO()
    converse(PACK, demo, answerer, io.StringIO(lines), out, err)
    return out.getvalue(), err.getvalue()


class TheStubChat(unittest.TestCase):
    def test_the_demo_banner_is_shown_once_at_the_start_and_on_every_reply(self) -> None:
        code, out, _ = chat("Which lead is positive?\nWhat now?\nquit\n")
        self.assertEqual(code, 0)
        self.assertTrue(out.startswith(DEMO_BANNER))
        self.assertEqual(out.count(DEMO_BANNER), 3)
        self.assertEqual(out.count(DO_NOT_KNOW_TEXT), 2)

    def test_quit_and_the_end_of_input_both_end_the_chat_with_exit_0(self) -> None:
        self.assertEqual(chat("quit\n")[0], 0)
        self.assertEqual(chat("QUIT\nignored\n")[0], 0)
        code, out, _ = chat("Which lead is positive?\n")
        self.assertEqual((code, out.count(DO_NOT_KNOW_TEXT)), (0, 1))

    def test_a_blank_line_is_skipped_and_nothing_after_quit_is_read(self) -> None:
        _, out, _ = chat("\n   \nquit\nWhat?\n")
        self.assertEqual(out.count(DO_NOT_KNOW_TEXT), 0)

    def test_without_demo_a_demo_pack_exits_2_in_words(self) -> None:
        code, out, err = chat("", ["--pack", str(SEED), "--answerer", "stub"])
        self.assertEqual((code, out), (2, ""))
        self.assertIn("seed-mc4-leads is a demo pack: run with --demo (HAD-06)", err)

    def test_a_missing_pack_and_a_missing_pack_option_exit_2(self) -> None:
        self.assertEqual(chat("", ["--pack", str(ROOT / "no-such-pack"), "--answerer", "stub"])[0], 2)
        self.assertEqual(chat("", ["--answerer", "stub"])[0], 2)

    def test_claude_is_the_default_and_with_no_key_exits_2_in_plain_words_and_calls_nothing(self) -> None:
        with mock.patch.dict(os.environ, {"ANTHROPIC_API_KEY": ""}):
            code, out, err = chat("", ["--pack", str(SEED), "--demo"])
        self.assertEqual((code, out), (2, ""))
        self.assertIn("ANTHROPIC_API_KEY is not set", err)

    def test_model_is_an_option_haiku_is_allowed_and_another_model_exits_2(self) -> None:
        with mock.patch.dict(os.environ, {"ANTHROPIC_API_KEY": ""}):
            code, _, err = chat("", ["--pack", str(SEED), "--demo", "--model", "claude-haiku-5-5"])
        self.assertEqual(code, 2)
        self.assertIn("ANTHROPIC_API_KEY is not set", err)
        self.assertEqual(chat("", ["--pack", str(SEED), "--demo", "--model", "gpt-9"])[0], 2)

    def test_an_unknown_answerer_exits_2(self) -> None:
        self.assertEqual(chat("", ["--pack", str(SEED), "--demo", "--answerer", "gpt"])[0], 2)


class TheConversation(unittest.TestCase):
    def test_the_history_grows_by_what_was_said_without_the_banner_or_the_sources(self) -> None:
        answerer = Scripted([Finding((STEP,), "Which device is it?"), Finding((STEP,), "Read the label.")])
        talk(answerer, "My panel is dead.\nThe inverter.\nquit\n")
        first, second = answerer.histories
        self.assertEqual(first, ())
        self.assertEqual(second, (Turn("user", "My panel is dead."), Turn("assistant", "Which device is it?")))

    def test_a_reply_shows_its_words_the_passage_title_and_each_sources_title_and_page(self) -> None:
        out, _ = talk(Scripted([Finding((STEP,), "Push the leads together.")]), "How do I join them?\nquit\n")
        self.assertIn("Push the leads together.", out)
        self.assertIn("From: ", out)
        self.assertIn("page ", out)
        self.assertEqual(out.count(DEMO_BANNER), 1)

    def test_without_demo_there_is_no_banner_anywhere(self) -> None:
        packs = io.StringIO()
        code = main(["--pack", str(ROOT / "test" / "fixtures" / "packs" / "good"), "--answerer", "stub"],
                    io.StringIO("Where is the Voc?\nquit\n"), packs, io.StringIO())
        self.assertEqual(code, 0)
        self.assertNotIn("DEMO", packs.getvalue())

    def test_a_model_that_fails_is_told_in_words_the_turn_is_dropped_and_the_chat_goes_on(self) -> None:
        answerer = Scripted([ModelError("the model service could not be reached"), Finding()])
        out, err = talk(answerer, "First?\nSecond?\nquit\n")
        self.assertIn("Sorry: the model service could not be reached", err)
        self.assertEqual(answerer.histories, [(), ()])
        self.assertEqual(out.count(DO_NOT_KNOW_TEXT), 1)

    def test_spoken_drops_the_banner_and_the_sources(self) -> None:
        reply = Reply(ReplyKind.ANSWER, f"{DEMO_BANNER}\n\nJoin plus to plus.\n\nFrom: Step 6 (Pack): Manual, page 15", (STEP,))
        self.assertEqual(spoken(reply), "Join plus to plus.")
        self.assertEqual(spoken(Reply(ReplyKind.DO_NOT_KNOW, "I do not know.")), "I do not know.")

    def test_a_warn_and_a_stop_show_the_rules_words_first_and_an_answer_does_not(self) -> None:
        warn = Reply(ReplyKind.WARN, "Cover the panel first.", (STEP,), "SR-03")
        stop = Reply(ReplyKind.STOP, "Stop.", (), "SR-08")
        self.assertTrue(render(warn).startswith("Safety rule SR-03: "))
        self.assertTrue(render(stop).startswith("Safety rule SR-08: "))
        self.assertTrue(render(warn).endswith("Cover the panel first."))
        self.assertEqual(render(Reply(ReplyKind.ANSWER, "Join.", (STEP,))), "Join.")


if __name__ == "__main__":
    unittest.main()
