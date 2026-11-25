"""What the chat shows and says of a reply: the spoken text, the rule's label and words, and the lowered warn's short form (SC-020, SC-029).

Moved out of chat.py to keep that file under 400 lines; `solarchat.project.chat` still names each function. The orchestrator's
helper: it reads the safety module's rules and the leaf, never the model.
"""
from solarchat.answer.door import STILL_STOPPED
from solarchat.leaf.contract import DEFAULT_PROFILE, DEMO_BANNER, SAFETY_RESPONSES, Profile, Reply, ReplyKind
from solarchat.safety.rules import load_rules

SOURCES_MARK = "\n\nFrom: "
# Decision: SC-029 (a lowering reads as the worker's sign-off being relied on, never as safety being reduced)
LOWERED_MARK = " (you are signed off for this work)"
LOWERED_REMINDER = "The precautions above still apply."


def spoken(reply: Reply) -> str:
    """What the assistant said, as the history keeps it: the reply without its demo banner and its "From:" lines:
    "DEMO: ...\\n\\nJoin plus to plus.\\n\\nFrom: Step 6 (Pack): Manual, page 15" gives "Join plus to plus."."""
    text = reply.text.removeprefix(DEMO_BANNER).strip()
    return text.split(SOURCES_MARK)[0].strip() if SOURCES_MARK in text else text


def rule_label(reply: Reply, profile: Profile = DEFAULT_PROFILE) -> tuple[str, str]:
    """The rule a warn or a stop names, as ("Safety rule SR-03", "<words>"), or ("", "") for any other reply; a rule the
    profile lowered says so: ("Safety rule SR-11 (you are signed off for this work)", "<the lowering's words>") (SC-020)."""
    if reply.kind not in (ReplyKind.WARN, ReplyKind.STOP) or not reply.safety_rule_id:
        return "", ""
    rule = {rule.rule_id: rule for rule in load_rules()}.get(reply.safety_rule_id)
    if rule is None:
        return f"Safety rule {reply.safety_rule_id}", ""
    matching = [lowering for lowering in rule.lowered_for if lowering.matches(profile)]
    if not matching:
        return f"Safety rule {reply.safety_rule_id}", rule.words_shown
    # the door's choice (SC-020): the lowest response of the matching lowerings, whose words the warn then shows
    lowest = min(matching, key=lambda lowering: SAFETY_RESPONSES.index(lowering.response))
    return f"Safety rule {reply.safety_rule_id}{LOWERED_MARK}", lowest.words


def rule_words(reply: Reply, profile: Profile = DEFAULT_PROFILE) -> str:
    """The words of the rule a warn or a stop names, "Safety rule SR-03: <words>", or "" for any other reply."""
    label, words = rule_label(reply, profile)
    return f"{label}: {words}" if words else label


def is_lowered(reply: Reply, profile: Profile = DEFAULT_PROFILE) -> bool:
    """Whether the reply is a warn or a stop a lowering of the profile has changed: SR-11 for a battery sign-off is, SR-03 for the
    default profile is not."""
    return rule_label(reply, profile)[0].endswith(LOWERED_MARK)


# Decision: SC-029 (the lowering's precautions are shown in full once per rule; after that the label and "The precautions above still apply.")
def with_rule(reply: Reply, text: str, profile: Profile = DEFAULT_PROFILE, shown: frozenset[str] | set[str] = frozenset()) -> str:
    """`text` under the rule's heading: the door puts the rule's words inside the reply text since 1.9, so then only the
    label ("Safety rule SR-03") goes above it, and so does a held stop's short text (SC-028); a reply recorded without them keeps "Safety rule SR-03: <words>" above.
    A lowered warn whose rule is in `shown` (its precautions were shown already) puts "The precautions above still apply." where the
    words were: with_rule(warn, "Words.\\n\\nAnswer.", engineer, {"SR-11"}) gives "Safety rule SR-11 (you are signed off for this work)\\n\\nThe
    precautions above still apply.\\n\\nAnswer." (the words being "Words.")."""
    label, words = rule_label(reply, profile)
    if not label:
        return text
    if label.endswith(LOWERED_MARK) and reply.safety_rule_id in shown:
        return f"{label}\n\n" + (text.replace(words, LOWERED_REMINDER, 1) if words in text else f"{LOWERED_REMINDER}\n\n{text}")
    return f"{label}\n\n{text}" if not words or words in text or STILL_STOPPED in text else f"{rule_words(reply, profile)}\n\n{text}"


def render(reply: Reply, profile: Profile = DEFAULT_PROFILE, shown: frozenset[str] | set[str] = frozenset()) -> str:
    """The reply as shown: the rule's label (and its words, when the text lacks them) first for a warn or a stop, then the
    door's text (which holds the demo banner and the citations): a plain answer renders as its own text."""
    return with_rule(reply, reply.text, profile, shown)


def spoken_aloud(reply: Reply, profile: Profile = DEFAULT_PROFILE, shown: frozenset[str] | set[str] = frozenset()) -> str:
    """What --voice reads aloud for a reply: the rule's label first for a warn or a stop, then the reply's words once,
    never the banner or the "From:" lines (the banner is spoken once, at the start)."""
    return with_rule(reply, spoken(reply), profile, shown)
