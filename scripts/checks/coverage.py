"""A manifest's `safety_coverage` is well formed, as docs/CONTRACT.md's "A declaration of coverage" states it (SC-024, SC-016).

`scripts/checks/packs.py` calls `coverage_problems` with the manifest, the passages and the sources' kinds, and prints
`coverage_lines` for a well-formed pack. The general rules' ids are read from `solarchat/safety/rules.json`. Standard library only.
"""
import json
import re
from pathlib import Path

PAGE_NUMBER = re.compile(r"^\d+(?:(?:, |-)\d+)*$")
RULES_FILE = Path(__file__).resolve().parents[2] / "solarchat" / "safety" / "rules.json"
COVERAGE_RESPONSES = ("warn", "stop")
EMERGENCY_RULES = ("SR-08", "SR-09")
DECLARED_FIELDS = ("by", "role", "date", "evidence")


def blank(value: object) -> bool:
    """True unless value is a string with something in it: blank(" ") and blank(None) give True, blank("a") False."""
    return not isinstance(value, str) or not value.strip()


def read_list(folder: Path, name: str) -> list:
    """The list in folder/name, [] when the file is absent or is not a list of objects (the pack check reports that)."""
    try:
        loaded = json.loads((folder / name).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    return [item for item in loaded if isinstance(item, dict)] if isinstance(loaded, list) else []


def general_rule_ids() -> set[str]:
    """The ids of the general rules in solarchat/safety/rules.json: {"SR-01", "SR-02", ...}."""
    return {rule["id"] for rule in json.loads(RULES_FILE.read_text(encoding="utf-8"))}


def covers_with_a_page(passage: dict, source_kinds: dict[str, object]) -> bool:
    """True when one of the passage's citations is a `document` source with a numeric page: "unknown" never counts."""
    citations = passage.get("sources") if isinstance(passage.get("sources"), list) else []
    return any(isinstance(cited, dict) and source_kinds.get(cited.get("source")) == "document"
               and isinstance(cited.get("page"), str) and bool(PAGE_NUMBER.match(cited["page"])) for cited in citations)


def declaration_problems(entry: dict, location: str, passages: dict[str, dict], source_kinds: dict[str, object], manifest: dict) -> list[str]:
    """The lines for one declaration: its response, its passages (own, non-empty, one with a paged document), and, on a
    demo pack, its `declared` (SC-016's four fields, role "maintainer")."""
    faults: list[str] = []
    allowed = ("emergency",) if entry.get("rule") in EMERGENCY_RULES else COVERAGE_RESPONSES
    if entry.get("response") not in allowed:
        faults.append(f"{location}: response must be {' or '.join(repr(word) for word in allowed)}")
    named = entry.get("passages")
    if not isinstance(named, list) or not named:
        faults.append(f"{location}: passages must name at least one passage of this pack")
    else:
        faults += [f"{location}: passage {name!r} is not a passage of this pack" for name in named if not isinstance(name, str) or name not in passages]
        faults += [f"{location}: passage {name!r} cites no document source with a page that is a number" for name in named
                   if isinstance(name, str) and name in passages and not covers_with_a_page(passages[name], source_kinds)]
    declared = entry.get("declared")
    if manifest.get("status") == "demo" or declared is not None:
        if not isinstance(declared, dict) or any(blank(declared.get(name)) for name in DECLARED_FIELDS):
            faults.append(f"{location}: declared needs {', '.join(DECLARED_FIELDS)}, each with something in it (SC-016)")
        elif manifest.get("status") == "demo" and declared.get("role") != "maintainer":
            faults.append(f"{location}: a demo pack's declaration is made by the maintainer: role must be 'maintainer' (SC-024)")
    return faults


# Decision: SC-024 (only a make-and-model pack's manifest may name a general rule, and only to say its own passages cover it)
def coverage_problems(manifest: object, passages: list[dict], source_kinds: dict[str, object]) -> list[str]:
    """The lines for the manifest's `safety_coverage` (absent or empty: none): a rule that is not a general rule or is listed
    twice, a passage that is not the pack's or has no paged document, a response out of place, no make and model, and a
    demo pack's declaration without a maintainer's `declared`; a rule SR-99 gives "manifest.json safety_coverage 'SR-99':
    not the id of a general safety rule"."""
    if not isinstance(manifest, dict) or manifest.get("safety_coverage") in (None, []):
        return []
    entries = manifest["safety_coverage"]
    if not isinstance(entries, list) or not all(isinstance(entry, dict) for entry in entries):
        return ["manifest.json: safety_coverage must be a list of objects"]
    faults: list[str] = []
    if blank(manifest.get("make")) and not blank(manifest.get("installation_type")):
        faults.append("manifest.json: safety_coverage needs make and model; an installation_type pack cannot declare coverage (SC-024)")
    rules, own_passages = general_rule_ids(), {str(passage.get("id")): passage for passage in passages}
    rule_ids = [entry.get("rule") for entry in entries]
    for position, entry in enumerate(entries):
        location = f"manifest.json safety_coverage {entry.get('rule')!r}"
        if entry.get("rule") not in rules:
            faults.append(f"{location}: not the id of a general safety rule")
        elif rule_ids.count(entry["rule"]) > 1 and rule_ids.index(entry["rule"]) != position:
            faults.append(f"{location}: a rule is declared once")
        faults += declaration_problems(entry, location, own_passages, source_kinds, manifest)
    return faults


def coverage_lines(folder: Path) -> list[str]:
    """For each declaration of a pack, the rule, the response and the covering passages' sources with pages, for a person
    to read: ["SR-02 warn: passage 'voltage' (Examplesun ES-100 installation manual, page 1)"]. [] when there is none."""
    try:
        manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    if not isinstance(manifest, dict) or not isinstance(manifest.get("safety_coverage"), list):
        return []
    titles = {str(source.get("id")): source.get("title") for source in manifest.get("sources", []) if isinstance(source, dict)}
    passages = {str(passage.get("id")): passage for passage in read_list(folder, "passages.json")}
    lines = []
    for entry in manifest["safety_coverage"]:
        shown = []
        for name in entry["passages"]:
            cited = [f"{titles.get(c['source'])}, page {c['page']}" for c in passages[name]["sources"] if isinstance(c, dict)]
            shown.append(f"passage {name!r} ({'; '.join(cited)})")
        lines.append(f"{entry['rule']} {entry['response']}: " + ", ".join(shown))
    return lines
