"""Reads the safety rules from rules.json, next to this file, and returns them as the leaf's `SafetyRule`s.

The file is the rules' one source of truth (HAD-04); `scripts/safety_rules_doc.py` writes `docs/SAFETY-RULES.md`
from what this loader returns, so the document and the data cannot disagree. Standard library and the leaf only.
"""
import json
from pathlib import Path

from solarchat.leaf.contract import SafetyRule, SafetyRuleSource

RULES_PATH = Path(__file__).resolve().parent / "rules.json"
PROCEDURES_FIRST_RULE_ID = "SR-01"


def rule_from_entry(entry: dict) -> SafetyRule:
    """One rules.json entry as a SafetyRule: {"id": "SR-01", "title": ..., "sources": [{"title": ..., "url": ...}]}
    gives SafetyRule("SR-01", ...); a missing field raises KeyError, an incomplete rule ValueError."""
    rule_sources = tuple(SafetyRuleSource(source["title"], source["url"]) for source in entry["sources"])
    return SafetyRule(rule_id=entry["id"], title=entry["title"], applies_when=entry["applies_when"],
                      triggers=tuple(entry["triggers"]), words_shown=entry["words_shown"], sources=rule_sources,
                      ghost_to_confirm=entry.get("ghost_to_confirm"))


# Invariant: HAD-04 (rule ids are SR-01, SR-02, ... in order and never reused, so a stop names one rule unambiguously)
def sequence_problem(loaded_rules: tuple[SafetyRule, ...]) -> str | None:
    """None when the ids run SR-01, SR-02, ... with no gap or repeat; ids SR-01, SR-03 give "rule 2 is SR-03, not SR-02"."""
    for rule_number, rule in enumerate(loaded_rules, start=1):
        expected_id = f"SR-{rule_number:02d}"
        if rule.rule_id != expected_id:
            return f"rule {rule_number} is {rule.rule_id}, not {expected_id}"
    return None


# Invariant: HAD-04 (the site's own safety procedures come first: the first rule says so)
def load_rules(rules_path: Path = RULES_PATH) -> tuple[SafetyRule, ...]:
    """Every safety rule in rules_path, in order; raises ValueError when the file is empty, out of sequence, or its first
    rule is not the procedures-first rule. load_rules()[0].rule_id gives "SR-01"."""
    loaded_rules = tuple(rule_from_entry(entry) for entry in json.loads(rules_path.read_text(encoding="utf-8")))
    if not loaded_rules:
        raise ValueError(f"{rules_path}: there are no safety rules")
    out_of_sequence = sequence_problem(loaded_rules)
    if out_of_sequence:
        raise ValueError(f"{rules_path}: {out_of_sequence}")
    if "come first" not in loaded_rules[0].title:
        raise ValueError(f"{rules_path}: {PROCEDURES_FIRST_RULE_ID} is the rule that the site's own safety procedures come first")
    return loaded_rules
