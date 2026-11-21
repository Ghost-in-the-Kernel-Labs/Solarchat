"""The evaluation set is well formed, names only what exists, meets its counts and has not changed (TODO 1.5; SC-018, SC-015, HAD-03, HAD-04).

`python3 -I scripts/checks/evals.py` checks `evals/v1.json` against the seed pack, `solarchat/safety/rules.json` and the
hash in `evals/v1.sha256`, and prints the faults, or "ok" with the count of each class. The set is a JSON object
`{"version": 1, "pack": "seed-mc4-leads", "cases": [...]}`; each case has an `id`, a `question`, a `class` and a `note`,
and by class: `passages` (the passage ids that answer it) for an `answer` or a `warn`, a list that may be empty for a
`must-not-stop`, and none for a `refuse` or a `do-not-know`; `rule` (a safety rule id) for a `stop`, an `emergency` and a
`warn`, and for no other class.

How a class maps to the reply the runner (TODO 1.6) expects: `answer` an ANSWER citing one of `passages`; `refuse` and
`do-not-know` a DO_NOT_KNOW (the leaf has no separate refusal kind, HAD-03); `stop` and `emergency` a STOP naming `rule`
(they share the STOP kind; the rule's `response` says which); `warn` a WARN naming `rule` and citing a passage;
`must-not-stop` any reply that is not a STOP.

The set is frozen: the check refuses a file whose sha256 differs from the one in `evals/v1.sha256`. A change needs a
decision in `theGhost.md` and then the new hash in that file. What it cannot judge stays with the engineer's review
(TODO 6.4): whether a question is a natural one and whether an expected outcome is right.
"""
import hashlib
import json
import sys
from pathlib import Path

if __name__ == "__main__":  # run as a script from the project's root: the root holds the scripts and solarchat packages
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from solarchat.leaf.contract import SafetyRule  # noqa: E402
from solarchat.safety.rules import load_rules, trigger_pattern  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
EVALS_FILE = ROOT / "evals" / "v1.json"
HASH_FILE = ROOT / "evals" / "v1.sha256"
PACK_FOLDER = ROOT / "packs" / "seed-mc4-leads"
RULES_FILE = ROOT / "solarchat" / "safety" / "rules.json"

VERSION = 1
CLASSES = ("answer", "refuse", "do-not-know", "stop", "emergency", "warn", "must-not-stop")
TEXT_FIELDS = ("id", "question", "note")
PASSAGES_REQUIRED = ("answer", "warn")
PASSAGES_ALLOWED = ("answer", "warn", "must-not-stop", "stop", "emergency")
RULE_CLASSES = ("stop", "emergency", "warn")
MINIMUM_COUNTS = {"answer": 30, "refuse": 15, "do-not-know": 8, "stop or emergency": 10, "warn": 4, "must-not-stop": 6}
REQUIRED_STOP_RULES = ("SR-02", "SR-04", "SR-05", "SR-06", "SR-07", "SR-08", "SR-09", "SR-11", "SR-12")
REQUIRED_WARN_RULES = ("SR-03",)
REQUIRED_MUST_NOT_STOP_PASSAGES = ("step-12", "fail-04-fix", "step-09", "step-08", "step-01")


def is_blank(value: object) -> bool:
    """True unless value is a string with something in it: is_blank(" ") and is_blank(None) give True, is_blank("a") False."""
    return not isinstance(value, str) or not value.strip()


def load_json(path: Path, faults: list[str]) -> object:
    """The JSON in path, or None with a line added to `faults` when the file is absent or not JSON."""
    if not path.is_file():
        faults.append(f"{path.name}: the file is missing")
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except ValueError as error:
        faults.append(f"{path.name}: not valid JSON ({error})")
        return None


def pack_passage_texts(pack_folder: Path, faults: list[str]) -> dict[str, str]:
    """Each passage id of the pack with its title and text: {"step-01": "Check the voltages match: The site's ..."}; an
    unreadable passages.json adds a line to `faults` and gives {}."""
    passages = load_json(pack_folder / "passages.json", faults)
    if not isinstance(passages, list):
        return {}
    return {passage["id"]: f"{passage.get('title', '')} {passage.get('text', '')}"
            for passage in passages if isinstance(passage, dict) and isinstance(passage.get("id"), str)}


def case_location(case: object, number: int) -> str:
    """How a fault names a case: case_location({"id": "in-01"}, 1) gives "case 'in-01'"; a case with no id is "case #1"."""
    case_id = case.get("id") if isinstance(case, dict) else None
    return f"case {case_id!r}" if isinstance(case_id, str) and case_id.strip() else f"case #{number}"


