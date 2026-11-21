"""The types every module shares: a passage and its reference, a reply and its four kinds, a pack's status, and a safety rule.

Built from docs/CONTRACT.md; each type cites the invariant it holds. Standard library only (HAD-01).
"""
import re
from dataclasses import dataclass
from datetime import date
from enum import Enum

SAFETY_RULE_ID_PATTERN = re.compile(r"^SR-\d{2}$")
SAFETY_RESPONSES = ("warn", "stop", "emergency")
CHANGE_FIELDS = ("date", "by", "role", "why", "evidence")


@dataclass(frozen=True)
class PassageRef:
    """Where an answer's words come from: PassageRef("seed-mc4-leads", "step-06")."""

    pack_id: str
    passage_id: str


@dataclass(frozen=True)
class Passage:
    """A pack's text, held as data and only ever quoted, never followed.

    Invariant: HAD-05 (a pack's text is data, never instructions; no field here is read as an instruction).
    """

    ref: PassageRef
    text: str


class ReplyKind(Enum):
    """The four things Hadley may say (HAD-03): an answer, "I do not know", a stop, or a warn (SC-015)."""

    ANSWER = "answer"
    DO_NOT_KNOW = "do not know"
    STOP = "stop"
    WARN = "warn"


@dataclass(frozen=True)
class Reply:
    """One reply, refused at construction when its kind and the passages or rule it names disagree.

    Invariant: HAD-03 (an answer or a warn names at least one admitted passage; "do not know" and a stop name none).
    Invariant: HAD-04 (a stop or a warn names the safety rule that fired; the rules are the safety module's, never a pack's).
    A warn carries the rule's words and the passage of the step the walk continues with; a stop and an emergency are
    both a STOP naming the rule (SC-015).
    Reply(ReplyKind.ANSWER, "Join plus to plus.", (PassageRef("seed-mc4-leads", "step-06"),)) is an answer;
    Reply(ReplyKind.ANSWER, "Join plus to plus.", ()) raises ValueError;
    Reply(ReplyKind.WARN, "Never pull connectors apart under load.", (PassageRef("seed-mc4-leads", "step-12"),), "SR-03")
    is a warn, and the same with no passage or no rule raises ValueError.
    """

    kind: ReplyKind
    text: str
    passage_refs: tuple[PassageRef, ...] = ()
    safety_rule_id: str | None = None

    def __post_init__(self) -> None:
        """Raise ValueError when the reply breaks HAD-03 or HAD-04 (the examples are in the class docstring)."""
        contract_breach = reply_problem(self)
        if contract_breach:
            raise ValueError(contract_breach)


# Decision: SC-015 (a warn names its rule and the passage it continues with: the smallest change to HAD-03 and HAD-04)
def reply_problem(reply: Reply) -> str | None:
    """What makes a reply impossible, or None: an answer with no sources gives "an answer or a warn names at least one
    passage"; a warn with passages and a rule gives None."""
    names_passage = reply.kind in (ReplyKind.ANSWER, ReplyKind.WARN)
    if names_passage and not reply.passage_refs:
        return "an answer or a warn names at least one passage (HAD-03)"
    if not names_passage and reply.passage_refs:
        return f"a {reply.kind.value} reply names no passage (HAD-03)"
    if (reply.kind in (ReplyKind.STOP, ReplyKind.WARN)) != bool(reply.safety_rule_id):
        return "a stop or a warn, and only they, name the safety rule that fired (HAD-04)"
    return None


def may_answer(manifest: dict, demo_mode: bool) -> bool:
    """Whether a pack may answer now: a field pack always, a demo pack only in demo mode, any other status never.

    Fails closed: a status this function does not know (missing, empty, misspelled, or not a string) never answers.
    Decision: SC-013 (a pack is a field pack or a demo pack).
    Invariant: HAD-06 (a demo pack never answers outside demo mode).
    {"status": "field"} gives True in either mode; {"status": "demo"} gives demo_mode; {"status": "library"} gives False.
    """
    status = manifest.get("status")
    if status == "field":
        return True
    if status == "demo":
        return demo_mode
    return False


@dataclass(frozen=True)
class SafetyRuleSource:
    """A public source a safety rule rests on: SafetyRuleSource("OSHA: Solar Energy, Falls", "https://www.osha.gov/green-jobs/solar/falls")."""

    title: str
    url: str


