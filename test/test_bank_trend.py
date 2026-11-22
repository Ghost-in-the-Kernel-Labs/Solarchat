"""The bank's trend page: what it shows from a fake ledger, the signal rule, and that a stale page fails (TODO 1.20; SC-023).

`test_the_page_is_current` is how `--check` joins the fast loop."""
import contextlib
import io
import unittest

from scripts import bank_run, bank_trend
from test.support import ROOT, scratch

BANK = bank_run.load_bank()
SAFETY, CORE = "BR-0010", "BR-0001"


def line(run: str, results: dict[str, list[str]], changes: dict | None = None) -> dict:
    """A ledger line for the real bank with these results; `changes` replaces fields: line("R-1", {})["cost"] gives 0.08."""
    meta = {name: "x" for name in bank_run.LINE_FIELDS if name not in bank_run.DERIVED_FIELDS}
    meta.update(run=run, date="2026-12-01", packs=[{"id": "seed-mc4-leads", "version": "0.1"}], agreement=0.9, door_faults=[],
                tokens={}, cost=0.08, canaries={"graded": 4, "wrong": []})
    return bank_run.ledger_line(dict(meta, **(changes or {})), results, BANK)


def failing(count: int, rule_id: str = CORE) -> list[dict]:
    """`count` runs in which the rule failed: failing(2)[1]["run"] gives "R-2"."""
    return [line(f"R-{number}", {rule_id: ["no", f"reason {number}"]}) for number in range(1, count + 1)]


def check(ledger: list[dict], page: str | None) -> int:
    """`--check` against a scratch page holding `page` (none for no page) and a scratch ledger of these lines."""
    folder = scratch()
    (folder / "ledger.jsonl").write_text(bank_run.ledger_text(ledger), encoding="utf-8")
    if page is not None:
        (folder / "page.md").write_text(page, encoding="utf-8")
    with contextlib.redirect_stdout(io.StringIO()):
        return bank_trend.main(["--check"], folder / "ledger.jsonl", ROOT / "evals" / "bank", folder / "page.md")


class TheRealPage(unittest.TestCase):
    def test_the_page_is_current(self) -> None:
        self.assertEqual(bank_trend.main(["--check"]), 0, "run: python3 -I scripts/bank_trend.py")

    def test_the_page_says_it_is_generated_and_a_trend_is_no_gate(self) -> None:
        text = (ROOT / "docs" / "BANK-TREND.md").read_text(encoding="utf-8")
        self.assertIn("do not edit here", text)
        self.assertIn("never a gate", text)
        for family in ("ask", "pace", "safety", "track"):
            self.assertIn(f"### {family}", text)


class TheStalePage(unittest.TestCase):
    def test_a_page_matching_the_ledger_is_current(self) -> None:
        ledger = failing(3)
        self.assertEqual(check(ledger, bank_trend.render(ledger, BANK)), 0)

    def test_a_page_written_before_another_run_is_stale(self) -> None:
        old = failing(3)
        self.assertEqual(check(old + failing(4)[3:], bank_trend.render(old, BANK)), 1)

    def test_a_missing_page_is_stale_and_an_edited_one_too(self) -> None:
        ledger = failing(2)
        self.assertEqual(check(ledger, None), 1)
        self.assertEqual(check(ledger, bank_trend.render(ledger, BANK) + "edited\n"), 1)

    def test_write_then_check_agrees_and_an_unknown_argument_exits_2(self) -> None:
        folder = scratch()
        (folder / "ledger.jsonl").write_text(bank_run.ledger_text(failing(2)), encoding="utf-8")
        paths = (folder / "ledger.jsonl", ROOT / "evals" / "bank", folder / "page.md")
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(bank_trend.main([], *paths), 0)
            self.assertEqual(bank_trend.main(["--check"], *paths), 0)
            self.assertEqual(bank_trend.main(["--nope"], *paths), 2)


