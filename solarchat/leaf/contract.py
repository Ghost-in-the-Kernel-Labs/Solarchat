"""The types every module shares: a passage and its reference, a reply and its three kinds, admission, and a safety rule.

Built from docs/CONTRACT.md; each type cites the invariant it holds. Standard library only (HAD-01).
"""
import re
from dataclasses import dataclass
from enum import Enum

SAFETY_RULE_ID_PATTERN = re.compile(r"^SR-\d{2}$")


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
    """The three things Hadley may say (HAD-03): an answer, "I do not know", or a stop."""

    ANSWER = "answer"
    DO_NOT_KNOW = "do not know"
    STOP = "stop"


@dataclass(frozen=True)
class Reply:
    """One reply, refused at construction when its kind and the passages or rule it names disagree.

    Invariant: HAD-03 (an answer names at least one admitted passage; "do not know" and a stop name none).
    Invariant: HAD-04 (a stop names the safety rule that fired; the rules are the safety module's, never a pack's).
    Reply(ReplyKind.ANSWER, "Join plus to plus.", (PassageRef("seed-mc4-leads", "step-06"),)) is an answer;
    Reply(ReplyKind.ANSWER, "Join plus to plus.", ()) raises ValueError.
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


def reply_problem(reply: Reply) -> str | None:
    """What makes a reply impossible, or None: an answer with no sources gives "an answer names at least one passage"."""
    if reply.kind is ReplyKind.ANSWER and not reply.passage_refs:
        return "an answer names at least one passage (HAD-03)"
    if reply.kind is not ReplyKind.ANSWER and reply.passage_refs:
        return f"a {reply.kind.value} reply names no passage (HAD-03)"
    if (reply.kind is ReplyKind.STOP) != bool(reply.safety_rule_id):
        return "a stop, and only a stop, names the safety rule that fired (HAD-04)"
    return None


def is_admitted(manifest: dict) -> bool:
    """Whether a pack may answer: its manifest names who admitted it and when.

    Invariant: HAD-06 (a pack that is not admitted is never used to answer).
    {"admitted_by": "A. Engineer", "admitted_on": "2026-12-01"} gives True; the demo pack's nulls give False.
    """
    return bool(manifest.get("admitted_by")) and bool(manifest.get("admitted_on"))


@dataclass(frozen=True)
class SafetyRuleSource:
    """A public source a safety rule rests on: SafetyRuleSource("OSHA: Solar Energy, Falls", "https://www.osha.gov/green-jobs/solar/falls")."""

    title: str
    url: str


@dataclass(frozen=True)
class SafetyRule:
    """One of the project's own fixed safety rules (`solarchat/safety/rules.json`), refused at construction when incomplete.

    Invariant: HAD-04 (a rule sits outside every pack; it has an id SR-nn, the words the worker is shown, the words that
    make it apply, and at least one public source).
    SafetyRule("SR-01", "Site first", "Always.", ("site procedure",), "Stop. Go to your site supervisor or engineer.",
    (SafetyRuleSource("HSE", "https://www.hse.gov.uk/"),)) stands; the same with triggers=() raises ValueError.
    """

    rule_id: str
    title: str
    applies_when: str
    triggers: tuple[str, ...]
    words_shown: str
    sources: tuple[SafetyRuleSource, ...]
    ghost_to_confirm: str | None = None

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
    return None
