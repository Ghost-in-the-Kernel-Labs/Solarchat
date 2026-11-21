"""The answering door's order of operations, each step on its own, and the two answerers that need no model (TODO 1.6; SC-019, HAD-03, HAD-06)."""
import json
import unittest
from dataclasses import replace
from pathlib import Path

from solarchat.answer.door import DO_NOT_KNOW_TEXT, NO_PACK_TEXT, answer
from solarchat.answer.recorded import RecordedAnswerer
from solarchat.answer.stub import NoAnswer
from solarchat.leaf.contract import DEMO_BANNER, Finding, Passage, PassageRef, ReplyKind
from solarchat.packs.load import Pack, load_pack
from test.support import ROOT, scratch

GOOD = load_pack(ROOT / "test" / "fixtures" / "packs" / "good")
SEED = load_pack(ROOT / "packs" / "seed-mc4-leads")
VOLTAGE = PassageRef("good", "voltage")
LABEL = PassageRef("good", "label")


class Spy:
    """An answerer that returns a fixed finding and remembers what it was asked: Spy(Finding()).asked is [] at first."""

    name = "spy"

    def __init__(self, finding: Finding) -> None:
        """Hold the finding to return and start with nothing asked."""
        self.finding = finding
        self.asked: list[tuple[str, tuple[Passage, ...]]] = []

    def find(self, question: str, passages: tuple[Passage, ...]) -> Finding:
        """Record the call and return the fixed finding: Spy(Finding()).find("q", ()) gives Finding()."""
        self.asked.append((question, passages))
        return self.finding


class Raising:
    """An answerer that breaks: Raising().find("q", ()) raises RuntimeError."""

    name = "raising"

    def find(self, question: str, passages: tuple[Passage, ...]) -> Finding:
        """Raise RuntimeError, as a buggy answerer would."""
        raise RuntimeError("the answerer broke")


def demo_copy(pack: Pack) -> Pack:
    """The pack with the status demo: demo_copy(GOOD).manifest["status"] gives "demo"."""
    return replace(pack, manifest=dict(pack.manifest, status="demo"))


def one(ref: PassageRef) -> Spy:
    """A spy that finds one passage: one(VOLTAGE).finding.refs gives (VOLTAGE,)."""
    return Spy(Finding((ref,), "Voc must be lower."))


class Step1AnEmptyQuestion(unittest.TestCase):
    def test_an_empty_or_blank_question_is_i_do_not_know_and_the_answerer_is_not_called(self) -> None:
        for question in ("", "   ", "\n\t"):
            spy = one(VOLTAGE)
            reply = answer(question, (GOOD,), False, spy)
            self.assertEqual((reply.kind, reply.text, reply.passage_refs), (ReplyKind.DO_NOT_KNOW, DO_NOT_KNOW_TEXT, ()))
            self.assertEqual(spy.asked, [])


class Step2ThePacksThatMayAnswer(unittest.TestCase):
    def test_a_demo_pack_outside_demo_mode_never_reaches_the_answerer(self) -> None:
        spy = one(VOLTAGE)
        reply = answer("Where is the Voc?", (demo_copy(GOOD),), False, spy)
        self.assertEqual((reply.kind, reply.text), (ReplyKind.DO_NOT_KNOW, NO_PACK_TEXT))
        self.assertEqual(spy.asked, [])

    def test_a_demo_pack_answers_in_demo_mode(self) -> None:
        reply = answer("Where is the Voc?", (demo_copy(GOOD),), True, one(VOLTAGE))
        self.assertEqual(reply.kind, ReplyKind.ANSWER)

    def test_no_packs_at_all_is_the_same_refusal(self) -> None:
        self.assertEqual(answer("Where is the Voc?", (), True, one(VOLTAGE)).text, DEMO_BANNER + "\n\n" + NO_PACK_TEXT)

    def test_a_status_the_door_does_not_know_never_answers(self) -> None:
        library = replace(GOOD, manifest=dict(GOOD.manifest, status="library"))
        self.assertEqual(answer("Where is the Voc?", (library,), True, one(VOLTAGE)).text[-len(NO_PACK_TEXT):], NO_PACK_TEXT)

    def test_the_answerer_gets_the_usable_packs_passages_in_pack_order_and_no_other(self) -> None:
        spy = Spy(Finding())
        answer("Where is the Voc?", (GOOD, demo_copy(SEED)), False, spy)
        question, passages = spy.asked[0]
        self.assertEqual(question, "Where is the Voc?")
        self.assertEqual([passage.ref for passage in passages], [VOLTAGE, LABEL])
        spy = Spy(Finding())
        answer("Where is the Voc?", (demo_copy(SEED), GOOD), True, spy)
        self.assertEqual(len(spy.asked[0][1]), 87)
        self.assertEqual(spy.asked[0][1][0].ref, PassageRef("seed-mc4-leads", "step-01"))
        self.assertEqual(spy.asked[0][1][-1].ref, LABEL)


