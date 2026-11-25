"""A clearly off-topic question gets the plain line, never the warning (SC-029; Ghost, 2026-11-25).

The model flags a question `off_topic`; the chat believes it only for a reply that is "I do not know" and a message that is not
about the work by plain word matching (a safety rule's trigger or holds word, a word of the equipment's make or model, or a work
word), so a wrong flag never removes the warning from a work question. The orchestrator's helper for chat.py; never the model.
"""
import re
from dataclasses import replace

from solarchat.leaf.contract import DEMO_BANNER, Equipment, Reply, ReplyKind, SafetyRule
from solarchat.safety.rules import rules_fired, topic_fired, trigger_pattern

OFF_TOPIC_TEXT = "That's outside what I can help with. I can help with setting up and fixing the equipment I listed at the start."
WORK_WORDS = ("solar", "panel", "panels", "controller", "charger", "battery", "inverter", "connector", "cable", "wire", "lead", "leads",
              "voltage", "volts", "amps", "fuse", "switch", "isolator", "roof", "install", "wiring", "connect", "power", "charge",
              "display", "light", "error", "fault", "terminal")
FILLER = ("the", "and", "with", "for", "any", "general", "steps")  # words of an equipment's name that say nothing about equipment


def equipment_words(equipment: tuple[Equipment, ...]) -> tuple[str, ...]:
    """The words of the equipment's makes and models, three characters or more, never "any" or a filler word:
    Equipment("m", "controller", "Victron Energy", "SmartSolar MPPT 75/10", ()) gives ("victron", "energy", "smartsolar", "mppt")."""
    found = (word for entry in equipment for word in re.findall(r"[a-z0-9]+", f"{entry.make} {entry.model}".lower()))
    return tuple(dict.fromkeys(word for word in found if len(word) >= 3 and word not in FILLER))


def about_the_work(message: str, equipment: tuple[Equipment, ...], rules: tuple[SafetyRule, ...]) -> bool:
    """Whether a message may be about the work: it holds a trigger or a holds word of any rule, a word of the equipment's names, or
    a work word: "how do I wire the inverter?" is, "what is the weather like?" is not, "Is it sunny and what do I do?" is not."""
    return bool(rules_fired(message, rules) or topic_fired(message, rules)
                or any(trigger_pattern(word).search(message) for word in (*equipment_words(equipment), *WORK_WORDS)))


# Decision: SC-029 (the plain line only for an "I do not know" the model flagged off topic and the words do not tie to the work; else the warning stays)
def plain_if_off_topic(reply: Reply, flagged: bool, message: str, equipment: tuple[Equipment, ...], rules: tuple[SafetyRule, ...]) -> Reply:
    """The reply to show: an "I do not know" flagged off topic, for a message not about the work, is the same reply with the words
    OFF_TOPIC_TEXT (the demo banner kept, no passage and no rule); every other reply is unchanged, the warning with it."""
    if not flagged or reply.kind is not ReplyKind.DO_NOT_KNOW or about_the_work(message, equipment, rules):
        return reply
    return replace(reply, text=(DEMO_BANNER + "\n\n" if reply.text.startswith(DEMO_BANNER) else "") + OFF_TOPIC_TEXT)
