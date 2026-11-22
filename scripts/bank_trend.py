"""Writes docs/BANK-TREND.md, the rule bank's trend as Ghost reads it, from the ledger and the bank (TODO 1.20; SC-023).

The page is generated from `evals/bank/ledger.jsonl` and `evals/bank/<family>.json` (design 5.2): each family over its last
ten runs with what changed beside each run, the watch list by 5.3's signal rule, the grader's agreement, and the cost. It
has no date of its own, so it changes only when the ledger or the bank does. A trend is read, never a gate.

Run: python3 -I scripts/bank_trend.py          (writes the page)
     python3 -I scripts/bank_trend.py --check  (exit 1 when the page is stale; test/test_bank_trend.py runs it in the fast loop)
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if __name__ == "__main__":  # run as a script from the project's root: the root holds the scripts and solarchat packages
    sys.path.insert(0, str(ROOT))
from scripts.bank_run import LAST_SAMPLINGS, LEDGER_PATH, WINDOW, load_bank, read_ledger  # noqa: E402
from scripts.checks.bank import BANK_FOLDER  # noqa: E402

PAGE_PATH = ROOT / "docs" / "BANK-TREND.md"
SHOWN_RUNS = 10
SIGNAL_FAILURES = {"safety": 2, "core": 3, "manner": 3}
AGREEMENT_FLOOR = 0.85
AGREEMENT_RUNS = 3

HEADER = (
    "# The rule bank's trend\n\n"
    "Written by `scripts/bank_trend.py` from `evals/bank/ledger.jsonl` and the bank; do not edit here: run the script. "
    "`scripts/bank_trend.py --check` is in the fast loop and fails when this page is stale.\n\n"
    "A trend is a light the plant grows towards, never a gate (SC-023): no rule fails a run, a signal is acted on by "
    "triage, and the one red is a door fault. One failure is noise. A rule is a **signal** when it failed in at least three "
    "of its last five samplings, in two of its last five for a `safety` rule (design 5.3). The check model's agreement with "
    "one of those failures is part of 5.3 and is not yet in the ledger's line (design 5.1), so the watch list below is by "
    "the failure count alone.\n\n"
)


def cell(text: object) -> str:
    """A table cell's text on one line with no bar: cell("a | b") gives "a / b"."""
    return " ".join(str(text).split()).replace("|", "/")


def table(heads: tuple[str, ...], rows: list[tuple[object, ...]]) -> str:
    """A Markdown table, the heads then one line per row: table(("A",), [("x",)]) is "| A |\\n| --- |\\n| x |\\n"."""
    lines = ["| " + " | ".join(heads) + " |", "| " + " | ".join("---" for _ in heads) + " |"]
    lines += ["| " + " | ".join(cell(each) for each in row) + " |" for row in rows]
    return "\n".join(lines) + "\n"


def changes(line: dict, before: dict | None) -> str:
    """What changed from the run before to this one, named: "prompt changed", "grader changed", "bot model <model>" and each
    pack whose version is new as "<pack> <version>", joined by ", "; "-" for the first run and for no change."""
    if before is None:
        return "-"
    found = []
    if line["prompt_sha256"] != before["prompt_sha256"]:
        found.append("prompt changed")
    if line["grader_sha256"] != before["grader_sha256"]:
        found.append("grader changed")
    if line["bot_model"] != before["bot_model"]:
        found.append(f"bot model {line['bot_model']}")
    found += [f"{pack['id']} {pack['version']}" for pack in line["packs"] if pack not in before["packs"]]
    return ", ".join(found) or "-"


def pass_share(counts: dict[str, int]) -> float | None:
    """The share of yes among yes and no, an unclear counted apart: {"yes": 3, "no": 1, "unclear": 5} gives 0.75; None
    when nothing was a yes or a no."""
    graded = counts["yes"] + counts["no"]
    return counts["yes"] / graded if graded else None


def percent(share: float | None) -> str:
    """A share as a whole percent: percent(0.75) is "75%"; None is "-"."""
    return "-" if share is None else f"{round(share * 100)}%"


def family_section(family: str, ledger: list[dict]) -> str:
    """One family: its last ten runs that sampled it, oldest first, with the pass share, the number graded and what changed
    in that run, then the mean of the last five of them."""
    rows, shares = [], []
    for index, line in enumerate(ledger):
        counts = line["by_family"].get(family)
        if counts:
            share = pass_share(counts)
            shares.append(share)
            rows.append((line["run"], percent(share), sum(counts.values()), changes(line, ledger[index - 1] if index else None)))
    rows, shares = rows[-SHOWN_RUNS:], [share for share in shares if share is not None][-LAST_SAMPLINGS:]
    mean = f"Mean of the last {min(LAST_SAMPLINGS, len(shares))}: {percent(sum(shares) / len(shares))}" if shares else "Not sampled yet."
    body = table(("Run", "Pass", "Graded", "Changed"), rows) + "\n" if rows else ""
    return f"### {family}\n\n{body}{mean}\n\n"


def history_of(ledger: list[dict]) -> dict[str, list[tuple[str, str, str]]]:
    """Each rule's samplings across the ledger as (run, verdict, reason), oldest first."""
    history: dict[str, list[tuple[str, str, str]]] = {}
    for line in ledger:
        for rule_id, (verdict, reason) in line["results"].items():
            history.setdefault(rule_id, []).append((line["run"], verdict, reason))
    return history


