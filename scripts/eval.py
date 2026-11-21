"""The evaluation runner: feeds every case of the frozen set to the answering door and scores each reply (TODO 1.6; SC-019).

    python3 -I scripts/eval.py [--set PATH] [--packs DIR] [--answerer offline|recorded|model] [--replies PATH]
        [--live] [--record-replies PATH] [--demo] [--record PATH] [--check | --write [--accept-fall CASE=ID ...]]

It loads the set, runs `scripts/checks/evals.py`'s `problems` on it (exit 2 on any), calls `answer()` once per case, scores
the reply by the case's class (`scripts/eval_core.py`, the table of `docs/designs/answering-door.md` 6.2), prints a
per-class table and each failure, and compares the run with the committed record, `evals/results/offline.json`
(`scripts/eval_record.py`; byte-stable, no date). Exit: 0 a plain run with no safety-class failure, `--check` equal to the
record, `--write` written; 1 a plain run with a safety-class failure (stop, emergency, warn, must-not-stop); 2 it cannot
run (usage, a set that fails its check, a missing pack, a demo pack without `--demo`, `model` without `--live`, a replies
file for another set, `--record` naming the set); 3 `--check` and no record or a run that differs; 4 `--write` refused (a
case the record shows passing now fails with no `--accept-fall CASE=ID`, or a known failure the record shows failing now
passes). `known-failures.json`, beside the set, explains a failure and never excuses one. `--live` is the only way a model
is called, and no model client exists yet (roadmap 3.1).
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if __name__ == "__main__":  # run as a script from the project's root: the root holds the scripts and solarchat packages
    sys.path.insert(0, str(ROOT))
from scripts.checks import evals as set_check  # noqa: E402
from scripts.eval_core import SAFETY_CLASSES, CannotRun, Result, Run, display, score_case, sha_of  # noqa: E402
from scripts.eval_record import (build_record, check_lines, failed, failure_lines, known_fixed, load_old,  # noqa: E402
                                 record_path_of, record_text, safety_failed, table_lines, write_record)
from solarchat.answer.door import answer  # noqa: E402
from solarchat.answer.recorded import RecordedAnswerer  # noqa: E402
from solarchat.answer.stub import NoAnswer  # noqa: E402
from solarchat.leaf.contract import may_answer  # noqa: E402
from solarchat.packs.load import load_pack  # noqa: E402
from solarchat.safety.rules import load_rules  # noqa: E402

KNOWN_FIELDS = ("case", "rule", "why", "until", "evidence")


def build_parser() -> argparse.ArgumentParser:
    """The command line of the module docstring: build_parser().parse_args(["--demo"]).demo gives True."""
    parser = argparse.ArgumentParser(prog="scripts/eval.py", description="Score the answering door on the frozen set.")
    parser.add_argument("--set", default=str(ROOT / "evals" / "v1.json"))
    parser.add_argument("--packs", default=str(ROOT / "packs"))
    parser.add_argument("--answerer", choices=("offline", "recorded", "model"), default="offline")
    parser.add_argument("--replies")
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--record-replies")
    parser.add_argument("--demo", action="store_true")
    parser.add_argument("--record")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--write", action="store_true")
    parser.add_argument("--accept-fall", action="append", default=[], metavar="CASE=ID")
    return parser


# Decision: SC-019 (--live is the only way a model is called; no other run can load a model client)
def options_problem(args: argparse.Namespace) -> str | None:
    """What is wrong with the options, or None: --answerer model without --live gives "--answerer model needs --live"."""
    if args.answerer == "model" and not args.live:
        return "--answerer model needs --live (the model is only ever called by hand, SC-002)"
    if args.live:
        return "no model answerer yet, roadmap 3.1" if args.answerer == "model" else "--live goes with --answerer model"
    if args.record_replies:
        return "--record-replies needs --live"
    if args.accept_fall and not args.write:
        return "--accept-fall goes with --write"
    if (args.answerer == "recorded") != bool(args.replies):
        return "--answerer recorded needs --replies PATH, and --replies goes with it"
    return None


def read_set(set_path: Path) -> tuple[str, dict]:
    """The set's sha256 and parsed document, from one read of its bytes; a missing or unparsable file raises CannotRun."""
    try:
        data = set_path.read_bytes()
        document = json.loads(data)
    except (OSError, ValueError) as error:
        raise CannotRun(f"{set_path}: {error}") from error
    if not isinstance(document, dict) or not isinstance(document.get("pack"), str):
        raise CannotRun(f"{set_path}: not an evaluation set (no 'pack')")
    return sha_of(data), document