class TheSignal(unittest.TestCase):
    def test_one_failure_is_noise_and_three_of_five_is_a_signal_for_a_core_rule(self) -> None:
        self.assertEqual(bank_trend.signals(failing(2), BANK), [])
        self.assertEqual(bank_trend.signals(failing(3), BANK), [CORE])

    def test_a_safety_rule_signals_at_two_of_five(self) -> None:
        self.assertEqual(bank_trend.signals(failing(1, SAFETY), BANK), [])
        self.assertEqual(bank_trend.signals(failing(2, SAFETY), BANK), [SAFETY])

    def test_only_the_last_five_samplings_count(self) -> None:
        ledger = failing(3) + [line(f"R-{n}", {CORE: ["yes", "ok"]}) for n in range(4, 9)]
        self.assertEqual(bank_trend.signals(ledger, BANK), [])

    def test_the_most_severe_comes_first(self) -> None:
        ledger = [line(f"R-{n}", {CORE: ["no", "x"], SAFETY: ["no", "y"]}) for n in range(1, 4)]
        self.assertEqual(bank_trend.signals(ledger, BANK), [SAFETY, CORE])

    def test_the_watch_list_shows_the_last_verdicts_with_their_runs_and_names_a_rule_that_left(self) -> None:
        ledger = failing(3)
        text = bank_trend.watch_section(ledger, BANK)
        self.assertIn(f"| {CORE} | core |", text)
        self.assertIn("R-1: no, reason 1; R-2: no, reason 2; R-3: no, reason 3", text)
        self.assertIn("None left the list", text)
        ledger += [line(f"R-{n}", {CORE: ["yes", "ok"]}) for n in range(4, 7)]
        self.assertEqual(bank_trend.signals(ledger, BANK), [])
        self.assertIn(f"Left the list since the previous page: {CORE}.", bank_trend.watch_section(ledger, BANK))


class TheSections(unittest.TestCase):
    def test_a_family_shows_its_last_ten_runs_and_the_mean_of_the_last_five(self) -> None:
        ledger = [line(f"R-{n:02d}", {CORE: ["yes" if n > 8 else "no", "x"]}) for n in range(1, 13)]
        text = bank_trend.family_section("ask", ledger)
        self.assertNotIn("R-01", text)
        self.assertNotIn("R-02 ", text)
        self.assertIn("| R-03 | 0% | 1 | -", text)
        self.assertIn("| R-12 | 100% | 1 |", text)
        self.assertIn("Mean of the last 5: 80%", text)
        self.assertLess(text.index("R-03"), text.index("R-12"))

    def test_a_change_is_named_beside_the_run_it_began_in(self) -> None:
        ledger = [line("R-1", {CORE: ["yes", "x"]}), line("R-2", {CORE: ["yes", "x"]}, {"prompt_sha256": "y", "bot_model": "haiku-9",
                                                                     "packs": [{"id": "seed-mc4-leads", "version": "0.2"}], "grader_sha256": "z"})]
        text = bank_trend.family_section("ask", ledger)
        self.assertIn("| R-1 | 100% | 1 | - |", text)
        self.assertIn("prompt changed, grader changed, bot model haiku-9, seed-mc4-leads 0.2", text)

    def test_an_unclear_is_counted_apart(self) -> None:
        ledger = [line("R-1", {CORE: ["unclear", "x"], "BR-0002": ["yes", "x"]})]
        text = bank_trend.family_section("ask", ledger)
        self.assertIn("| R-1 | 100% | 2 |", text)
        self.assertIn("| R-1 | 0.90 | 0 | 1 |", bank_trend.grader_section(ledger))

    def test_the_grader_is_unreliable_below_the_floor_over_the_last_three_runs(self) -> None:
        good = [line(f"R-{n}", {}, {"agreement": 0.9}) for n in range(1, 4)]
        self.assertNotIn("unreliable", bank_trend.grader_section(good))
        bad = [line(f"R-{n}", {}, {"agreement": 0.8}) for n in range(1, 4)]
        self.assertIn("The grader is unreliable", bank_trend.grader_section(bad))
        self.assertNotIn("unreliable", bank_trend.grader_section(bad[:2]))

    def test_canaries_missed_and_a_missing_agreement_are_shown(self) -> None:
        ledger = [line("R-1", {}, {"agreement": None, "canaries": {"graded": 4, "wrong": ["C-2"]}})]
        self.assertIn("| R-1 | - | 1 | 0 |", bank_trend.grader_section(ledger))

    def test_the_cost_is_per_run_and_the_month_so_far_is_the_latest_runs_month(self) -> None:
        ledger = [line("R-1", {}, {"date": "2026-11-30", "cost": 0.5}), line("R-2", {}, {"date": "2026-12-01", "cost": 0.08}),
                  line("R-3", {}, {"date": "2026-12-02", "cost": 0.1})]
        text = bank_trend.cost_section(ledger)
        self.assertIn("| R-2 | 2026-12-01 | $0.080 |", text)
        self.assertIn("The month so far (2026-12): $0.180 over 2 runs.", text)

    def test_an_empty_ledger_says_no_run_yet(self) -> None:
        text = bank_trend.render([], BANK)
        self.assertIn("No run has been recorded yet", text)
        self.assertIn("No rule is a signal.", text)
        self.assertIn("Not sampled yet.", text)


if __name__ == "__main__":
    unittest.main()