class Step3FindAndStep4TheContract(unittest.TestCase):
    def test_what_the_answerer_raises_reaches_the_caller(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "the answerer broke"):
            answer("Where is the Voc?", (GOOD,), False, Raising())

    def test_a_ref_not_among_the_passages_is_answered_i_do_not_know(self) -> None:
        reply = answer("Where is the Voc?", (GOOD,), False, one(PassageRef("good", "invented")))
        self.assertEqual((reply.kind, reply.text, reply.passage_refs), (ReplyKind.DO_NOT_KNOW, DO_NOT_KNOW_TEXT, ()))

    def test_a_ref_in_a_pack_that_may_not_answer_is_one_not_given(self) -> None:
        reply = answer("Where is the Voc?", (GOOD, demo_copy(SEED)), False, one(PassageRef("seed-mc4-leads", "step-01")))
        self.assertEqual(reply.kind, ReplyKind.DO_NOT_KNOW)

    def test_a_ref_cited_twice_is_refused(self) -> None:
        reply = answer("Where is the Voc?", (GOOD,), False, Spy(Finding((VOLTAGE, VOLTAGE), "Voc must be lower.")))
        self.assertEqual(reply.kind, ReplyKind.DO_NOT_KNOW)

    def test_more_than_the_most_cited_passages_is_refused(self) -> None:
        refs = tuple(passage.ref for passage in SEED.passages[:4])
        self.assertEqual(answer("Where?", (SEED,), True, Spy(Finding(refs, "Four."))).kind, ReplyKind.DO_NOT_KNOW)
        self.assertEqual(answer("Where?", (SEED,), True, Spy(Finding(refs[:3], "Three."))).kind, ReplyKind.ANSWER)


class Step5AndStep7TheAnswer(unittest.TestCase):
    def test_an_empty_finding_is_i_do_not_know_with_no_passage(self) -> None:
        reply = answer("Where is the Voc?", (GOOD,), False, NoAnswer())
        self.assertEqual((reply.kind, reply.text, reply.passage_refs), (ReplyKind.DO_NOT_KNOW, DO_NOT_KNOW_TEXT, ()))

    def test_an_answer_is_the_findings_words_then_one_from_line_per_ref(self) -> None:
        finding = Finding((VOLTAGE, LABEL), "Voc must be lower.", 2.0)
        reply = answer("Where is the Voc?", (GOOD,), False, Spy(finding))
        self.assertEqual((reply.kind, reply.passage_refs, reply.safety_rule_id), (ReplyKind.ANSWER, (VOLTAGE, LABEL), None))
        self.assertEqual(reply.text, "Voc must be lower.\n\n"
                         "From: Check the voltages match (Connecting a panel to a power station): "
                         "Examplesun ES-100 installation manual, page 1\n"
                         "From: Reading the label (Connecting a panel to a power station): "
                         "Examplesun ES-100 installation manual, page 1; Reading a panel's label (web page)")

    def test_an_unknown_page_is_worded_as_not_yet_found(self) -> None:
        reply = answer("Where?", (SEED,), True, Spy(Finding((PassageRef("seed-mc4-leads", "step-01"),), "Compare them.")))
        self.assertIn("page not yet found", reply.text)
        self.assertIn("From: Check the voltages match (Connecting a solar panel by its MC4 leads): ", reply.text)
        self.assertIn("EcoFlow R600 user manual, page 15: solar panel connection, page 15", reply.text)

    def test_the_safety_step_is_not_built_so_a_passage_that_fires_a_rule_is_still_an_answer(self) -> None:
        reply = answer("How do I disconnect?", (SEED,), True, Spy(Finding((PassageRef("seed-mc4-leads", "step-12"),), "Use the tool.")))
        self.assertEqual((reply.kind, reply.safety_rule_id), (ReplyKind.ANSWER, None))


