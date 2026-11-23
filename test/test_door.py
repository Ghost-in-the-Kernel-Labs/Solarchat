"""The answering door's order of operations, each step on its own, and the two answerers that need no model (TODO 1.6; SC-019, HAD-03, HAD-06)."""
import json
import unittest
from dataclasses import replace
from pathlib import Path

from solarchat.answer.door import DO_NOT_KNOW_TEXT, NO_PACK_TEXT, answer
from solarchat.answer.recorded import RecordedAnswerer
from solarchat.answer.stub import NoAnswer
from solarchat.leaf.contract import DEFAULT_PROFILE, DEMO_BANNER, Finding, Passage, PassageRef, Profile, Reply, ReplyKind, Turn
from solarchat.packs.load import Pack, load_pack
from solarchat.safety.rules import load_rules
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
        self.histories: list[tuple[Turn, ...]] = []

    def find(self, question: str, passages: tuple[Passage, ...], history: tuple[Turn, ...] = ()) -> Finding:
        """Record the call and return the fixed finding: Spy(Finding()).find("q", ()) gives Finding()."""
        self.asked.append((question, passages))
        self.histories.append(history)
        return self.finding


class Raising:
    """An answerer that breaks: Raising().find("q", ()) raises RuntimeError."""

    name = "raising"

    def find(self, question: str, passages: tuple[Passage, ...], history: tuple[Turn, ...] = ()) -> Finding:
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
        self.assertEqual(len(spy.asked[0][1]), 91)
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


RULES = {rule.rule_id: rule for rule in load_rules()}


def planted(texts: tuple[str, ...]) -> Pack:
    """GOOD with one more passage per text of the tuple, planted-1, planted-2, ..., each titled "Planted n" and sourced as S1 page 1."""
    added = tuple(Passage(PassageRef("good", f"planted-{n}"), text, f"Planted {n}") for n, text in enumerate(texts, start=1))
    cited = {passage.ref.passage_id: [{"source": "S1", "page": "1"}] for passage in added}
    return replace(GOOD, passages=GOOD.passages + added, citations={**GOOD.citations, **cited})


def planted_ref(number: int) -> PassageRef:
    """The ref of planted-n: planted_ref(1) is PassageRef("good", "planted-1")."""
    return PassageRef("good", f"planted-{number}")


def trigger_of(rule_id: str) -> str:
    """The rule's first trigger, so a planted passage fires it by the rule's own data: trigger_of("SR-03")."""
    return RULES[rule_id].triggers[0]


