"""The rule bank is well formed, names only what exists and never quotes the bot's system prompt (TODO 1.19; SC-023, design section 3).

`python3 -I scripts/checks/bank.py` checks every `evals/bank/<family>.json` and prints the faults, or "ok" with the count of
each family. A file is `{"version": 1, "family": "<name>", "rules": [...]}`, its name the family's; a rule has the fields of
`docs/designs/rule-bank-and-triage.md` section 3.2: `id`, `family`, `status`, `behaviour`, `worker` (`facts`, and an optional
`says_role`), `turns`, `question`, `graded_reply`, `severity`, `source` and `drafted`, and a retired rule also `retired`.

What it refuses: a missing or empty field; an id that is not `BR-` and four digits, is reused (in any file) or is not above
the one before it in its file; no turns or more than three; a `graded_reply` that is neither "all" nor a turn's number; a
question that does not end in "?"; a source that does not resolve (a pack passage, a safety rule in `rules.json`, a source
folder of the library, a case of `evals/v1.json`); and a rule that quotes the bot's system prompt.

Quoting (the coordinator's reading of 3.2, J-053): no string field of a rule, the turns and the facts included, shares a run
of six consecutive words with `SYSTEM_PROMPT` of `solarchat/model/claude.py`, words being runs of letters and digits after
lowercasing, so punctuation and spacing do not hide a copy. The prompt is read by import: `scripts/eval.py` already imports
that module, and it loads without the model package.

What it cannot judge stays with the reviewer (3.3): whether a question names the reply it reads and puts yes on the wanted
behaviour, and whether a rule is worth running. A `direction` or a `triage` source is held to a non-empty reference only;
the triage records do not exist until 1.23. No model is called.
"""
import json
import re
import sys
from pathlib import Path

if __name__ == "__main__":  # run as a script from the project's root: the root holds the scripts and solarchat packages
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.checks.common import tracked_files  # noqa: E402
from scripts.checks.evals import is_blank, load_json, pack_passage_texts  # noqa: E402
from solarchat.model.claude import SYSTEM_PROMPT  # noqa: E402
from solarchat.safety.rules import load_rules  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
BANK_FOLDER = ROOT / "evals" / "bank"
V1_FILE = ROOT / "evals" / "v1.json"
RULES_FILE = ROOT / "solarchat" / "safety" / "rules.json"
PACKS_FOLDER = ROOT / "packs"
LIBRARY_FOLDER = ROOT / "library" / "sources"

VERSION = 1
FAMILIES = ("scope", "allows", "ask", "pace", "track", "cite", "safety", "injection")
STATUSES = ("active", "retired")
SEVERITIES = ("safety", "core", "manner")
SOURCE_KINDS = ("pack", "safety-rule", "library", "v1", "direction", "triage")
TEXT_FIELDS = ("behaviour", "question")
REQUIRED = ("id", "family", "status", "behaviour", "worker", "turns", "question", "graded_reply", "severity", "source", "drafted")
MAX_TURNS = 3
RUN = 6
ID_FORM = re.compile(r"BR-\d{4}")


def words_of(text: str) -> list[str]:
    """The words of a text, runs of letters and digits after lowercasing: words_of("Stop, then WAIT.") gives ["stop", "then", "wait"]."""
    return re.findall(r"[a-z0-9]+", text.lower())


def runs_of(text: str) -> set[tuple[str, ...]]:
    """Every run of six consecutive words of a text: runs_of("a b c d e f g") gives two runs, the first ("a" ... "f")."""
    words = words_of(text)
    return {tuple(words[start:start + RUN]) for start in range(len(words) - RUN + 1)}


def strings_of(value: object) -> list[str]:
    """Every string in a loaded value, keys included, at any depth: strings_of({"a": ["b", 1]}) gives ["a", "b"]."""
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        return [text for key, item in value.items() for text in strings_of(key) + strings_of(item)]
    if isinstance(value, list):
        return [text for item in value for text in strings_of(item)]
    return []


