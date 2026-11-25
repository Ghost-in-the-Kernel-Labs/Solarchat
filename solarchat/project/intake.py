"""The equipment intake: after the profile the chat says what the packs cover, asks for the make and model, and says back the
match (TODO 2.14; SC-027, docs/designs/equipment-intake.md).

The orchestrator's helper for chat.py: the list and the question are fixed words (no model call); the answer is read by the
answerer's `identify` when it has one, else by word matching; the chat keeps only an entry actually on the list. Choosing
equipment unlocks no safety rule, so SC-020's word-matching guard is not needed here (Ghost, 2026-11-23).
"""
import re
from collections.abc import Callable
from typing import TextIO

from solarchat.leaf.contract import EQUIPMENT_KINDS, Answerer, Equipment
from solarchat.model.claude import ModelError
from solarchat.packs.load import Pack
from solarchat.project.speech import Speaker

LIST_HEADING = "I can help with:"
QUESTION = ("What is the make and model of your panel, and of your charge controller or power station? "
            "Say 'not sure' if you don't know.")
WRONG = "If that is wrong, say so at any point."
PANEL_QUESTION = "And the panel's make and model? Say 'not sure' if you don't know."
HELP_QUESTION = ("That's fine. Look for a label on the back of the panel and on the front of the controller or power station, "
                 "and tell me any names you see.")
NO_PACK = "I have no pack for that equipment."
ONLY_LISTED = "I can only help with the equipment listed above."
NOT_SURE = ("not sure", "unsure", "dont know", "do not know", "no idea", "idk")
Ask = Callable[[str, TextIO, TextIO, Speaker | None], str]


def equipment_name(entry: Equipment) -> str:
    """The words for an entry: Equipment("r600", "power-station", "EcoFlow", "R600", ("S8",)) gives "EcoFlow R600"; an "any" make
    gives the model's words alone: "MC4 and MC4-compatible connectors"."""
    return entry.model if entry.make == "any" else f"{entry.make} {entry.model}"


# Decision: SC-027 (an id clash between packs is refused at start, since the id is what a match and --equipment name)
def equipment_of(packs: tuple[Pack, ...]) -> tuple[Equipment, ...]:
    """Every entry of the packs switched on, in order; an id in two packs raises ValueError in words:
    equipment_of((a, b)) with "r600" in both gives "equipment id 'r600' is in both a and b"."""
    owner: dict[str, str] = {}
    for pack in packs:
        for entry in pack.equipment:
            if entry.id in owner:
                raise ValueError(f"equipment id {entry.id!r} is in both {owner[entry.id]} and {pack.pack_id}")
            owner[entry.id] = pack.pack_id
    return tuple(entry for pack in packs for entry in pack.equipment)


def list_text(equipment: tuple[Equipment, ...]) -> str:
    """What the packs cover, one line per entry, grouped by kind: "I can help with:\\n- Victron Energy SmartSolar MPPT 75/10 to
    100/20\\n- EcoFlow R600"."""
    ordered = sorted(equipment, key=lambda entry: EQUIPMENT_KINDS.index(entry.kind))  # stable: the pack's order within a kind
    return "\n".join([LIST_HEADING] + [f"- {equipment_name(entry)}" for entry in ordered])


def general_entry(equipment: tuple[Equipment, ...]) -> Equipment | None:
    """The general entry, the first panel with the make "any", or None when the packs hold none."""
    return next((entry for entry in equipment if entry.make == "any" and entry.kind == "panel"), None)


def said_back(matched: tuple[Equipment, ...], equipment: tuple[Equipment, ...]) -> str:
    """The match in words: one match gives "Working with: Victron Energy SmartSolar MPPT 75/10 to 100/20. If that is wrong, say
    so at any point."; none gives "I have no pack for that equipment. I can give the general steps for crystalline silicon
    panels with MC4 leads; where your maker's manual says otherwise, follow the manual." (the general entry's words), or "I can
    only help with the equipment listed above." when the packs hold no general entry."""
    if matched:
        return f"Working with: {'; '.join(equipment_name(entry) for entry in matched)}. {WRONG}"
    general = general_entry(equipment)
    if general is None:
        return f"{NO_PACK} {ONLY_LISTED}"
    words = re.sub(r"\s*\([^)]*\)$", "", general.model)  # "Crystalline silicon panels with MC4 leads (the general steps)"
    words = words[0].lower() + words[1:]
    return f"{NO_PACK} I can give the general steps for {words}; where your maker's manual says otherwise, follow the manual."