class Step6TheSafetyRules(unittest.TestCase):
    def test_a_passage_that_fires_a_warn_rule_gives_a_warn_with_the_rules_words_and_the_answer(self) -> None:
        pack = planted((f"Be careful: {trigger_of('SR-03')}.",))
        reply = answer("How?", (pack,), False, Spy(Finding((planted_ref(1),), "Do it slowly.")), profile=signed_off(("connector",)))
        self.assertEqual((reply.kind, reply.safety_rule_id, reply.passage_refs), (ReplyKind.WARN, "SR-03", (planted_ref(1),)))
        self.assertEqual(reply.text, RULES["SR-03"].lowered_for[0].words + "\n\nDo it slowly.\n\n"
                         "From: Planted 1 (Connecting a panel to a power station): Examplesun ES-100 installation manual, page 1")

    def test_a_passage_that_fires_a_stop_rule_gives_a_stop_with_the_words_and_what_to_bring(self) -> None:
        pack = planted((f"Never ignore {trigger_of('SR-06')}.",))
        reply = answer("How?", (pack,), False, Spy(Finding((planted_ref(1),), "Carry on.")))
        self.assertEqual((reply.kind, reply.safety_rule_id, reply.passage_refs), (ReplyKind.STOP, "SR-06", ()))
        self.assertEqual(reply.text, RULES["SR-06"].words_shown + "\n\nWhat to bring your supervisor: rule SR-06; Planted 1, "
                         "Examplesun ES-100 installation manual, page 1")

    def test_a_passage_that_lists_an_emergency_sign_fires_nothing_but_the_question_that_reports_it_does(self) -> None:
        pack = planted((f"If you see {trigger_of('SR-08')}, leave.",))
        listed = answer("How?", (pack,), False, Spy(Finding((planted_ref(1),), "Carry on.")))
        self.assertEqual((listed.kind, listed.safety_rule_id), (ReplyKind.ANSWER, None))
        reply = answer(f"There is {trigger_of('SR-08')} here", (pack,), False, Spy(Finding((planted_ref(1),), "Carry on.")))
        self.assertEqual((reply.kind, reply.safety_rule_id, reply.passage_refs), (ReplyKind.STOP, "SR-08", ()))
        self.assertEqual(reply.text, RULES["SR-08"].words_shown)

    def test_the_rules_apply_whatever_the_answerer_said_in_its_finding(self) -> None:
        pack = planted((f"Never ignore {trigger_of('SR-06')}.",))
        reply = answer("How?", (pack,), False, Spy(Finding((planted_ref(1),), f"All fine, {trigger_of('SR-03')} is allowed.")))
        self.assertEqual(reply.safety_rule_id, "SR-06")
        self.assertNotIn("All fine", reply.text)

    def test_the_most_severe_response_wins_then_the_lowest_id(self) -> None:
        pack = planted((f"{trigger_of('SR-03')}", f"{trigger_of('SR-06')}", f"{trigger_of('SR-14')}", f"{trigger_of('SR-04')}",))
        refs = (planted_ref(1), planted_ref(2), planted_ref(3))
        self.assertEqual(answer(f"q {trigger_of('SR-08')}", (pack,), False, Spy(Finding(refs, "x"))).safety_rule_id, "SR-08")
        self.assertEqual(answer("q", (pack,), False, Spy(Finding(refs, "x"))).safety_rule_id, "SR-03")
        signed = signed_off(("connector",))
        self.assertEqual(answer("q", (pack,), False, Spy(Finding(refs, "x")), profile=signed).safety_rule_id, "SR-06")
        both = Finding((planted_ref(4), planted_ref(2)), "x")
        self.assertEqual(answer("q", (pack,), False, Spy(both)).safety_rule_id, "SR-04")

    def test_only_the_cited_passages_fire_never_one_that_was_given_and_not_cited(self) -> None:
        pack = planted((f"{trigger_of('SR-08')}",))
        reply = answer("How?", (pack,), False, Spy(Finding((VOLTAGE,), "Voc must be lower.")))
        self.assertEqual((reply.kind, reply.safety_rule_id), (ReplyKind.ANSWER, None))

    def test_the_question_fires_a_rule_even_when_a_passage_is_cited_and_says_nothing_of_it(self) -> None:
        reply = answer(f"I got {trigger_of('SR-08')}", (GOOD,), False, one(VOLTAGE))
        self.assertEqual((reply.kind, reply.safety_rule_id, reply.passage_refs), (ReplyKind.STOP, "SR-08", ()))

    def test_an_i_do_not_know_is_not_a_safety_reply(self) -> None:
        pack = planted((f"{trigger_of('SR-08')}",))
        reply = answer("How?", (pack,), False, NoAnswer())
        self.assertEqual((reply.kind, reply.safety_rule_id), (ReplyKind.DO_NOT_KNOW, None))

    def test_the_real_pack_step_12_warns_and_a_worker_who_sees_sparks_gets_an_emergency(self) -> None:
        step_12 = Spy(Finding((PassageRef("seed-mc4-leads", "step-12"),), "Use the tool."))
        warn = answer("How?", (SEED,), True, step_12, profile=signed_off(("connector",)))
        self.assertEqual((warn.kind, warn.safety_rule_id), (ReplyKind.WARN, "SR-03"))
        stopped = answer("How?", (SEED,), True, step_12)
        self.assertEqual((stopped.kind, stopped.safety_rule_id), (ReplyKind.STOP, "SR-03"))
        fail_04 = Finding((PassageRef("seed-mc4-leads", "fail-04-stop"),), "Stop.")
        stop = answer("I see sparks at the connector", (SEED,), True, Spy(fail_04))
        self.assertEqual((stop.kind, stop.safety_rule_id, stop.text.split("\n\n")[-1]), (ReplyKind.STOP, "SR-08", RULES["SR-08"].words_shown))

    def test_the_demo_banner_is_the_only_change_in_demo_mode(self) -> None:
        pack = planted((f"{trigger_of('SR-03')}",))
        plain = answer("q", (pack,), False, Spy(Finding((planted_ref(1),), "x")))
        banner = answer("q", (demo_copy(pack),), True, Spy(Finding((planted_ref(1),), "x")))
        self.assertEqual(banner.text, DEMO_BANNER + "\n\n" + plain.text)