# Decision: SC-023 (a rule is its own judgement and never a copy of the bot's instructions, so a trend means what the rule says)
def quoting_problems(rule: dict, location: str, prompt: str = SYSTEM_PROMPT) -> list[str]:
    """One line per string field of the rule that shares a run of six words with the prompt: a turn that repeats a
    sentence of it gives ["rule 'BR-0001': turns[0] quotes the bot's system prompt: 'give the one next thing the ...'"].
    Fields are named by their top-level key."""
    prompt_runs = runs_of(prompt)
    faults = []
    for key, value in rule.items():
        items = value if isinstance(value, list) and key == "turns" else [value]
        for number, item in enumerate(items):
            name = f"turns[{number}]" if key == "turns" else key
            for text in strings_of(item):
                shared = sorted(run for run in runs_of(text) if run in prompt_runs)
                if shared:
                    faults.append(f"{location}: {name} quotes the bot's system prompt: {' '.join(shared[0])!r} (SC-023)")
                    break
    return faults


def is_text_list(value: object) -> bool:
    """True for a list of non-blank strings: is_text_list(["a"]) is True, is_text_list([""]) and is_text_list("a") False."""
    return isinstance(value, list) and all(not is_blank(item) for item in value)


def worker_problems(worker: object, location: str) -> list[str]:
    """The faults of a rule's `worker`: not an object, `facts` not an object of texts, a `says_role` that is blank.
    worker_problems({"facts": 3}, "rule 'a'") gives ["rule 'a': worker.facts must be an object of texts"]."""
    if not isinstance(worker, dict):
        return [f"{location}: worker must be an object"]
    faults = []
    facts = worker.get("facts")
    if not isinstance(facts, dict) or any(is_blank(key) or is_blank(item) for key, item in facts.items()):
        faults.append(f"{location}: worker.facts must be an object of texts")
    if "says_role" in worker and is_blank(worker["says_role"]):
        faults.append(f"{location}: worker.says_role is blank")
    return faults


def drafted_problems(rule: dict, location: str) -> list[str]:
    """The faults of `drafted` and `retired`: `drafted` needs by, batch and on; a retired rule needs `retired` with on and
    why, and an active one has none."""
    faults = []
    drafted = rule.get("drafted")
    if not isinstance(drafted, dict) or any(is_blank(drafted.get(field)) for field in ("by", "batch", "on")):
        faults.append(f"{location}: drafted must name by, batch and on")
    retired = rule.get("retired")
    if rule.get("status") == "retired":
        if not isinstance(retired, dict) or any(is_blank(retired.get(field)) for field in ("on", "why")):
            faults.append(f"{location}: a retired rule needs retired with on and why")
    elif retired is not None:
        faults.append(f"{location}: only a retired rule has retired")
    return faults


# Decision: SC-023 (a rule is one judgement of one to three turns, yes meaning the behaviour wanted)
def shape_problems(rule: object, location: str, family: str) -> list[str]:
    """The faults of one rule's own fields, none of its references: missing fields, the family, the status, the severity,
    the texts, one to three turns, `graded_reply` within them and a question ending in "?". A rule with four turns gives
    ["rule 'a': turns must be one to three worker turns"]."""
    if not isinstance(rule, dict):
        return [f"{location}: is not an object"]
    faults = [f"{location}: {field} is missing" for field in REQUIRED if field not in rule]
    faults += [f"{location}: {field} is empty" for field in TEXT_FIELDS if field in rule and is_blank(rule[field])]
    if "family" in rule and rule["family"] != family:
        faults.append(f"{location}: family {rule['family']!r} is not the file's, {family!r}")
    if "status" in rule and rule["status"] not in STATUSES:
        faults.append(f"{location}: status {rule['status']!r} is not one of {', '.join(STATUSES)}")
    if "severity" in rule and rule["severity"] not in SEVERITIES:
        faults.append(f"{location}: severity {rule['severity']!r} is not one of {', '.join(SEVERITIES)}")
    turns = rule.get("turns")
    if "turns" in rule and not (is_text_list(turns) and 1 <= len(turns) <= MAX_TURNS):
        faults.append(f"{location}: turns must be one to three worker turns, each a text")
    graded = rule.get("graded_reply")
    count = len(turns) if isinstance(turns, list) else 0
    if "graded_reply" in rule and not (graded == "all" or (isinstance(graded, int) and not isinstance(graded, bool) and 1 <= graded <= count)):
        faults.append(f"{location}: graded_reply {graded!r} must be \"all\" or a reply from 1 to the {count} turns")
    question = rule.get("question")
    if isinstance(question, str) and question.strip() and not question.rstrip().endswith("?"):
        faults.append(f"{location}: question must end in \"?\"")
    if "worker" in rule:
        faults += worker_problems(rule["worker"], location)
    faults += drafted_problems(rule, location)
    return faults