def is_not_sure(text: str) -> bool:
    """Whether an answer says nothing about the equipment: "", "not sure" and "I don't know" are; "Victron" is not."""
    plain = " ".join(re.findall(r"[a-z]+", text.lower().replace("'", "")))
    return not plain or any(phrase in plain for phrase in NOT_SURE)


def word_match(text: str, equipment: tuple[Equipment, ...]) -> tuple[Equipment, ...]:
    """The stub's reading: an entry matches when the answer holds, as a whole word of four letters or more (lowercased), a word of
    its make other than "any" or the first word of its model: "Victron SmartSolar 75/10" matches the Victron entry, "my
    panel" matches nothing, and "any" never matches an "any" make."""
    heard = {word for word in re.findall(r"[a-z0-9]+", text.lower()) if len(word) >= 4}
    def names(entry: Equipment) -> set[str]:
        words = [] if entry.make == "any" else re.findall(r"[a-z0-9]+", entry.make.lower())
        return {word for word in words + re.findall(r"[a-z0-9]+", entry.model.lower())[:1] if len(word) >= 4}
    return tuple(entry for entry in equipment if names(entry) & heard)


def read_answer(text: str, equipment: tuple[Equipment, ...], answerer: Answerer) -> tuple[Equipment, ...]:
    """The entries an answer names: "not sure" is no match with no call; an answerer with `identify` reads it (a ModelError is no
    match, and an id off the list is dropped); one without is read by word matching."""
    if is_not_sure(text):
        return ()
    reader = getattr(answerer, "identify", None)
    if reader is None:
        return word_match(text, equipment)
    try:
        named = reader(text, equipment)
    except ModelError:
        return ()
    return tuple(entry for entry in equipment if entry.id in named)


def parse_option(text: str, equipment: tuple[Equipment, ...]) -> tuple[Equipment, ...]:
    """The --equipment value: "victron-smartsolar-mppt,ecoflow-r600" gives both entries, "none" gives (); an id that is not on
    the list raises ValueError naming the offered ids (a pack with no list: "no pack lists any equipment")."""
    names = [name.strip().lower() for name in text.split(",") if name.strip()]
    offered = {entry.id: entry for entry in equipment}
    if not offered:
        raise ValueError("no pack lists any equipment, so --equipment has nothing to name")
    unknown = [name for name in names if name not in offered and name != "none"]
    if unknown or not names:
        raise ValueError(f"{', '.join(unknown) or 'an empty value'} is not equipment on the list; the ids are {', '.join(offered)}, or none")
    return tuple(offered[name] for name in names if name != "none")


def tell(line: str, stdout: TextIO, speaker: Speaker | None) -> None:
    """Show a line, then speak it."""
    stdout.write(line + "\n\n")
    if speaker:
        stdout.flush()
        speaker.say(line)


# Decision: SC-029 (a controller named with no panel asks for the panel once; "not sure" first gets one helping question, two misses the no-match line)
def run_intake(equipment: tuple[Equipment, ...], chosen: tuple[Equipment, ...] | None, answerer: Answerer, stdin: TextIO,
               stdout: TextIO, speaker: Speaker | None, ask: Ask) -> tuple[Equipment, ...]:
    """The intake: the list, the question, the reading and the said-back line, and the entries matched. `chosen` (from
    --equipment) skips the list, the question and the reading. A pack list that is empty is no intake: the answer is (). A first
    answer of "not sure" is asked the helping question once and its answer read as the first; a controller matched with no panel is
    asked for the panel once, and "not sure" keeps the general steps: "victron" gives the Victron entry, then "a Solarex 300" adds
    no panel (the said-back line is "Working with: Victron ...")."""
    if not equipment:
        return ()
    if chosen is None:
        tell(list_text(equipment), stdout, speaker)
        typed = ask(QUESTION, stdin, stdout, speaker)
        chosen = read_answer(typed, equipment, answerer)
        if not chosen and is_not_sure(typed):
            chosen = read_answer(ask(HELP_QUESTION, stdin, stdout, speaker), equipment, answerer)
        panels = tuple(entry for entry in equipment if entry.kind == "panel")
        if panels and any(entry.kind == "controller" for entry in chosen) and not any(entry.kind == "panel" for entry in chosen):
            chosen += tuple(entry for entry in read_answer(ask(PANEL_QUESTION, stdin, stdout, speaker), panels, answerer) if entry not in chosen)
    tell(said_back(chosen, equipment), stdout, speaker)
    return chosen