class Step8TheDemoBanner(unittest.TestCase):
    def test_every_kind_of_reply_carries_the_banner_in_demo_mode_and_none_outside_it(self) -> None:
        cases = [("", NoAnswer()), ("Where?", NoAnswer()), ("Where?", one(VOLTAGE))]
        for question, answerer in cases:
            self.assertTrue(answer(question, (GOOD,), True, answerer).text.startswith(DEMO_BANNER + "\n\n"))
            self.assertNotIn(DEMO_BANNER, answer(question, (GOOD,), False, answerer).text)
        refused = answer("Where?", (demo_copy(GOOD),), False, NoAnswer())
        self.assertNotIn(DEMO_BANNER, refused.text)

    def test_the_banner_is_only_a_prefix(self) -> None:
        plain = answer("Where?", (GOOD,), False, one(VOLTAGE))
        banner = answer("Where?", (GOOD,), True, one(VOLTAGE))
        self.assertEqual(banner.text, DEMO_BANNER + "\n\n" + plain.text)
        self.assertEqual((banner.kind, banner.passage_refs), (plain.kind, plain.passage_refs))


class TheNoAnswerAnswerer(unittest.TestCase):
    def test_it_finds_nothing_for_every_question(self) -> None:
        self.assertEqual(NoAnswer.name, "no-answer")
        for question in ("Where is the Voc?", "", "anything"):
            self.assertEqual(NoAnswer().find(question, GOOD.passages), Finding())


def replies_file(changes: dict | None = None) -> Path:
    """A replies file in a scratch folder, with `changes` laid over a good one: replies_file().is_file() is True."""
    document = {"version": 1, "set_sha256": "ab" * 32, "answerer": "claude-test", "recorded_on": "2026-11-21",
                "replies": {"Where is the Voc?": {"refs": [["good", "voltage"]], "text": "Voc must be lower.", "score": 3.5}}}
    document.update(changes or {})
    path = scratch() / "replies.json"
    path.write_text(json.dumps(document), encoding="utf-8")
    return path


class TheRecordedAnswerer(unittest.TestCase):
    def test_it_replays_the_exact_question_and_names_itself_by_the_file(self) -> None:
        recorded = RecordedAnswerer(replies_file())
        self.assertEqual(recorded.name, "claude-test")
        self.assertEqual(recorded.set_sha256, "ab" * 32)
        self.assertEqual(recorded.find("Where is the Voc?", GOOD.passages), Finding((VOLTAGE,), "Voc must be lower.", 3.5))

    def test_a_question_not_recorded_gets_i_do_not_know(self) -> None:
        recorded = RecordedAnswerer(replies_file())
        self.assertEqual(recorded.find("where is the voc?", GOOD.passages), Finding())

    def test_through_the_door_it_gives_an_answer_with_its_sources(self) -> None:
        reply = answer("Where is the Voc?", (GOOD,), False, RecordedAnswerer(replies_file()))
        self.assertEqual((reply.kind, reply.passage_refs), (ReplyKind.ANSWER, (VOLTAGE,)))

    def test_a_replies_file_that_is_missing_or_malformed_is_refused(self) -> None:
        with self.assertRaisesRegex(ValueError, "not a replies file"):
            RecordedAnswerer(scratch() / "none.json")
        with self.assertRaisesRegex(ValueError, "not a replies file"):
            RecordedAnswerer(replies_file({"version": 2}))
        with self.assertRaisesRegex(ValueError, "not a replies file"):
            RecordedAnswerer(replies_file({"replies": {"q": {"refs": [["good", "voltage"]], "text": ""}}}))
        with self.assertRaisesRegex(ValueError, "not a replies file"):
            RecordedAnswerer(replies_file({"answerer": None, "replies": []}))


if __name__ == "__main__":
    unittest.main()
