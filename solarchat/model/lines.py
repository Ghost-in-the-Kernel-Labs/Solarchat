"""The lines put in front of the worker's question, never in the cached system block (SC-020, SC-027).

The profile line says who the worker is; the equipment line says what they work with. `messages_for` builds the conversation the
API takes. Standard library and the leaf only.
"""
from solarchat.leaf.contract import PROFILE_SIGN_OFFS, Equipment, Profile, Turn

# Decision: SC-020 (who the worker is, in words, as the answerer is told it and the chat says it back)
ROLE_WORDS = {"new": "new to solar", "crew": "crew member", "qualified": "licensed electrician or engineer"}
SIGN_OFF_WORDS = {"meter": "meter tests", "connector": "connector work", "battery": "battery and controller wiring",
                  "height": "work at height with fall protection"}


def profile_line(profile: Profile) -> str:
    """The one line the answerer is told: Profile("qualified", frozenset({"battery"})) gives "The worker: licensed electrician
    or engineer; signed off for: battery and controller wiring."; no sign-off gives "signed off for: none"."""
    signed = ", ".join(SIGN_OFF_WORDS[name] for name in PROFILE_SIGN_OFFS if name in profile.signed_off) or "none"
    return f"The worker: {ROLE_WORDS[profile.role]}; signed off for: {signed}."


# Decision: SC-027 (the equipment goes in the messages beside the profile line, so the cached system block never varies with it)
def equipment_line(equipment: tuple[Equipment, ...] | None) -> str:
    """What the answerer is told of the worker's equipment: None (not asked) gives ""; () gives "The equipment: not one the
    packs cover."; one controller gives "The equipment: Victron Energy SmartSolar MPPT 75/10 (controller)."; several are joined
    by "; "."""
    if equipment is None:
        return ""
    named = "; ".join(f"{each.model if each.make == 'any' else each.make + ' ' + each.model} ({each.kind})" for each in equipment)
    return f"The equipment: {named}." if equipment else "The equipment: not one the packs cover."


# Decision: SC-028 (the held stops go in the messages beside the profile line, so the cached system block never varies with them)
def held_line(held: tuple[tuple[str, str], ...]) -> str:
    """What the answerer is told of the stops that hold: () gives ""; (("SR-11", "batteries"),) gives "Stopped for this worker:
    batteries (SR-11). Do not give or offer any step of that work; if it comes up, say it is stopped and they should go to
    their supervisor."; several are joined by "; "."""
    if not held:
        return ""
    named = "; ".join(f"{name} ({rule_id})" for rule_id, name in held)
    return (f"Stopped for this worker: {named}. Do not give or offer any step of that work; if it comes up, say it is stopped "
            "and they should go to their supervisor.")


def messages_for(question: str, history: tuple[Turn, ...], profile: Profile | None = None,
                 equipment: tuple[Equipment, ...] | None = None, held: tuple[tuple[str, str], ...] = ()) -> list[dict[str, str]]:
    """The conversation as the API takes it: the history, then the new question as the last user turn, which begins with
    the profile's line, the equipment's line and the held stops' line when there are any (never the system block, SC-020,
    SC-027, SC-028): messages_for("Next?", (Turn("user", "Hi"),)) gives two messages."""
    turns = [{"role": turn.role, "content": turn.text} for turn in history]
    lines = [line for line in (profile_line(profile) if profile is not None else "", equipment_line(equipment), held_line(held)) if line]
    return turns + [{"role": "user", "content": "\n".join(lines) + "\n\n" + question if lines else question}]