@dataclass(frozen=True)
class SafetyRuleChange:
    """One entry of a safety rule's change log: SafetyRuleChange("2026-11-21", "Ghost", "maintainer", "Connecting is daily
    work.", "J-032"). Only the rule's latest entry carries a fingerprint, the sha256 the safety check compares.

    Decision: SC-016 (each change names who, in what role, why and on what evidence).
    """

    date: str
    by: str
    role: str
    why: str
    evidence: str
    fingerprint: str | None = None


@dataclass(frozen=True)
class SafetyRule:
    """One of the project's own fixed safety rules (`solarchat/safety/rules.json`), refused at construction when incomplete.

    Invariant: HAD-04 (a rule sits outside every pack; it has an id SR-nn, the words the worker is shown, the words that
    make it apply, at least one public source, a response and a change log).
    Decision: SC-015 (its response is exactly "warn", "stop" or "emergency").
    Decision: SC-016 (its change log has at least one entry, each with date, by, role, why and evidence).
    SafetyRule("SR-01", "Site first", "Always.", ("site procedure",), "Stop. Go to your site supervisor or engineer.",
    (SafetyRuleSource("HSE", "https://www.hse.gov.uk/"),), "stop", (SafetyRuleChange("2026-11-21", "Ghost", "maintainer",
    "First draft.", "J-027"),)) stands; the same with triggers=(), response="halt" or changes=() raises ValueError.
    """

    rule_id: str
    title: str
    applies_when: str
    triggers: tuple[str, ...]
    words_shown: str
    sources: tuple[SafetyRuleSource, ...]
    response: str
    changes: tuple[SafetyRuleChange, ...]
    engineer_to_confirm: str | None = None

    def __post_init__(self) -> None:
        """Raise ValueError when the rule breaks HAD-04 (the examples are in the class docstring)."""
        rule_breach = safety_rule_problem(self)
        if rule_breach:
            raise ValueError(rule_breach)


def safety_rule_problem(rule: SafetyRule) -> str | None:
    """What makes a safety rule incomplete, or None: a rule with no triggers gives "SR-01: a rule has triggers"."""
    if not SAFETY_RULE_ID_PATTERN.match(rule.rule_id):
        return f"{rule.rule_id!r}: a safety rule's id is SR- and two digits (HAD-04)"
    blank_texts = [name for name, text in (("title", rule.title), ("applies_when", rule.applies_when),
                                           ("words_shown", rule.words_shown)) if not text.strip()]
    if blank_texts:
        return f"{rule.rule_id}: {', '.join(blank_texts)} is empty (HAD-04)"
    if not rule.triggers or any(not trigger.strip() or trigger != trigger.lower() for trigger in rule.triggers):
        return f"{rule.rule_id}: a rule has triggers, each lowercase and not empty (HAD-04)"
    if not rule.sources or any(not source.title.strip() or not source.url.startswith("https://") for source in rule.sources):
        return f"{rule.rule_id}: a rule has at least one source, each with a title and an https address (HAD-04)"
    if rule.response not in SAFETY_RESPONSES:
        return f"{rule.rule_id}: response {rule.response!r} is not one of {', '.join(SAFETY_RESPONSES)} (SC-015)"
    return changes_problem(rule)


# Decision: SC-016 (a rule has a change log; every entry names its date, who, role, why and evidence)
def changes_problem(rule: SafetyRule) -> str | None:
    """What is wrong with a rule's change log, or None: no entry gives "SR-01: a rule has at least one change"; an entry
    with an empty "why" gives "SR-01: change 2 has an empty 'why'"; a date that is not ISO (2026-13-40) is refused too."""
    if not rule.changes:
        return f"{rule.rule_id}: a rule has at least one change (SC-016)"
    for number, change in enumerate(rule.changes, start=1):
        empty = [name for name in CHANGE_FIELDS if not getattr(change, name).strip()]
        if empty:
            return f"{rule.rule_id}: change {number} has an empty {empty[0]!r} (SC-016)"
        try:
            date.fromisoformat(change.date)
        except ValueError:
            return f"{rule.rule_id}: change {number} has a date that is not ISO, YYYY-MM-DD (SC-016)"
    return None
