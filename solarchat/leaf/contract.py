"""The types every module shares: a passage and its reference, a reply and its four kinds, a pack's status, and a safety rule.

Built from docs/CONTRACT.md; each type cites the invariant it holds. Standard library only (HAD-01).
"""
import re
from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Protocol

SAFETY_RULE_ID_PATTERN = re.compile(r"^SR-\d{2}$")
SAFETY_RESPONSES = ("warn", "stop", "emergency")
CHANGE_FIELDS = ("date", "by", "role", "why", "evidence")
# Decision: SC-024 (a pack's declaration of coverage says who declared it, in SC-016's shape; SR-08 and SR-09 stay emergencies)
DECLARED_FIELDS = ("by", "role", "date", "evidence")
COVERAGE_RESPONSES = ("warn", "stop")
EMERGENCY_RULE_IDS = ("SR-08", "SR-09")
# Decision: SC-020 (who the bot is talking to: a role and the sign-offs the worker's supervisor has given, self-declared)
PROFILE_ROLES = ("new", "crew", "qualified")
PROFILE_SIGN_OFFS = ("meter", "connector", "battery", "height")
# Decision: SC-019 (a reply cites at most this many passages; more is an answerer's breach, answered with "I do not know")
MAX_CITED_PASSAGES = 3
# Decision: SC-019 (SC-010's words, one home: every reply shown in demo mode starts with them)
DEMO_BANNER = "DEMO: not reviewed by an engineer, do not use on a site"


@dataclass(frozen=True)
class PassageRef:
    """Where an answer's words come from: PassageRef("seed-mc4-leads", "step-06")."""

    pack_id: str
    passage_id: str


@dataclass(frozen=True)
class Passage:
    """A pack's text, held as data and only ever quoted, never followed.

    Invariant: HAD-05 (a pack's text is data, never instructions; no field here is read as an instruction).
    Decision: SC-019 (it gains a title, shown in a citation; the default keeps Passage(ref, text) valid).
    """

    ref: PassageRef
    text: str
    title: str = ""


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


@dataclass(frozen=True)
class Finding:
    """What an answerer found: Finding((PassageRef("seed-mc4-leads", "step-06"),), "Join plus to plus.", 4.5);
    Finding() is "I do not know". Refs with no text, or text with no refs, raise ValueError.

    Decision: SC-019 (an answerer returns refs, best first, the words to show and its score for refs[0]).
    """

    refs: tuple[PassageRef, ...] = ()
    text: str = ""
    score: float = 0.0

    def __post_init__(self) -> None:
        """Raise ValueError when refs and text do not come together: Finding((), "words") raises."""
        if bool(self.refs) != bool(self.text.strip()):
            raise ValueError("a finding has refs and text together, or neither (SC-019)")


TURN_ROLES = ("user", "assistant")


@dataclass(frozen=True)
class Turn:
    """One turn of the conversation so far: Turn("user", "Which lead is positive?") or Turn("assistant", "Look at the label.").

    Decision: SC-019 (amended 2026-11-21: the door carries the conversation's history, so an answerer can be conversational).
    A role other than "user" or "assistant" raises ValueError.
    """

    role: str
    text: str

    def __post_init__(self) -> None:
        """Raise ValueError for a role that is neither "user" nor "assistant": Turn("system", "x") raises."""
        if self.role not in TURN_ROLES:
            raise ValueError(f"a turn's role is one of {', '.join(TURN_ROLES)}, not {self.role!r} (SC-019)")


class Answerer(Protocol):
    """What the door asks: a short stable `name` ("no-answer") and find(question, passages, history) -> Finding.

    Decision: SC-019 (the door takes its answerer as an argument, so no mode changes the door; amended 2026-11-21: the
    history of the conversation is passed through, and an answerer that is not conversational ignores it).
    """

    name: str

    def find(self, question: str, passages: tuple[Passage, ...], history: tuple[Turn, ...] = ()) -> Finding:
        """The finding for a question among the passages it may use, given the turns so far:
        NoAnswer().find("q", ()) gives Finding()."""
        ...


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
class Profile:
    """Who the bot is talking to, for one chat session: a role and the sign-offs the worker says they hold.

    Decision: SC-020 (role is "new", "crew" or "qualified"; signed_off is a frozenset of "meter", "connector", "battery"
    and "height"; nothing else is held, and the default is the newest contractor, so no profile gives today's replies).
    Profile("qualified", frozenset({"meter"})) stands; Profile("boss", frozenset()), Profile("new", frozenset({"roof"})) or
    a signed_off that is a list raises ValueError.
    """

    role: str
    signed_off: frozenset[str]

    def __post_init__(self) -> None:
        """Raise ValueError when the profile breaks SC-020 (the examples are in the class docstring)."""
        if self.role not in PROFILE_ROLES:
            raise ValueError(f"role {self.role!r} is not one of {', '.join(PROFILE_ROLES)} (SC-020)")
        if not isinstance(self.signed_off, frozenset) or not self.signed_off <= set(PROFILE_SIGN_OFFS):
            raise ValueError(f"signed_off is a frozenset of {', '.join(PROFILE_SIGN_OFFS)} (SC-020)")


DEFAULT_PROFILE = Profile("new", frozenset())


