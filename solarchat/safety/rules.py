"""Reads the safety rules from rules.json, next to this file, and returns them as the leaf's `SafetyRule`s.

The file is the rules' one source of truth (HAD-04); `scripts/safety_rules_doc.py` writes `docs/SAFETY-RULES.md`
from what this loader returns, so the document and the data cannot disagree. Standard library and the leaf only.
"""
import hashlib
import json
import re
from pathlib import Path

from solarchat.leaf.contract import CHANGE_FIELDS, SafetyLowering, SafetyRule, SafetyRuleChange, SafetyRuleSource

RULES_PATH = Path(__file__).resolve().parent / "rules.json"
PROCEDURES_FIRST_RULE_ID = "SR-01"


# Decision: SC-016 (an entry missing a field, or holding something that is not text, is refused by name)
def change_from_entry(rule_id: str, number: int, entry: dict) -> SafetyRuleChange:
    """One change-log entry as a SafetyRuleChange: {"date": "2026-11-21", "by": "Ghost", "role": "maintainer", "why": "...",
    "evidence": "J-032"} stands; one with no "why" raises ValueError "SR-03: change 2 is missing 'why'"."""
    for name in CHANGE_FIELDS:
        if not isinstance(entry.get(name), str):
            raise ValueError(f"{rule_id}: change {number} is missing {name!r}, as text (SC-016)")
    return SafetyRuleChange(*(entry[name] for name in CHANGE_FIELDS), fingerprint=entry.get("fingerprint"))


# Decision: SC-020 (a rule's lowerings are data in rules.json: {"signed_off" or "role", "response", "words"})
def lowering_from_entry(entry: dict) -> SafetyLowering:
    """One lowered_for entry as a SafetyLowering: {"signed_off": "meter", "response": "warn", "words": "..."} stands; a
    missing "response" or "words" is a KeyError."""
    return SafetyLowering(response=entry["response"], words=entry["words"], signed_off=entry.get("signed_off"),
                          role=entry.get("role"))


def rule_from_entry(entry: dict) -> SafetyRule:
    """One rules.json entry as a SafetyRule: {"id": "SR-01", "title": ..., "sources": [{"title": ..., "url": ...}]}
    gives SafetyRule("SR-01", ...); a missing field raises KeyError, an incomplete rule ValueError. A missing
    "response" or "changes" is an incomplete rule (SC-015, SC-016), not a KeyError."""
    rule_sources = tuple(SafetyRuleSource(source["title"], source["url"]) for source in entry["sources"])
    rule_changes = tuple(change_from_entry(entry["id"], number, change)
                         for number, change in enumerate(entry.get("changes", []), start=1))
    return SafetyRule(rule_id=entry["id"], title=entry["title"], applies_when=entry["applies_when"],
                      triggers=tuple(entry["triggers"]), words_shown=entry["words_shown"], sources=rule_sources,
                      response=entry.get("response", ""), changes=rule_changes,
                      engineer_to_confirm=entry.get("engineer_to_confirm"),
                      lowered_for=tuple(lowering_from_entry(lowering) for lowering in entry.get("lowered_for", [])),
                      reads=entry.get("reads", "both"))


# Decision: SC-016 (the fingerprint is the sha256 of a canonical JSON of the rule's triggers, words_shown and response)
# Decision: SC-020 (and its lowered_for, when it has any, so a lowering is never added without a change entry)
# Decision: TODO 1.10 (and its reads, when it is not "both", so a rule never changes what it reads without a change entry)
def rule_fingerprint(rule: SafetyRule) -> str:
    """The hex sha256 of the UTF-8 of json.dumps({"response": ..., "triggers": [...], "words_shown": ...}) with sorted
    keys, separators (",", ":") and no \\u escapes, plus a "lowered_for" list of {"signed_off", "role", "response", "words"}
    when the rule has lowerings, plus "reads" when it is not "both": a rule's fingerprint changes when any of these does, and
    when nothing else does (its title, sources and change log are not in it); a rule with no lowerings and reads "both" keeps
    the fingerprint it had before SC-020."""
    fields: dict = {"triggers": list(rule.triggers), "words_shown": rule.words_shown, "response": rule.response}
    if rule.lowered_for:
        fields["lowered_for"] = [{"signed_off": lowering.signed_off, "role": lowering.role,
                                  "response": lowering.response, "words": lowering.words} for lowering in rule.lowered_for]
    if rule.reads != "both":
        fields["reads"] = rule.reads
    canonical = json.dumps(fields, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


# Decision: SC-016 (a rule changed since its last log entry is refused: the latest entry's fingerprint must match)
def fingerprint_problem(rule: SafetyRule) -> str | None:
    """None when the rule's latest change carries the rule's current fingerprint; otherwise what to do, e.g.
    "SR-03: the rule changed since its last change entry; add an entry and its fingerprint (SC-016)"."""
    if rule.changes[-1].fingerprint == rule_fingerprint(rule):
        return None
    return (f"{rule.rule_id}: the rule changed since its last change entry, or that entry has no matching fingerprint; "
            f"add an entry and set its fingerprint to {rule_fingerprint(rule)} (SC-016)")


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
    unlogged = [problem for problem in map(fingerprint_problem, loaded_rules) if problem]
    if unlogged:
        raise ValueError(f"{rules_path}: {unlogged[0]}")
    if "come first" not in loaded_rules[0].title:
        raise ValueError(f"{rules_path}: {PROCEDURES_FIRST_RULE_ID} is the rule that the site's own safety procedures come first")
    return loaded_rules


# Invariant: HAD-04 (a trigger matches a text only as a whole word or whole phrase, never inside a longer word)
def trigger_pattern(trigger: str) -> re.Pattern:
    """The pattern for one trigger: case-insensitive, with no letter, digit or underscore touching either end, and any
    run of spaces or line breaks inside a phrase counting as one space. "live" matches "Live view" and "go live" but not
    "deliver" or "alive"; "open the pairs" matches "open the\npairs"."""
    words = r"\s+".join(re.escape(word) for word in trigger.split())
    return re.compile(r"(?<!\w)" + words + r"(?!\w)", re.IGNORECASE)


# Invariant: HAD-04 (a rule fires on a whole-word trigger match, so the walker stops on it)
def rules_fired(text: str, loaded_rules: tuple[SafetyRule, ...] | None = None) -> list[str]:
    """The ids, in rule order, of the rules with a trigger that occurs in text as a whole word or phrase, e.g.
    rules_fired("Open the inverter cover") gives ["SR-04"]; "undamaged" fires nothing. Rules default to load_rules()."""
    for_rules = load_rules() if loaded_rules is None else loaded_rules
    return [rule.rule_id for rule in for_rules
            if any(trigger_pattern(trigger).search(text) for trigger in rule.triggers)]
