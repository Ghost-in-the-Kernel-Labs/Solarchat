"""The bank run's deterministic half: the sample, the ledger line and window, the door-fault cross-check (TODO 1.20; SC-023).

Fake interrogator, bot and grader throughout; no model is called and no key is read."""
import contextlib
import io
import json
import unittest

from scripts import bank_run
from solarchat.leaf.contract import SAFETY_RESPONSES, PassageRef, Reply, ReplyKind
from solarchat.packs.load import load_pack
from solarchat.safety.rules import load_rules, rules_fired
from test.support import ROOT, scratch

PACK = load_pack(ROOT / "packs" / "seed-mc4-leads")
BANK = bank_run.load_bank()


def rule(number: int, severity: str = "core", family: str = "ask", status: str = "active") -> dict:
    """A bank rule with only the fields the sample reads: rule(7)["id"] gives "BR-0007"."""
    return {"id": f"BR-{number:04d}", "family": family, "severity": severity, "status": status,
            "behaviour": "x", "turns": ["Hello?", "Yes."]}


def run_line(results: dict[str, list[str]], run: str = "R-1") -> dict:
    """A ledger line holding these results, the other fields as a fake run's."""
    meta = {name: "x" for name in bank_run.LINE_FIELDS if name not in bank_run.DERIVED_FIELDS}
    meta.update(run=run, packs=[{"id": "seed-mc4-leads", "version": "0.1"}], agreement=0.9, door_faults=[], tokens={}, cost=0.08,
                canaries={"graded": 4, "wrong": []})
    families = [rule(n) for n in range(1, 60)]
    return bank_run.ledger_line(meta, results, families)


class TheSample(unittest.TestCase):
    def test_the_same_bank_ledger_and_seed_give_the_same_rule_ids(self) -> None:
        ledger = [run_line({"BR-0001": ["no", "x"], "BR-0002": ["yes", "x"]})]
        first = bank_run.sample(BANK, ledger, 17, 8)
        self.assertEqual(first, bank_run.sample(BANK, ledger, 17, 8))
        self.assertEqual(len(first), 8)
        self.assertEqual(len(set(first)), 8)

    def test_another_seed_gives_another_sample(self) -> None:
        self.assertNotEqual(bank_run.sample(BANK, [], 1, 8), bank_run.sample(BANK, [], 2, 8))

    def test_the_ledger_changes_the_sample(self) -> None:
        ledger = [run_line({rule_id: ["no", "x"] for rule_id in ("BR-0001", "BR-0002", "BR-0003")})]
        self.assertNotEqual(bank_run.sample(BANK, [], 3, 8), bank_run.sample(BANK, ledger, 3, 8))

    def test_the_weights(self) -> None:
        core, safety, manner = rule(1), rule(2, "safety"), rule(3, "manner")
        self.assertEqual(bank_run.weight(core, []), 3.0)
        self.assertEqual(bank_run.weight(safety, []), 6.0)
        self.assertEqual(bank_run.weight(manner, []), 2.0)
        self.assertEqual(bank_run.weight(core, ["yes"]), 1.5)
        self.assertEqual(bank_run.weight(core, ["no", "yes"]), 3.0)
        self.assertEqual(bank_run.weight(safety, ["no"]), 9.0)

    def test_only_the_last_five_samplings_count_and_an_unclear_is_no_failure(self) -> None:
        core = rule(1)
        self.assertEqual(bank_run.weight(core, ["no"] * 3 + ["yes"] * 5), 1.5)
        self.assertEqual(bank_run.weight(core, ["unclear", "yes"]), 1.5)
        self.assertEqual(bank_run.weight(core, ["yes", "no", "no", "no", "no", "no"]), 4.5)

    def test_a_rule_never_sampled_weighs_double_a_rule_that_passed(self) -> None:
        self.assertEqual(bank_run.weight(rule(1), []), 2 * bank_run.weight(rule(1), ["yes"]))

    def test_a_quarter_of_the_sample_is_safety_when_the_bank_has_them(self) -> None:
        rules = [rule(n) for n in range(1, 41)] + [rule(n, "safety", "safety") for n in range(41, 61)]
        for seed in range(5):
            chosen = bank_run.sample(rules, [], seed, 40)
            self.assertEqual(len(chosen), 40)
            self.assertGreaterEqual(sum(each > "BR-0040" for each in chosen[:10]), 10)
            self.assertEqual(chosen[:10], [each for each in chosen[:10] if each > "BR-0040"])

    def test_a_bank_with_few_safety_rules_gives_all_it_has_first(self) -> None:
        rules = [rule(n) for n in range(1, 31)] + [rule(31, "safety", "safety"), rule(32, "safety", "safety")]
        chosen = bank_run.sample(rules, [], 4, 40)
        self.assertEqual(sorted(chosen[:2]), ["BR-0031", "BR-0032"])
        self.assertEqual(len(chosen), 32)

    def test_a_sample_beyond_the_bank_is_the_whole_bank_and_retired_rules_are_never_drawn(self) -> None:
        rules = [rule(1), rule(2, status="retired"), rule(3)]
        self.assertEqual(sorted(bank_run.sample(rules, [], 9, 40)), ["BR-0001", "BR-0003"])

    def test_a_family_filter_keeps_to_those_families(self) -> None:
        chosen = bank_run.sample(BANK, [], 5, 40, ("pace",))
        self.assertEqual(sorted(chosen), ["BR-0006", "BR-0007", "BR-0008", "BR-0009"])

    def test_the_real_bank_samples_whole_at_forty(self) -> None:
        chosen = bank_run.sample(BANK, [], 1)
        self.assertEqual(sorted(chosen), sorted(each["id"] for each in BANK if each["status"] == "active"))
        self.assertEqual(len(chosen), 20)

    def test_a_rule_that_failed_is_drawn_first_more_often(self) -> None:
        rules = [rule(1), rule(2)]
        ledger = [run_line({"BR-0001": ["no", "x"], "BR-0002": ["yes", "x"]})]
        firsts = [bank_run.sample(rules, ledger, seed, 1)[0] for seed in range(300)]
        self.assertGreater(firsts.count("BR-0001"), 1.5 * firsts.count("BR-0002"))


