"""The types every module shares: a passage and its reference, a reply and its three kinds, and admission.

Built from docs/CONTRACT.md; each type cites the invariant it holds. Standard library only (HAD-01).
"""
from dataclasses import dataclass
from enum import Enum


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