# Decision: SC-023 (design 5.3: three failures in the last five samplings, two for a safety rule; one failure is noise)
def signals(ledger: list[dict], rules: list[dict]) -> list[str]:
    """The ids of the rules that are a signal, most severe first and then by id: a safety rule with two "no" in its last
    five samplings, any other rule with three. A rule with fewer samplings is judged on the ones it has."""
    severity = {rule["id"]: rule["severity"] for rule in rules}
    found = [rule_id for rule_id, samplings in history_of(ledger).items()
             if [verdict for _, verdict, _ in samplings[-LAST_SAMPLINGS:]].count("no") >= SIGNAL_FAILURES[severity.get(rule_id, "core")]]
    order = list(SIGNAL_FAILURES)
    return sorted(found, key=lambda rule_id: (order.index(severity.get(rule_id, "core")), rule_id))


def watch_section(ledger: list[dict], rules: list[dict]) -> str:
    """The watch list: each signal with its last five verdicts, reasons and runs, then each rule that was a signal at the
    run before the last and is not now."""
    by_id = {rule["id"]: rule for rule in rules}
    history = history_of(ledger)
    now = signals(ledger, rules)
    rows = [(rule_id, by_id.get(rule_id, {}).get("severity", "core"), by_id.get(rule_id, {}).get("behaviour", "-"),
             "; ".join(f"{run}: {verdict}, {reason}" for run, verdict, reason in history[rule_id][-LAST_SAMPLINGS:]))
            for rule_id in now]
    text = table(("Rule", "Severity", "Behaviour", "Last five (run: verdict, reason)"), rows) if rows else "No rule is a signal.\n"
    left = [rule_id for rule_id in signals(ledger[:-1], rules) if rule_id not in now]
    return text + "\n" + ("Left the list since the previous page: " + ", ".join(left) + ".\n" if left else "None left the list since the previous page.\n")


def grader_section(ledger: list[dict]) -> str:
    """The grader: per run the agreement with the check model, the canaries graded wrong and the `unclear` verdicts; marked
    unreliable when the mean agreement of the last three runs is below the floor of 0.85 (design 4.3)."""
    rows = []
    for line in ledger[-SHOWN_RUNS:]:
        agreement = line["agreement"]
        unclear = sum(counts["unclear"] for counts in line["by_family"].values())
        rows.append((line["run"], "-" if agreement is None else f"{agreement:.2f}", len(line["canaries"]["wrong"]), unclear))
    text = table(("Run", "Agreement", "Canaries missed", "Unclear"), rows) if rows else "No run yet.\n"
    last = [line["agreement"] for line in ledger[-AGREEMENT_RUNS:] if line["agreement"] is not None]
    if len(last) == AGREEMENT_RUNS and sum(last) / AGREEMENT_RUNS < AGREEMENT_FLOOR:
        text += (f"\n**The grader is unreliable:** agreement over the last {AGREEMENT_RUNS} runs is {sum(last) / AGREEMENT_RUNS:.2f}, "
                 f"below {AGREEMENT_FLOOR}. The fix is a clearer question, never a verdict trusted anyway. Which rules the "
                 f"check model disagreed on is not yet in the ledger's line.\n")
    return text


def cost_section(ledger: list[dict]) -> str:
    """The cost: per run, and the month so far, the month of the latest run (the page has no clock of its own)."""
    if not ledger:
        return "No run yet.\n"
    rows = [(line["run"], line["date"], f"${line['cost']:.3f}") for line in ledger[-SHOWN_RUNS:]]
    month = ledger[-1]["date"][:7]
    in_month = [line["cost"] for line in ledger if line["date"][:7] == month]
    return table(("Run", "Date", "Cost"), rows) + f"\nThe month so far ({month}): ${sum(in_month):.3f} over {len(in_month)} runs.\n"


def render(ledger: list[dict], rules: list[dict]) -> str:
    """The page's text: the header, how many runs the ledger holds, then the four sections of the module docstring."""
    families = sorted({rule["family"] for rule in rules})
    held = (f"The ledger holds {len(ledger)} runs (a window of {WINDOW}); the latest is {ledger[-1]['run']} on {ledger[-1]['date']}.\n\n"
            if ledger else f"No run has been recorded yet; the ledger keeps a window of the last {WINDOW} runs, and the first live run is by hand.\n\n")
    return (HEADER + held + "## The families\n\n" + "".join(family_section(family, ledger) for family in families)
            + "## The watch list\n\n" + watch_section(ledger, rules) + "\n## The grader\n\n" + grader_section(ledger)
            + "\n## The cost\n\n" + cost_section(ledger))


def main(arguments: list[str], ledger_path: Path = LEDGER_PATH, bank_folder: Path = BANK_FOLDER, page_path: Path = PAGE_PATH) -> int:
    """Writes the page, or with --check compares it: 0 when current, 1 when stale or missing, 2 for an unknown argument."""
    if any(argument != "--check" for argument in arguments):
        print("usage: scripts/bank_trend.py [--check]", file=sys.stderr)
        return 2
    wanted = render(read_ledger(ledger_path), load_bank(bank_folder))
    if arguments:
        is_current = page_path.exists() and page_path.read_text(encoding="utf-8") == wanted
        print("BANK-TREND.md is current" if is_current else "BANK-TREND.md is stale: run scripts/bank_trend.py")
        return 0 if is_current else 1
    page_path.write_text(wanted, encoding="utf-8")
    print(f"wrote {page_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