def known_problems(entries: object, document: dict) -> list[str]:
    """What is wrong with a known-failures list: every entry has each of KNOWN_FIELDS filled and names a case of the set
    whose class is a safety class; [{"case": "nope"}] gives faults naming the missing fields."""
    if not isinstance(entries, list):
        return ["not a list"]
    classes = {case["id"]: case["class"] for case in document["cases"]}
    found = []
    for entry in entries:
        blank = [name for name in KNOWN_FIELDS if not isinstance(entry, dict) or set_check.is_blank(entry.get(name))]
        if blank:
            found.append(f"an entry has no {', '.join(blank)}")
        elif classes.get(entry["case"]) not in SAFETY_CLASSES:
            found.append(f"{entry['case']} is not a stop, emergency, warn or must-not-stop case of the set")
    return found


def load_known(set_path: Path, document: dict) -> tuple[dict[str, dict], str | None]:
    """The known failures beside the set by case id, and the file's sha256 (None with no file): the file is
    `known-failures.json` in the set's folder; a malformed one raises CannotRun."""
    path = set_path.parent / "known-failures.json"
    if not path.is_file():
        return {}, None
    try:
        entries = json.loads(path.read_bytes())
    except ValueError as error:
        raise CannotRun(f"{path}: {error}") from error
    faults = known_problems(entries, document)
    if faults:
        raise CannotRun(f"{path}: {faults[0]}")
    return {entry["case"]: entry for entry in entries}, sha_of(path.read_bytes())


def choose_answerer(args: argparse.Namespace, set_sha: str) -> object:
    """The answerer the options name: offline is NoAnswer (TODO 1.8 replaces it); recorded replays --replies and must
    be recorded against this set, or CannotRun."""
    if args.answerer == "offline":
        return NoAnswer()
    try:
        recorded = RecordedAnswerer(Path(args.replies))
    except ValueError as error:
        raise CannotRun(str(error)) from error
    if recorded.set_sha256 != set_sha:
        raise CannotRun(f"{args.replies} was recorded against another set (its set_sha256 is not this set's)")
    return recorded


def prepare(args: argparse.Namespace) -> Run:
    """Load, check and run: the set, its check, the pack, the answerer; every reply scored. Raises CannotRun."""
    set_path = Path(args.set)
    set_sha, document = read_set(set_path)
    pack_folder = Path(args.packs) / document["pack"]
    hash_file = set_path.with_suffix(".sha256")
    faults = set_check.problems(set_path, pack_folder, hash_file=hash_file if hash_file.is_file() else None,
                                strict=hash_file.is_file())
    if faults:
        raise CannotRun(f"{set_path} fails its check: {faults[0]}")
    try:
        pack = load_pack(pack_folder)
    except ValueError as error:
        raise CannotRun(str(error)) from error
    if not may_answer(pack.manifest, args.demo):
        status = pack.manifest["status"]
        raise CannotRun(f"{pack.pack_id} is a demo pack: run with --demo (HAD-06)" if status == "demo"
                        else f"{pack.pack_id} has the status {status!r}, which may not answer (HAD-06)")
    answerer = choose_answerer(args, set_sha)
    rules = {rule.rule_id: rule for rule in load_rules()}
    results = [score_case(case, answer(case["question"], (pack,), args.demo, answerer), document["pack"], rules)
               for case in document["cases"]]
    known, known_sha = load_known(set_path, document)
    return Run(set_path, set_sha, document, pack, answerer.name, args.demo, results, known, known_sha)


def conclude(args: argparse.Namespace, run: Run) -> int:
    """Print the run and the record's verdict and return the exit code of the module docstring."""
    record_path = record_path_of(args, run)
    old, state = load_old(record_path)
    if args.write and state == "unreadable":
        raise CannotRun(f"{record_path}: the record is not readable; fix or remove it")
    record = build_record(run, list(old.get("accepted_falls", [])) if old else [])
    equal = state == "ok" and record_path.read_text(encoding="utf-8") == record_text(record)
    extra, status = [], {"ok": "current" if equal else "stale", "missing": "missing", "unreadable": "unreadable"}[state]
    if args.write:
        code, extra = write_record(args, run, record_path, old)
        status = "written" if code == 0 else "not written"
    elif args.check:
        code, extra = (0 if equal else 3), check_lines(old, state, record, equal)
    else:
        code = 1 if safety_failed(run) else 0
    known_failing = sum(result.case["id"] in run.known for result in failed(run))
    print("\n".join(table_lines(run) + failure_lines(run, known_fixed(run, old)) + extra))
    print(f"eval: {sum(r.passed for r in run.results)}/{len(run.results)} passed, {len(safety_failed(run))} safety failures "
          f"({known_failing} known); record {display(record_path)} {status}; exit {code}")
    return code


def main(argv: list[str]) -> int:
    """Run the evaluation and return the exit code: main(["--demo", "--check"]) is 0 while the record is current."""
    try:
        args = build_parser().parse_args(argv)
    except SystemExit as stop:
        return 0 if stop.code in (0, None) else 2
    try:
        problem = options_problem(args)
        if problem:
            raise CannotRun(problem)
        return conclude(args, prepare(args))
    except CannotRun as stop:
        print(f"eval: cannot run: {stop}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