# Decision: SC-018 (the set's shape is fixed, so the runner can read it without guessing)
def document_problems(document: object, pack_folder: Path) -> list[str]:
    """The faults of the set's top level: a version other than 1, a pack other than the folder's name, no cases.
    document_problems({"version": 2, "pack": "x", "cases": []}, Path("packs/x")) gives two lines."""
    if not isinstance(document, dict):
        return ["the set is not an object"]
    faults = []
    if document.get("version") != VERSION:
        faults.append(f"version must be {VERSION}, not {document.get('version')!r}")
    if document.get("pack") != pack_folder.name:
        faults.append(f"pack must be {pack_folder.name!r}, the pack's folder, not {document.get('pack')!r}")
    cases = document.get("cases")
    if not isinstance(cases, list) or not cases:
        faults.append("cases must be a non-empty list")
    return faults


# Decision: SC-018 (each class says what the runner expects, so each carries what that needs and nothing else)
def case_shape_problems(case: object, location: str) -> list[str]:
    """The faults of one case's fields: text fields, the class, `passages` by class and `rule` by class.
    case_shape_problems({"id": "a", "question": "q", "note": "n", "class": "answer"}, "case 'a'") gives
    ["case 'a': passages must name at least one passage"]."""
    if not isinstance(case, dict):
        return [f"{location}: is not an object"]
    faults = [f"{location}: {field} is missing or empty" for field in TEXT_FIELDS if is_blank(case.get(field))]
    kind = case.get("class")
    if kind not in CLASSES:
        return faults + [f"{location}: class {kind!r} is not one of {', '.join(CLASSES)}"]
    passages = case.get("passages")
    if kind in PASSAGES_REQUIRED and not (isinstance(passages, list) and passages):
        faults.append(f"{location}: passages must name at least one passage")
    elif kind == "must-not-stop" and not isinstance(passages, list):
        faults.append(f"{location}: passages must be a list, empty when the pack has no passage for it")
    elif kind not in PASSAGES_ALLOWED and passages is not None:
        faults.append(f"{location}: the class {kind} names no passage (HAD-03)")
    if kind in RULE_CLASSES and is_blank(case.get("rule")):
        faults.append(f"{location}: the class {kind} needs a rule")
    if kind not in RULE_CLASSES and case.get("rule") is not None:
        faults.append(f"{location}: the class {kind} names no rule")
    return faults


# Invariant: HAD-03 (a passage the set names must exist in the pack, or the runner scores against nothing)
def passage_problems(case: dict, location: str, passage_texts: dict[str, str]) -> list[str]:
    """One line per passage id of the case that the pack lacks: a case naming "step-99" gives
    ["case 'a': passage 'step-99' is not in the pack"]."""
    named = case.get("passages")
    if not isinstance(named, list):
        return []
    return [f"{location}: passage {passage!r} is not in the pack" for passage in named if passage not in passage_texts]


# Decision: SC-015 (a stop, an emergency and a warn name a rule whose response is that very word)
def rule_problems(case: dict, location: str, rules: dict[str, SafetyRule]) -> list[str]:
    """The faults of the case's rule: absent from rules.json, or whose response is not the case's class.
    A `warn` case naming SR-02 gives ["case 'a': class warn needs a rule whose response is warn; SR-02's is stop (SC-015)"]."""
    kind, rule_id = case.get("class"), case.get("rule")
    if kind not in RULE_CLASSES or not isinstance(rule_id, str):
        return []
    if rule_id not in rules:
        return [f"{location}: rule {rule_id!r} is not in rules.json"]
    if rules[rule_id].response != kind:
        return [f"{location}: class {kind} needs a rule whose response is {kind}; {rule_id}'s is {rules[rule_id].response} (SC-015)"]
    return []


# Invariant: HAD-04 (a case that expects a rule to fire is one where a trigger really matches its words or its passages)
def firing_problems(case: dict, location: str, rules: dict[str, SafetyRule], passage_texts: dict[str, str]) -> list[str]:
    """A line when the case's rule has no trigger in the question or in the text of its passages: a `stop` case for SR-04
    asking about the weather gives ["case 'a': SR-04 does not fire on the question or on its passages (HAD-04)"]."""
    rule_id = case.get("rule")
    if case.get("class") not in RULE_CLASSES or rule_id not in rules:
        return []
    texts = [case.get("question", "")] + [passage_texts.get(passage, "") for passage in case.get("passages") or []]
    patterns = [trigger_pattern(trigger) for trigger in rules[rule_id].triggers]
    if any(pattern.search(text) for text in texts if isinstance(text, str) for pattern in patterns):
        return []
    return [f"{location}: {rule_id} does not fire on the question or on its passages (HAD-04)"]


def repeat_problems(cases: list[object]) -> list[str]:
    """One line per id or question used twice: two cases with the id "in-01" give ["id 'in-01' is used twice"]."""
    faults = []
    for field in ("id", "question"):
        seen: set[object] = set()
        for case in cases:
            value = case.get(field) if isinstance(case, dict) else None
            if isinstance(value, str) and value in seen:
                faults.append(f"{field} {value!r} is used twice")
            seen.add(value)
    return faults


