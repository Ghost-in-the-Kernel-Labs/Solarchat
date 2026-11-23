"""A stop holds for the rest of the conversation (SC-028; docs/designs/sticky-stops-and-proposal-guards.md section 2).

The chat keeps the ids of the stops it has shown, the held set. Each later reply that is not itself a stop or an emergency is
checked against the held rules' topic words (a rule's `holds`, else its triggers), in the worker's message, the reply's text and
the cited passages; a hit replaces the reply with the held stop. Plain word matching through the safety module's matcher, never
the model. The orchestrator's helper for chat.py; the held set is plain data the chat owns.
"""
from solarchat.answer.door import held_stop
from solarchat.leaf.contract import Profile, Reply, ReplyKind, SafetyRule
from solarchat.packs.load import Pack
from solarchat.safety.rules import topic_fired


# Decision: SC-028 (only a stop is held; an emergency stands alone and a warn holds nothing)
def stop_shown(reply: Reply, rules: tuple[SafetyRule, ...]) -> str | None:
    """The id of the rule whose stop a reply is, or None: a STOP naming SR-11 gives "SR-11"; an emergency (SR-08), a warn, an
    answer and "I do not know" give None."""
    if reply.kind is not ReplyKind.STOP or not reply.safety_rule_id:
        return None
    named = {rule.rule_id: rule for rule in rules}.get(reply.safety_rule_id)
    return reply.safety_rule_id if named is not None and named.response == "stop" else None


# Decision: SC-028 (a hold leaves only when the profile changes so that the rule is lowered for it, SC-026; a new person starts again)
def kept_holds(held: set[str], profile: Profile, rules: tuple[SafetyRule, ...], new_person: bool = False) -> set[str]:
    """The held ids once the profile is this one: {"SR-11"} for a profile signed off for battery work gives set(), for a new
    worker gives {"SR-11"}; someone new typing gives set() whatever they hold."""
    if new_person:
        return set()
    lowered = {rule.rule_id for rule in rules if any(lowering.matches(profile) for lowering in rule.lowered_for)}
    return held - lowered


def held_names(held: set[str], rules: tuple[SafetyRule, ...]) -> tuple[tuple[str, str], ...]:
    """The (id, topic) pairs the answerer is told, in rule order: {"SR-11"} gives (("SR-11", "batteries"),) (the rule's title,
    first letter lowercase)."""
    return tuple((rule.rule_id, rule.title[0].lower() + rule.title[1:]) for rule in rules if rule.rule_id in held)


def reply_texts(question: str, reply: Reply, pack: Pack) -> str:
    """The words a held topic is looked for in: the worker's message, the reply's text and the title and text of each passage
    the reply cites."""
    cited = [passage for passage in pack.passages if passage.ref in reply.passage_refs]
    return "\n".join([question, reply.text, *(f"{passage.title}\n{passage.text}" for passage in cited)])


# Decision: SC-028 (a reply that is not a stop, and names a held topic anywhere, is the held stop again)
def enforce_holds(reply: Reply, held: set[str], question: str, pack: Pack, demo: bool, rules: tuple[SafetyRule, ...]) -> Reply:
    """The reply to show: with SR-11 held, "no" answered "Did you connect the battery to the controller?" gives the SR-11 held
    stop ("This is still stopped for you. ..."); "what is an MC4 connector?" answered with a reply naming no battery word is
    unchanged; a stop or an emergency is never replaced. Several held rules fire: the lowest id answers."""
    if not held or reply.kind is ReplyKind.STOP:
        return reply
    fired = topic_fired(reply_texts(question, reply, pack), tuple(rule for rule in rules if rule.rule_id in held))
    return held_stop(next(rule for rule in rules if rule.rule_id == fired[0]), demo) if fired else reply
