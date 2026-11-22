"""The evaluation record, its ratchet and the printing of a run (TODO 1.6; SC-003, SC-019).

The record, `evals/results/offline.json`, is byte-stable (no date, no duration); `--write` refuses a fall no decision
names; `--check` compares a run with it. The design is `docs/designs/answering-door.md` 6.3, 6.4 and 6.7.
"""
import argparse
import json
import re
from pathlib import Path

from scripts.eval_core import CLASSES, ROOT, SAFETY_CLASSES, CannotRun, Result, Run, class_scores, display, sha_of
from solarchat.leaf.contract import MAX_CITED_PASSAGES
from solarchat.safety.rules import RULES_PATH

SAFETY_ACCEPT = re.compile(r"^SC-\d{3}$")
ACCURACY_ACCEPT = re.compile(r"^(SC|J)-\d{3}$")
RESULTS_FOLDER = ROOT / "evals" / "results"


def known_note(run_known: dict[str, dict], case_id: str) -> str:
    """The words for a known failure: "<why>, until <until>"; known_note({"a": {"why": "w", "until": "u"}}, "a") gives
    "w, until u"."""
    return f"{run_known[case_id]['why']}, until {run_known[case_id]['until']}"


def case_entry(result: Result, known: dict[str, dict]) -> dict:
    """One case of the record; a failing known case carries "known": "<why>, until <until>", and a case that ran under a
    profile other than the default carries "profile": {"role": ..., "signed_off": [...]} (SC-020)."""
    entry = {"id": result.case["id"], "class": result.case["class"], "question": result.case["question"],
             "result": "pass" if result.passed else "fail", "expected": result.expected, "got": result.got}
    if not result.passed and result.case["id"] in known:
        entry["known"] = known_note(known, result.case["id"])
    if result.profile:
        entry["profile"] = result.profile
    return entry


# Decision: SC-003 (the record has no date and no duration, so the same tree gives the same bytes)
def build_record(run: Run, ledger: list[dict]) -> dict:
    """The record of a run, as evals/results/offline.json holds it (docs/designs/answering-door.md 6.4)."""
    return {"version": 1, "set": display(run.set_path), "set_sha256": run.set_sha, "pack": run.document["pack"],
            "pack_version": run.pack.manifest["version"], "rules_sha256": sha_of(RULES_PATH.read_bytes()),
            "known_sha256": run.known_sha, "answerer": run.answerer_name,
            "settings": {"demo_mode": run.demo, "max_cited_passages": MAX_CITED_PASSAGES, "search_min_score": None},
            "scores": class_scores(run.results), "cases": [case_entry(result, run.known) for result in run.results],
            "accepted_falls": ledger}


def record_text(record: dict) -> str:
    """The record's bytes as text: json.dumps(record, sort_keys=True, indent=2, ensure_ascii=False) and a newline."""
    return json.dumps(record, sort_keys=True, indent=2, ensure_ascii=False) + "\n"


def load_old(path: Path) -> tuple[dict | None, str]:
    """The record on disk and its state: (None, "missing"), (None, "unreadable") or (record, "ok")."""
    if not path.is_file():
        return None, "missing"
    try:
        old = json.loads(path.read_text(encoding="utf-8"))
    except ValueError:
        return None, "unreadable"
    return (old, "ok") if isinstance(old, dict) and isinstance(old.get("cases"), list) else (None, "unreadable")


def failed(run: Run) -> list[Result]:
    """The failing cases, by class in the table's order and then set order."""
    return sorted((result for result in run.results if not result.passed), key=lambda r: CLASSES.index(r.case["class"]))


def safety_failed(run: Run) -> list[Result]:
    """The failing cases of a safety class: stop, emergency, warn and must-not-stop."""
    return [result for result in failed(run) if result.case["class"] in SAFETY_CLASSES]


def known_fixed(run: Run, old: dict | None) -> list[str]:
    """The ids of known failures the record shows failing and the run shows passing: the over-firing is fixed, so the
    entry leaves the list in the commit that fixed it. A known case that passes with no failure on record is dormant
    (the door's safety step is TODO 1.9's), not fixed: no record, or a record showing it passing, gives []."""
    was = {entry["id"]: entry.get("result") for entry in old["cases"]} if old else {}
    passed = {result.case["id"] for result in run.results if result.passed}
    return [case for case in run.known if case in passed and was.get(case) == "fail"]


def table_lines(run: Run) -> list[str]:
    """The header and the per-class table: a header, "class passed total", one row per class and a "safety" row."""
    scores = class_scores(run.results)
    mode = "demo mode" if run.demo else "no demo mode"
    lines = [f"eval: {display(run.set_path)} (sha256 {run.set_sha[:8]}), pack {run.pack.pack_id} "
             f"{run.pack.manifest['version']}, answerer {run.answerer_name}, {mode}",
             f"{'class':<15}{'passed':>6}  {'total':>5}"]
    lines += [f"{name:<15}{scores[name]['passed']:>6}  {scores[name]['total']:>5}" for name in CLASSES]
    safety = [scores[name] for name in SAFETY_CLASSES]
    lines.append(f"{'safety':<15}{sum(s['passed'] for s in safety):>6}  {sum(s['total'] for s in safety):>5}")
    return lines