class TheLedger(unittest.TestCase):
    def test_a_line_has_every_field_of_the_design_and_its_tallies(self) -> None:
        results = {"BR-0001": ["no", "asked nothing"], "BR-0002": ["yes", "ok"], "BR-0003": ["unclear", "hm"]}
        line = run_line(results)
        self.assertEqual(set(line), set(bank_run.LINE_FIELDS))
        self.assertEqual(line["by_family"], {"ask": {"yes": 1, "no": 1, "unclear": 1}})
        self.assertEqual(line["by_severity"], {"core": {"yes": 1, "no": 1, "unclear": 1}})

    def test_a_missing_or_unknown_field_is_refused(self) -> None:
        with self.assertRaisesRegex(ValueError, "seed"):
            bank_run.ledger_line({"run": "R-1"}, {}, [])
        meta = {name: "x" for name in bank_run.LINE_FIELDS if name not in bank_run.DERIVED_FIELDS}
        with self.assertRaisesRegex(ValueError, "extra"):
            bank_run.ledger_line(dict(meta, extra=1), {}, [])

    def test_an_unknown_rule_or_verdict_is_refused(self) -> None:
        meta = {name: "x" for name in bank_run.LINE_FIELDS if name not in bank_run.DERIVED_FIELDS}
        with self.assertRaisesRegex(ValueError, "BR-9999"):
            bank_run.ledger_line(meta, {"BR-9999": ["yes", "x"]}, [rule(1)])
        with self.assertRaisesRegex(ValueError, "BR-0001"):
            bank_run.ledger_line(meta, {"BR-0001": ["maybe", "x"]}, [rule(1)])

    def test_one_line_is_appended_per_run(self) -> None:
        path = scratch() / "ledger.jsonl"
        self.assertEqual(bank_run.read_ledger(path), [])
        self.assertEqual(bank_run.append_ledger(path, run_line({"BR-0001": ["yes", "x"]}, "R-1")), 1)
        self.assertEqual(bank_run.append_ledger(path, run_line({"BR-0002": ["no", "y"]}, "R-2")), 2)
        text = path.read_text(encoding="utf-8")
        self.assertEqual(len(text.splitlines()), 2)
        self.assertTrue(text.endswith("\n"))
        self.assertEqual([line["run"] for line in bank_run.read_ledger(path)], ["R-1", "R-2"])
        self.assertEqual(json.loads(text.splitlines()[0])["results"], {"BR-0001": ["yes", "x"]})

    def test_the_window_keeps_the_last_sixty_runs(self) -> None:
        path = scratch() / "ledger.jsonl"
        for number in range(1, 66):
            bank_run.append_ledger(path, run_line({"BR-0001": ["yes", "x"]}, f"R-{number:02d}"))
        runs = [line["run"] for line in bank_run.read_ledger(path)]
        self.assertEqual(len(runs), 60)
        self.assertEqual((runs[0], runs[-1]), ("R-06", "R-65"))

    def test_the_history_runs_oldest_first_and_skips_runs_that_did_not_sample_a_rule(self) -> None:
        ledger = [run_line({"BR-0001": ["no", "x"]}, "R-1"), run_line({"BR-0002": ["yes", "x"]}, "R-2"),
                  run_line({"BR-0001": ["yes", "x"]}, "R-3")]
        self.assertEqual(bank_run.verdict_history(ledger), {"BR-0001": ["no", "yes"], "BR-0002": ["yes"]})

    def test_a_missing_ledger_reads_as_empty(self) -> None:
        self.assertEqual(bank_run.read_ledger(scratch() / "none.jsonl"), [])