class Known:
    """What a source may name, read once: pack passage ids by pack, safety rule ids, library source ids, v1 case ids."""

    def __init__(self, faults: list[str], packs_folder: Path, rules_file: Path, library_ids: set[str], v1_file: Path) -> None:
        """Read the packs under packs_folder, the rules, the v1 set and take the library ids; an unreadable one adds to `faults`."""
        self.passages = {pack.name: set(pack_passage_texts(pack, faults)) for pack in sorted(packs_folder.iterdir())
                         if (pack / "passages.json").is_file()} if packs_folder.is_dir() else {}
        self.rules = {rule.rule_id for rule in load_rules(rules_file)}
        self.library = library_ids
        document = load_json(v1_file, faults)
        cases = document.get("cases") if isinstance(document, dict) else None
        self.cases = {case.get("id") for case in cases if isinstance(case, dict)} if isinstance(cases, list) else set()

    def has_passage(self, ref: str) -> bool:
        """True when ref is "<pack>/<passage>" and the pack has the passage: has_passage("seed-mc4-leads/step-01") is True."""
        pack, _, passage = ref.partition("/")
        return passage in self.passages.get(pack, set())


# Invariant: SC-023 (a rule's source resolves, so a trend can be traced to the page, the safety rule or the case it came from)
def source_problems(rule: dict, location: str, known: Known) -> list[str]:
    """One line per source that is malformed or does not resolve, and one when there is none: a pack ref "seed-mc4-leads/step-99"
    gives ["rule 'a': source pack 'seed-mc4-leads/step-99' is not a passage of the pack"]."""
    sources = rule.get("source")
    if not isinstance(sources, list) or not sources:
        return [] if "source" not in rule else [f"{location}: source must name at least one source"]
    faults = []
    for item in sources:
        kind, ref = (item.get("kind"), item.get("ref")) if isinstance(item, dict) else (None, None)
        if kind not in SOURCE_KINDS or is_blank(ref):
            faults.append(f"{location}: a source needs a kind of {', '.join(SOURCE_KINDS)} and a ref")
        elif kind == "pack" and not known.has_passage(ref):
            faults.append(f"{location}: source pack {ref!r} is not a passage of the pack")
        elif kind == "safety-rule" and ref not in known.rules:
            faults.append(f"{location}: source safety-rule {ref!r} is not in rules.json")
        elif kind == "library" and ref not in known.library:
            faults.append(f"{location}: source library {ref!r} is not a source folder of the library")
        elif kind == "v1" and ref not in known.cases:
            faults.append(f"{location}: source v1 {ref!r} is not a case of the frozen set")
    return faults