@dataclass(frozen=True)
class SafetyLowering:
    """One way a profile lowers a rule: for a sign-off or a role, the rule gives a lower response with these words instead.

    Decision: SC-020 (exactly one of signed_off or role names the profile answer; response is lower than the rule's own,
    checked with the rule; words replace the rule's words_shown and are the precautions that still apply).
    SafetyLowering("warn", "You are signed off for meter tests: ...", signed_off="meter") stands; the same with both signed_off
    and role, or neither, raises ValueError in the rule that holds it.
    """

    response: str
    words: str
    signed_off: str | None = None
    role: str | None = None

    def matches(self, profile: Profile) -> bool:
        """Whether the profile has the sign-off or the role this names: a "meter" lowering matches Profile("crew",
        frozenset({"meter"})) and not DEFAULT_PROFILE."""
        if self.signed_off is not None:
            return self.signed_off in profile.signed_off
        return self.role == profile.role


# Decision: SC-020 (a lowering is for a stop only; an emergency never lowers; a lowering is lower than its rule and names a known answer)
def lowering_problem(rule_id: str, response: str, lowering: object) -> str | None:
    """What is wrong with one lowering of a rule, or None: a lowering of an emergency rule gives "SR-08: an emergency never
    carries lowered_for (SC-020)"; a "stop" lowering of a "stop" rule gives "... is not lower than the rule's stop (SC-020)"."""
    if not isinstance(lowering, SafetyLowering):
        return f"{rule_id}: lowered_for holds lowerings only (SC-020)"
    if response == "emergency":
        return f"{rule_id}: an emergency never carries lowered_for (SC-020)"
    if (lowering.signed_off is None) == (lowering.role is None):
        return f"{rule_id}: a lowering names exactly one of signed_off or role (SC-020)"
    if lowering.signed_off is not None and lowering.signed_off not in PROFILE_SIGN_OFFS:
        return f"{rule_id}: signed_off {lowering.signed_off!r} is not one of {', '.join(PROFILE_SIGN_OFFS)} (SC-020)"
    if lowering.role is not None and lowering.role not in PROFILE_ROLES:
        return f"{rule_id}: role {lowering.role!r} is not one of {', '.join(PROFILE_ROLES)} (SC-020)"
    if lowering.response not in SAFETY_RESPONSES or SAFETY_RESPONSES.index(lowering.response) >= SAFETY_RESPONSES.index(response):
        return f"{rule_id}: a lowering's response {lowering.response!r} is not lower than the rule's {response} (SC-020)"
    if not isinstance(lowering.words, str) or not lowering.words.strip():
        return f"{rule_id}: a lowering has words (SC-020)"
    return None


@dataclass(frozen=True)
class SafetyRule:
    """One of the project's own fixed safety rules (`solarchat/safety/rules.json`), refused at construction when incomplete.

    Invariant: HAD-04 (a rule sits outside every pack; it has an id SR-nn, the words the worker is shown, the words that
    make it apply, at least one public source, a response and a change log).
    Decision: SC-015 (its response is exactly "warn", "stop" or "emergency").
    Decision: SC-016 (its change log has at least one entry, each with date, by, role, why and evidence).
    Decision: SC-020 (`lowered_for`, default empty, holds the lowerings a profile may apply; an emergency has none).
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
    lowered_for: tuple[SafetyLowering, ...] = ()

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
    for lowering in rule.lowered_for:
        lowered = lowering_problem(rule.rule_id, rule.response, lowering)
        if lowered:
            return lowered
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


@dataclass(frozen=True)
class SafetyCoverage:
    """One declaration in a pack's manifest that its own passages cover a general safety rule, refused at construction
    when incomplete.

    Decision: SC-024 (a make-and-model pack may declare that some of its passages cover the hazard of a rule; the response is
    "warn" or "stop", and for SR-08 and SR-09 only "emergency"; the passages are the pack's own, in the order shown).
    Decision: SC-016 (`declared`, when given, holds by, role, date and evidence, each with something in it; a field pack
    may leave it out, so the default is None).
    SafetyCoverage("SR-02", "warn", ("meter-check-1",), {"by": "Ghost", "role": "maintainer", "date": "2026-11-23",
    "evidence": "J-072"}) stands; the same with passages=(), response="emergency" (for SR-02) or a declared with no "by"
    raises ValueError.
    """

    rule: str
    response: str
    passages: tuple[str, ...]
    declared: dict[str, str] | None = None

    def __post_init__(self) -> None:
        """Raise ValueError when the declaration breaks SC-024 (the examples are in the class docstring)."""
        coverage_breach = safety_coverage_problem(self)
        if coverage_breach:
            raise ValueError(coverage_breach)


def safety_coverage_problem(coverage: SafetyCoverage) -> str | None:
    """What makes a declaration incomplete, or None: a rule that is not SR-nn gives "'X': a covered rule's id is SR- and
    two digits (SC-024)"; SR-08 with the response "warn" gives "SR-08: the response is emergency (SC-024)"."""
    if not isinstance(coverage.rule, str) or not SAFETY_RULE_ID_PATTERN.match(coverage.rule):
        return f"{coverage.rule!r}: a covered rule's id is SR- and two digits (SC-024)"
    allowed = ("emergency",) if coverage.rule in EMERGENCY_RULE_IDS else COVERAGE_RESPONSES
    if coverage.response not in allowed:
        return f"{coverage.rule}: the response is {' or '.join(allowed)}, not {coverage.response!r} (SC-024)"
    if not coverage.passages or any(not isinstance(passage, str) or not passage.strip() for passage in coverage.passages):
        return f"{coverage.rule}: a declaration names at least one passage, each with an id (SC-024)"
    if coverage.declared is None:
        return None
    declared = coverage.declared
    if not isinstance(declared, dict) or any(not isinstance(declared.get(name), str) or not declared[name].strip() for name in DECLARED_FIELDS):
        return f"{coverage.rule}: declared has {', '.join(DECLARED_FIELDS)}, each with something in it (SC-016)"
    return None