def fake_replay_stop(words: str, packs: tuple, demo_mode: bool) -> Reply:
    """A replay in which the door's fixed rules fire SR-09's emergency on the words "shock" (what TODO 1.10 will do)."""
    if "shock" in words:
        return Reply(ReplyKind.STOP, "Step back and call for help.", (), "SR-09")
    return bank_run.replay_reply(words, packs, demo_mode)


class TheDoorFault(unittest.TestCase):
    def test_a_live_reply_that_carries_the_rule_is_no_fault(self) -> None:
        live = Reply(ReplyKind.STOP, "Step back and call for help.", (), "SR-09")
        self.assertEqual(bank_run.door_faults([("I got a shock", live)], (PACK,), True, fake_replay_stop), [])

    def test_a_planted_fake_reply_without_the_rule_is_a_fault_and_exits_1(self) -> None:
        fake = Reply(ReplyKind.DO_NOT_KNOW, "I do not know.")
        faults = bank_run.door_faults([("What is Voc?", fake), ("I got a shock", fake)], (PACK,), True, fake_replay_stop)
        self.assertEqual(faults, [bank_run.Fault("SR-09", "I got a shock")])
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(bank_run.report_faults(faults), 1)
        self.assertEqual(out.getvalue(), 'DOOR FAULT SR-09 on "I got a shock"\n')

    def test_another_rule_in_the_live_reply_is_a_fault(self) -> None:
        other = Reply(ReplyKind.STOP, "Stop.", (), "SR-02")
        self.assertEqual(len(bank_run.door_faults([("I got a shock", other)], (PACK,), True, fake_replay_stop)), 1)

    def test_no_fault_exits_0_and_prints_nothing(self) -> None:
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(bank_run.report_faults([]), 0)
        self.assertEqual(out.getvalue(), "")

    def test_a_rule_fired_by_a_cited_passage_in_the_live_reply_is_no_fault(self) -> None:
        live = Reply(ReplyKind.WARN, "Careful.", (PassageRef("seed-mc4-leads", "step-12"),), "SR-03")
        self.assertEqual(bank_run.door_faults([("How do I part the connectors?", live)], (PACK,), True), [])

    def test_with_no_answer_a_trigger_in_the_workers_words_fires_its_rule_so_the_door_fault_check_is_live(self) -> None:
        """TODO 1.10 ended "no trigger fires with NoAnswer": the door reads the worker's words, so a trigger of a words-read
        rule or of a stop rule gives that rule's stop or emergency with no passage; a warn rule's words come before an "I do
        not know" (a warn must name a passage, HAD-03)."""
        by_id = {each.rule_id: each for each in load_rules()}
        for each in load_rules():
            for trigger in each.triggers:
                with self.subTest(rule=each.rule_id, trigger=trigger):
                    words = f"I need to {trigger}"
                    reply = bank_run.replay_reply(words, (PACK,), True)
                    fired = [by_id[rule_id] for rule_id in rules_fired(words, load_rules())]
                    worst = min(fired, key=lambda hit: (-SAFETY_RESPONSES.index(hit.response), hit.rule_id))
                    if worst.response == "warn":
                        self.assertIs(reply.kind, ReplyKind.DO_NOT_KNOW)
                        self.assertIsNone(reply.safety_rule_id)
                        self.assertIn(worst.words_shown, reply.text)
                    else:
                        self.assertIs(reply.kind, ReplyKind.STOP)
                        self.assertEqual(reply.safety_rule_id, worst.rule_id)
                    if each.reads == "words" or each.response == "stop":
                        self.assertIn(each.rule_id, [hit.rule_id for hit in fired])
                        self.assertIs(reply.kind, ReplyKind.STOP)

    def test_a_rule_fired_only_by_a_passage_never_fires_with_no_answer(self) -> None:
        """NoAnswer cites nothing, so a passage's text fires no rule: every passage of the seed pack, replayed under a
        question that fires nothing, is "I do not know"."""
        for passage in PACK.passages:
            with self.subTest(passage=passage.ref.passage_id):
                self.assertEqual(rules_fired("Where do I start?", load_rules()), [])
                reply = bank_run.replay_reply("Where do I start?", (PACK,), True)
                self.assertIsNone(reply.safety_rule_id)
                self.assertIs(reply.kind, ReplyKind.DO_NOT_KNOW)
        self.assertTrue(any(rules_fired(passage.text, load_rules()) for passage in PACK.passages))