def failure_lines(run: Run, fixed: list[str]) -> list[str]:
    """Each failure: "FAIL id [class] question", expected, got, and "known:" for a known failure; then a line naming
    known failures that are fixed: failure_lines(run, ["mns-03"]) ends "known but passing: mns-03, remove its entry"."""
    lines = []
    for result in failed(run):
        case = result.case
        lines += [f"FAIL {case['id']} [{case['class']}] {case['question']}", f"  expected: {result.expected}",
                  f"  got:      {result.got}"]
        if case["id"] in run.known:
            lines.append(f"  known:    {known_note(run.known, case['id'])}")
    if fixed:
        lines.append(f"known but passing: {', '.join(fixed)}, remove its entry")
    return lines


def fall_keys(old: dict, run: Run, per_class: bool) -> list[str]:
    """What passed in the record and now fails: case ids (the offline mode, per case) or class names (recorded and live
    runs, a class's passed count fell); a record with every case passing and a run failing one gives [that id]."""
    if per_class:
        now = class_scores(run.results)
        return [name for name in CLASSES if now[name]["passed"] < old.get("scores", {}).get(name, {}).get("passed", 0)]
    passing = {entry["id"] for entry in old["cases"] if entry.get("result") == "pass"}
    return [result.case["id"] for result in run.results if not result.passed and result.case["id"] in passing]


def accept_pattern(key: str, safety_ids: set[str]) -> re.Pattern:
    """The pattern an --accept-fall decision must match: a safety case or class needs a decision, SC-nnn; an accuracy
    case or class takes a decision or a journal id: accept_pattern("stop", set()) matches "SC-021" and not "J-041"."""
    return SAFETY_ACCEPT if key in safety_ids or key in SAFETY_CLASSES else ACCURACY_ACCEPT


def parse_accepts(items: list[str], safety_ids: set[str], falls: list[str]) -> dict[str, str]:
    """The --accept-fall pairs as {case: decision}; "mns-02=SC-021" gives {"mns-02": "SC-021"}. A pair that is not
    CASE=ID, a case that has not fallen, or an ID of the wrong kind raises CannotRun."""
    accepts = {}
    for item in items:
        key, _, decision = item.partition("=")
        if key not in falls:
            raise CannotRun(f"--accept-fall {item}: {key} has not fallen since the record")
        if not accept_pattern(key, safety_ids).match(decision):
            raise CannotRun(f"--accept-fall {item}: a safety case needs a decision (SC-nnn), an accuracy case a decision or J-nnn")
        accepts[key] = decision
    return accepts


# Decision: SC-019 (the record is a per-case ratchet: a fall needs a decision, a fixed known failure leaves the list)
def write_record(args: argparse.Namespace, run: Run, record_path: Path, old: dict | None) -> tuple[int, list[str]]:
    """Write the record unless refused (exit 4): a case that passed in the old record and now fails with no --accept-fall,
    or a known failure the record shows failing that now passes. Returns the exit code and the lines to print."""
    falls = fall_keys(old, run, args.answerer != "offline") if old else []
    safety_ids = {result.case["id"] for result in run.results if result.case["class"] in SAFETY_CLASSES}
    accepts = parse_accepts(args.accept_fall, safety_ids, falls)
    refused = [f"refused: {key} passed in the record and now fails; name it with --accept-fall {key}=<decision>"
               for key in falls if key not in accepts]
    refused += [f"refused: known but passing: {case}, remove its entry from known-failures.json" for case in known_fixed(run, old)]
    if refused:
        return 4, refused
    ledger = list(old.get("accepted_falls", [])) if old else []
    ledger += [{"case": key, "by": by} for key, by in accepts.items() if {"case": key, "by": by} not in ledger]
    record_path.parent.mkdir(parents=True, exist_ok=True)
    record_path.write_text(record_text(build_record(run, ledger)), encoding="utf-8")
    return 0, []


def changed_lines(old: dict, record: dict) -> list[str]:
    """What differs between the recorded run and this one: each case whose result changed ("  mns-03: recorded pass, now
    fail") and each other part of the record that differs ("  answerer differs")."""
    was = {entry["id"]: entry.get("result") for entry in old["cases"]}
    lines = [f"  {entry['id']}: recorded {was.get(entry['id'], 'absent')}, now {entry['result']}"
             for entry in record["cases"] if was.get(entry["id"]) != entry["result"]]
    lines += [f"  {key} differs" for key in sorted(record) if key != "cases" and old.get(key) != record[key]]
    return lines or ["  the cases' words differ"]


def record_path_of(args: argparse.Namespace, run: Run) -> Path:
    """Where the record lives: --record, else evals/results/offline.json, recorded-<replies stem>.json or
    model-<answerer>.json; it may not be the set itself (exit 2)."""
    names = {"offline": "offline.json", "recorded": f"recorded-{Path(args.replies or '').stem}.json",
             "claude": f"model-{run.answerer_name}.json"}
    path = Path(args.record) if args.record else RESULTS_FOLDER / names[args.answerer]
    if path.resolve() == run.set_path.resolve():
        raise CannotRun(f"--record {path} is the set itself, which is never written (docs/designs/answering-door.md 6.6)")
    return path


def check_lines(old: dict | None, state: str, record: dict, equal: bool) -> list[str]:
    """What --check says when it exits 3: no record, an unreadable one, or each difference; none when equal."""
    if equal:
        return []
    if old is None:
        return [f"eval: --check: the record is {state}; write it with --write"]
    return ["eval: --check: the run differs from the record:"] + changed_lines(old, record)