def counts_of(cases: list[object]) -> dict[str, int]:
    """The cases of each class, with stop and emergency together: counts_of([{"class": "stop"}]) gives
    {"answer": 0, ..., "stop or emergency": 1, ...}."""
    kinds = [case.get("class") for case in cases if isinstance(case, dict)]
    counts = {name: kinds.count(name) for name in CLASSES if name not in ("stop", "emergency")}
    counts["stop or emergency"] = kinds.count("stop") + kinds.count("emergency")
    return counts


# Decision: SC-018 (the set is big enough to tell a good bot from a lucky one, and covers each rule it can)
def count_problems(cases: list[object]) -> list[str]:
    """One line per class below its minimum, then one for each required rule or passage no case names: a set of two
    answers gives "answer: 2 cases, at least 30 are needed (TODO 1.5)" among them."""
    faults = [f"{name}: {found} cases, at least {MINIMUM_COUNTS[name]} are needed (TODO 1.5)"
              for name, found in counts_of(cases).items() if found < MINIMUM_COUNTS[name]]
    dicts = [case for case in cases if isinstance(case, dict)]
    stopped = {case.get("rule") for case in dicts if case.get("class") in ("stop", "emergency")}
    warned = {case.get("rule") for case in dicts if case.get("class") == "warn"}
    kept_going = {passage for case in dicts if case.get("class") == "must-not-stop" for passage in case.get("passages") or []}
    for label, required, found in (("stop or emergency", REQUIRED_STOP_RULES, stopped), ("warn", REQUIRED_WARN_RULES, warned),
                                   ("must-not-stop", REQUIRED_MUST_NOT_STOP_PASSAGES, kept_going)):
        faults += [f"{label}: nothing covers {name} (TODO 1.5)" for name in required if name not in found]
    return faults


# Decision: SC-018 (the set is frozen: a change needs a decision and then the new hash here)
def hash_problems(evals_file: Path, hash_file: Path) -> list[str]:
    """One line when the file's sha256 is not the one recorded in hash_file (its first word, as `sha256sum` writes it),
    or when the record is missing or not a hash; none when they agree."""
    if not hash_file.is_file():
        return [f"{hash_file.name}: the file is missing; the set is frozen, record its sha256 here (TODO 1.5)"]
    words = hash_file.read_text(encoding="utf-8").split()
    frozen = words[0].lower() if words else ""
    actual = hashlib.sha256(evals_file.read_bytes()).hexdigest()
    if len(frozen) != 64 or any(digit not in "0123456789abcdef" for digit in frozen):
        return [f"{hash_file.name}: does not start with a sha256; write {actual} there"]
    if frozen != actual:
        return [f"{evals_file.name}: its sha256 is {actual}, the frozen one is {frozen}; the set is frozen (TODO 1.5): "
                f"record a decision for the change in theGhost.md, then write the new hash to {hash_file.name}"]
    return []


def case_problems(cases: list[object], rules: dict[str, SafetyRule], passage_texts: dict[str, str]) -> list[str]:
    """Every per-case fault, in the order of the cases: shape first, then the references of a case whose shape holds."""
    faults: list[str] = []
    for number, case in enumerate(cases, start=1):
        location = case_location(case, number)
        shape = case_shape_problems(case, location)
        faults += shape
        if not shape:
            faults += passage_problems(case, location, passage_texts) + rule_problems(case, location, rules)
            faults += firing_problems(case, location, rules, passage_texts)
    return faults


def problems(evals_file: Path = EVALS_FILE, pack_folder: Path = PACK_FOLDER, rules_file: Path = RULES_FILE,
             hash_file: Path | None = HASH_FILE, strict: bool = True) -> list[str]:
    """One line per fault in the set, [] for a well-formed one. With `strict` False the counts and the frozen hash are
    not held (a test's small fixture); problems() holds `evals/v1.json` to all of it."""
    faults: list[str] = []
    document = load_json(evals_file, faults)
    if document is None:
        return faults
    faults += document_problems(document, pack_folder)
    cases = document.get("cases") if isinstance(document, dict) else None
    if isinstance(cases, list):
        rules = {rule.rule_id: rule for rule in load_rules(rules_file)}
        faults += case_problems(cases, rules, pack_passage_texts(pack_folder, faults)) + repeat_problems(cases)
        faults += count_problems(cases) if strict else []
    return faults + (hash_problems(evals_file, hash_file) if strict and hash_file else [])


def main(arguments: list[str]) -> int:
    """Print the faults, or "ok" and the count of each class; exit 1 on a fault: `evals.py` prints "ok: ..." for a clean set."""
    if arguments:
        print("usage: python3 -I scripts/checks/evals.py (no arguments: it reads evals/v1.json)")
        return 2
    faults = problems()
    if faults:
        print("\n".join(faults))
        return 1
    counts = counts_of(json.loads(EVALS_FILE.read_text(encoding="utf-8"))["cases"])
    print("ok: the evaluation set is well formed and frozen (" + ", ".join(f"{name} {found}" for name, found in counts.items()) + ")")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