LOWERINGS = (("SR-02", "meter", "stop"), ("SR-11", "battery", "stop"), ("SR-05", "height", "stop"), ("SR-03", "connector", "stop"))


def signed_off(names: tuple[str, ...] = (), role: str = "crew") -> Profile:
    """A profile of this role signed off for these: signed_off(("meter",)) is Profile("crew", frozenset({"meter"}))."""
    return Profile(role, frozenset(names))


class Step6TheProfile(unittest.TestCase):
    """SC-020: a fired rule lowers for the profile's sign-off, only as its own lowered_for says, before the most severe is chosen."""

    def reply(self, rule_id: str, profile: Profile | None = None) -> Reply:
        """The door's reply to a planted passage that fires the rule, cited by a fake finding, for the profile."""
        pack = planted((f"Be careful: {trigger_of(rule_id)}.",))
        spy = Spy(Finding((planted_ref(1),), "Do it slowly."))
        if profile is None:
            return answer("How?", (pack,), False, spy)
        return answer("How?", (pack,), False, spy, profile=profile)

    def test_each_of_the_three_rules_warns_with_the_lowered_words_for_its_sign_off(self) -> None:
        for rule_id, sign_off, _ in LOWERINGS:
            with self.subTest(rule=rule_id):
                reply = self.reply(rule_id, signed_off((sign_off,)))
                lowering = RULES[rule_id].lowered_for[0]
                self.assertEqual((reply.kind, reply.safety_rule_id, reply.passage_refs), (ReplyKind.WARN, rule_id, (planted_ref(1),)))
                self.assertEqual(reply.text, lowering.words + "\n\nDo it slowly.\n\n"
                                 "From: Planted 1 (Connecting a panel to a power station): Examplesun ES-100 installation manual, page 1")
                self.assertNotIn(RULES[rule_id].words_shown, reply.text)

    def test_without_the_sign_off_each_still_stops_as_before(self) -> None:
        others = {"SR-02": ("battery", "height", "connector"), "SR-11": ("meter", "height", "connector"),
                  "SR-05": ("meter", "battery", "connector"), "SR-03": ("meter", "battery", "height")}
        for rule_id, _, _ in LOWERINGS:
            for profile in (DEFAULT_PROFILE, signed_off(), signed_off(others[rule_id], role="qualified"), Profile("qualified", frozenset())):
                with self.subTest(rule=rule_id, profile=profile):
                    reply = self.reply(rule_id, profile)
                    self.assertEqual((reply.kind, reply.safety_rule_id, reply.passage_refs), (ReplyKind.STOP, rule_id, ()))
                    self.assertTrue(reply.text.startswith(RULES[rule_id].words_shown))

    def test_a_rule_not_in_the_table_never_lowers_for_any_profile(self) -> None:
        everything = Profile("qualified", frozenset({"meter", "connector", "battery", "height"}))
        for rule in load_rules():
            if rule.lowered_for or rule.reads == "words":  # a words-only rule fires on no passage, so no reply to compare
                continue
            with self.subTest(rule=rule.rule_id):
                self.assertEqual(self.reply(rule.rule_id, everything), self.reply(rule.rule_id))
                self.assertEqual(self.reply(rule.rule_id, everything).safety_rule_id, rule.rule_id)

    def test_the_default_profile_gives_exactly_the_reply_there_was_with_no_profile(self) -> None:
        for rule in load_rules():
            with self.subTest(rule=rule.rule_id):
                self.assertEqual(self.reply(rule.rule_id, DEFAULT_PROFILE), self.reply(rule.rule_id))

    def test_a_lowered_rule_is_chosen_among_the_others_by_its_lowered_response(self) -> None:
        pack = planted((trigger_of("SR-02"), trigger_of("SR-03")))
        both = Finding((planted_ref(1), planted_ref(2)), "x")
        self.assertEqual(answer("q", (pack,), False, Spy(both), profile=signed_off(("meter", "connector"))).safety_rule_id, "SR-02")
        self.assertEqual(answer("q", (pack,), False, Spy(both), profile=signed_off(("meter",))).safety_rule_id, "SR-03")
        pack = planted((trigger_of("SR-02"), trigger_of("SR-06")))
        self.assertEqual(answer("q", (pack,), False, Spy(both), profile=signed_off(("meter",))).safety_rule_id, "SR-06")
        self.assertEqual(answer("q", (pack,), False, Spy(both)).safety_rule_id, "SR-02")

    def test_a_lowered_rule_does_not_hide_another_that_still_stops(self) -> None:
        pack = planted((f"{trigger_of('SR-11')} and {trigger_of('SR-06')}",))
        reply = answer("q", (pack,), False, Spy(Finding((planted_ref(1),), "x")), profile=signed_off(("battery",), role="qualified"))
        self.assertEqual((reply.kind, reply.safety_rule_id), (ReplyKind.STOP, "SR-06"))

    def test_the_demo_banner_is_still_the_only_change_in_demo_mode_for_a_lowered_warn(self) -> None:
        pack = planted((trigger_of("SR-02"),))
        profile = signed_off(("meter",))
        plain = answer("q", (pack,), False, Spy(Finding((planted_ref(1),), "x")), profile=profile)
        banner = answer("q", (demo_copy(pack),), True, Spy(Finding((planted_ref(1),), "x")), profile=profile)
        self.assertEqual(banner.text, DEMO_BANNER + "\n\n" + plain.text)


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