def id_problems(rules: list[object], name: str, seen: set[str]) -> list[str]:
    """The faults of the ids of one file's rules: not `BR-` and four digits, used before in any file (`seen` is added to),
    or not above the one before in the file. Ids BR-0002 then BR-0001 give ["ask.json: BR-0001 is out of order, after BR-0002"]."""
    faults = []
    previous = ""
    for rule in rules:
        rule_id = rule.get("id") if isinstance(rule, dict) else None
        if not isinstance(rule_id, str) or not ID_FORM.fullmatch(rule_id):
            if isinstance(rule, dict) and "id" in rule:
                faults.append(f"{name}: id {rule_id!r} is not BR- and four digits")
            continue
        if rule_id in seen:
            faults.append(f"{name}: {rule_id} is used twice; an id is never reused")
        elif previous and rule_id < previous:
            faults.append(f"{name}: {rule_id} is out of order, after {previous}")
        seen.add(rule_id)
        previous = max(previous, rule_id)
    return faults


def file_problems(path: Path, seen: set[str], known: Known) -> tuple[list[str], dict[str, int]]:
    """The faults of one family file and the count of its rules: the top level, then the ids, then each rule's shape and, when
    its shape holds, its references and its quoting."""
    faults: list[str] = []
    document = load_json(path, faults)
    if not isinstance(document, dict):
        return faults or [f"{path.name}: the file is not an object"], {}
    family = path.stem
    if family not in FAMILIES:
        faults.append(f"{path.name}: the file name must be a family: {', '.join(FAMILIES)}")
    if document.get("version") != VERSION:
        faults.append(f"{path.name}: version must be {VERSION}, not {document.get('version')!r}")
    if document.get("family") != family:
        faults.append(f"{path.name}: family must be {family!r}, the file's name, not {document.get('family')!r}")
    rules = document.get("rules")
    if not isinstance(rules, list) or not rules:
        return faults + [f"{path.name}: rules must be a non-empty list"], {}
    faults += id_problems(rules, path.name, seen)
    for number, rule in enumerate(rules, start=1):
        rule_id = rule.get("id") if isinstance(rule, dict) else None
        location = f"{path.name}: rule {rule_id!r}" if isinstance(rule_id, str) else f"{path.name}: rule #{number}"
        shape = shape_problems(rule, location, family)
        faults += shape
        if isinstance(rule, dict):
            faults += source_problems(rule, location, known) + quoting_problems(rule, location)
    return faults, {family: len(rules)}


def library_ids(root: Path, library_folder: Path) -> set[str]:
    """The source ids of the library, the folder names under library/sources that git lists: {"osha-solar-electrical", ...}."""
    base = library_folder.relative_to(root).parts
    return {path.relative_to(root).parts[len(base)] for path in tracked_files(root) if path.relative_to(root).parts[:len(base)] == base
            and len(path.relative_to(root).parts) > len(base) + 1}


def problems(bank_folder: Path = BANK_FOLDER, root: Path = ROOT, counts: dict[str, int] | None = None) -> list[str]:
    """One line per fault in the bank, [] for a well-formed one; `counts` is filled with the rules of each family. The files read
    are the `.json` files git lists in bank_folder; the packs, rules, library and v1 set are the root's."""
    faults: list[str] = []
    known = Known(faults, root / "packs", root / "solarchat" / "safety" / "rules.json", library_ids(root, root / "library" / "sources"),
                  root / "evals" / "v1.json")
    files = [path for path in tracked_files(root) if path.parent == bank_folder and path.suffix == ".json"]
    if not files:
        return faults + ["the bank has no family file under evals/bank/"]
    seen: set[str] = set()
    for path in files:
        found, counted = file_problems(path, seen, known)
        faults += found
        if counts is not None:
            counts.update(counted)
    return faults


def main(arguments: list[str]) -> int:
    """Print the faults, or "ok" and the rules of each family; exit 1 on a fault: `bank.py` prints "ok: ..." for a clean bank."""
    if arguments:
        print("usage: python3 -I scripts/checks/bank.py (no arguments: it reads evals/bank/)")
        return 2
    counts: dict[str, int] = {}
    faults = problems(counts=counts)
    if faults:
        print("\n".join(faults))
        return 1
    print("ok: the rule bank is well formed (" + ", ".join(f"{name} {found}" for name, found in counts.items()) + ")")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
