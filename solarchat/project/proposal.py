"""A profile proposal is kept only where the worker's own message supports it (SC-028; the design's section 3 (1)).

The model proposes; this reads the worker's words by the chat's own word matching (`read_role`, `read_signed_off`) and drops
what they do not say, so a question about a task, "ok what next", or a sign-off the worker never named proposes nothing. The
orchestrator's helper for chat.py. Never calls the model.
"""
import re
from dataclasses import dataclass

from solarchat.leaf.contract import Profile
from solarchat.project.reading import read_role, read_signed_off
from solarchat.safety.rules import trigger_pattern

HAND_OVER = ("taking over", "take over", "is here", "now typing", "someone else", "hand over", "handing over", "new person",
             "my supervisor", "my boss", "my engineer")
FIRST_PERSON = ("i", "im")
SIGN_OFF_WORDS = ("signed off", "sign off", "sign-off", "signed-off", "certified")
I_AM = ("i am", "im", "i m")


@dataclass(frozen=True)
class Proposal:
    """A proposal as the chat settles it, the same fields as the answerer's (the model's record is not an entry point, MOD-04):
    Proposal("qualified", frozenset({"battery"})) is "make me an electrician signed off for battery wiring"."""

    role: str | None = None
    add: frozenset[str] = frozenset()
    remove: frozenset[str] = frozenset()
    new_person: bool = False


def says_hand_over(message: str) -> bool:
    """Whether the message holds a hand-over phrase, whole words: "My supervisor is taking over" is True, "ok what next" is not."""
    return any(trigger_pattern(phrase).search(message) for phrase in HAND_OVER)


def speaks_for_self(message: str) -> bool:
    """Whether the message is in the first person: "I'm the site electrician now" is, "what torque for the terminals?" is not."""
    return bool(set(re.findall(r"[a-z]+", message.lower().replace("'", ""))) & set(FIRST_PERSON))


# Decision: SC-028 (the model's reading is kept only where the worker's message says it; SC-026's guard applied to the proposal too)
def checked_proposal(change: object, message: str, profile: Profile) -> Proposal | None:
    """The proposal the message supports, or None. Examples: ProfileChange(add={"connector"}) for "what torque for the
    terminals?" gives None; new_person for "ok what next" gives None; new_person for "I'm the site electrician now, signed off
    for battery wiring" gives Proposal("qualified", {"battery"}) (this person's change, asked, not a new person); new_person
    for "my supervisor is taking over" is kept. A role stays only when read_role(message) gives it, an added sign-off only
    when read_signed_off(message) names it; a proposal left with nothing, or that changes nothing for the profile, is None."""
    said_role, said_off = read_role(message), read_signed_off(message)
    role, add, remove = change.role, change.add, change.remove  # type: ignore[attr-defined]
    if change.new_person:  # type: ignore[attr-defined]
        if says_hand_over(message):
            return Proposal(new_person=True)
        if not (speaks_for_self(message) and said_role):
            return None
        role, add, remove = said_role, said_off, frozenset()
    kept = Proposal(role if role is not None and role == said_role and role != profile.role else None,
                    (add & said_off) - profile.signed_off, remove & profile.signed_off)
    return kept if (kept.role or kept.add or kept.remove) else None


# Decision: SC-028 (when the model proposes nothing, the chat reads the worker's own statement; a raise is still asked)
def said_proposal(message: str, profile: Profile) -> Proposal | None:
    """The proposal the worker's own words make when the model made none, or None: "My supervisor is here, she's taking over"
    gives Proposal(new_person=True); "I am signed off for all of them" gives the sign-offs the profile lacks; "I'm the site
    electrician now" gives Proposal("qualified"); "I need an engineer" or "I am at the battery step" gives None (a role needs
    "I am" or "I'm", a sign-off needs the words "signed off" or "certified")."""
    if says_hand_over(message):
        return Proposal(new_person=True)
    lowered = " " + " ".join(re.findall(r"[a-z]+", message.lower().replace("'", ""))) + " "
    if not any(f" {phrase} " in lowered for phrase in I_AM):
        return None
    said_role = read_role(message)
    said_off = read_signed_off(message) if any(trigger_pattern(word).search(message) for word in SIGN_OFF_WORDS) else frozenset()
    kept = Proposal(said_role if said_role and said_role != profile.role else None, said_off - profile.signed_off)
    return kept if (kept.role or kept.add) else None