class TheHistory(unittest.TestCase):
    """The conversation's turns reach the answerer unchanged and change nothing else in the door (SC-019, amended 2026-11-21)."""

    def test_the_history_is_passed_through_to_the_answerer_unchanged(self) -> None:
        spy = one(VOLTAGE)
        turns = (Turn("user", "Hi"), Turn("assistant", "Which device?"))
        answer("The inverter.", (GOOD,), False, spy, turns)
        self.assertEqual(spy.histories, [turns])

    def test_with_no_history_the_answerer_is_given_an_empty_one(self) -> None:
        spy = one(VOLTAGE)
        answer("Where is the Voc?", (GOOD,), False, spy)
        self.assertEqual(spy.histories, [()])

    def test_the_history_does_not_change_the_reply(self) -> None:
        turns = (Turn("user", "Hi"), Turn("assistant", "Hello"))
        self.assertEqual(answer("q", (GOOD,), False, one(VOLTAGE), turns), answer("q", (GOOD,), False, one(VOLTAGE)))

    def test_the_offline_answerers_ignore_the_history(self) -> None:
        turns = (Turn("user", "Hi"),)
        self.assertEqual(NoAnswer().find("q", GOOD.passages, turns), Finding())
        self.assertEqual(RecordedAnswerer(replies_file()).find("Where is the Voc?", GOOD.passages, turns).refs, (VOLTAGE,))

    def test_a_turn_has_a_user_or_an_assistant_role_only(self) -> None:
        self.assertEqual(Turn("user", "x").role, "user")
        with self.assertRaises(ValueError):
            Turn("system", "x")


if __name__ == "__main__":
    unittest.main()