class ThePlay(unittest.TestCase):
    def test_a_rule_is_played_for_exactly_its_turns_with_fake_parts(self) -> None:
        seen: list[tuple[str, int]] = []

        def interrogator(each: dict, transcript: list) -> str:
            """The next turn of the rule: interrogator(rule(1), []) gives "Hello?"."""
            return each["turns"][len(transcript) // 2]

        def bot(words: str, history: tuple) -> Reply:
            """A bot that records what it was given and knows nothing: bot("Hi", ()).kind is DO_NOT_KNOW."""
            seen.append((words, len(history)))
            return Reply(ReplyKind.DO_NOT_KNOW, "I do not know.")

        exchanges = bank_run.play(rule(1), interrogator, bot)
        self.assertEqual([words for words, _ in exchanges], ["Hello?", "Yes."])
        self.assertEqual(seen, [("Hello?", 0), ("Yes.", 2)])

    def test_a_whole_run_with_fake_parts_builds_a_ledger_line_and_finds_the_fault(self) -> None:
        ids = bank_run.sample(BANK, [], 1, 4)
        by_id = {each["id"]: each for each in BANK}
        fake = Reply(ReplyKind.DO_NOT_KNOW, "I do not know.")
        exchanges = [pair for rule_id in ids for pair in bank_run.play(by_id[rule_id], lambda each, transcript: "I got a shock", lambda w, h: fake)]
        faults = bank_run.door_faults(exchanges, (PACK,), True, fake_replay_stop)
        self.assertEqual(len(faults), len(exchanges))
        results = {rule_id: ["yes" if number % 2 else "no", "fake grader"] for number, rule_id in enumerate(ids)}
        meta = {name: "x" for name in bank_run.LINE_FIELDS if name not in bank_run.DERIVED_FIELDS}
        line = bank_run.ledger_line(dict(meta, door_faults=[each.rule for each in faults]), results, BANK)
        self.assertEqual(sorted(line["results"]), sorted(ids))


if __name__ == "__main__":
    unittest.main()
