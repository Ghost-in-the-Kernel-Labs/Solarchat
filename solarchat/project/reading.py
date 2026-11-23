"""How the chat reads a worker's words: roles, sign-offs and yes-or-no by plain word matching, never by the model (SC-020, SC-026).

Moved out of chat.py to keep that file under 400 lines; `solarchat.project.chat` still names each function. Standard library and
the leaf only.
"""
import difflib
import re

from solarchat.leaf.contract import PROFILE_SIGN_OFFS

YES_WORDS = ("yes", "y", "yeah", "yep", "correct", "confirm")
NO_WORDS = ("no", "n", "nope", "not", "dont")


def word_matches(word: str, vocabulary: list[str]) -> str | None:
    """The vocabulary word a spoken or typed word stands for, or None: "crewmember" gives "crew" (it starts with it), "eletrician"
    gives "electrician" (a close spelling, only for words of 6 letters or more); "now" gives None, never "new"."""
    for known in vocabulary:
        if word.startswith(known):
            return known
    close = difflib.get_close_matches(word, vocabulary, n=1, cutoff=0.8) if len(word) >= 6 else []
    return close[0] if close else None


# Decision: SC-020 (the answers are read by plain word matching, never by the model; the safest reading wins when words clash)
def read_role(text: str) -> str | None:
    """The role an answer names, or None: "I'm the site engineer" gives "qualified", "crewmember" gives "crew", "new to solar"
    gives "new", "licenssed eletrician" gives "qualified", "cew member" gives "crew" ("member" says crew); an answer with several (new before crew before engineer) gives
    the one with the least say; no role word ("now", "the boss") gives None."""
    roles = {"new": "new", "crew": "crew", "member": "crew", "electrician": "qualified", "engineer": "qualified", "licensed": "qualified",
             "qualified": "qualified"}
    found = {roles[known] for word in re.findall(r"[a-z]+", text.lower()) if (known := word_matches(word, list(roles)))}
    return next((role for role in ("new", "crew", "qualified") if role in found), None)


def read_signed_off(text: str) -> frozenset[str]:
    """The sign-offs an answer names: "battery and meter" gives {"battery", "meter"}, "baterry" gives {"battery"}, "all of these"
    or "everything" gives all four; "none" or "not" or "except" or "but" anywhere, or nothing known, gives the empty set
    (fewer sign-offs is the safe reading, so "all except height" signs off nothing and the said-back line lets them restart)."""
    words = re.findall(r"[a-z]+", text.lower())
    if {"none", "not", "except", "but"} & set(words):
        return frozenset()
    if {"all", "every", "everything"} & set(words):
        return frozenset(PROFILE_SIGN_OFFS)
    signs = {"meter": "meter", "connector": "connector", "battery": "battery", "batteries": "battery", "controller": "battery",
             "height": "height", "roof": "height"}
    return frozenset(signs[known] for word in words if (known := word_matches(word, list(signs))))


# Decision: SC-026 (a yes is read by word matching, never by the model; anything but a clear yes is a no)
def read_yes(text: str) -> bool:
    """Whether an answer is a yes: "yes" and "Yeah, confirm" are; "no", "maybe", "" and "yes, no" are not (a no word wins)."""
    words = set(re.findall(r"[a-z]+", text.lower().replace("'", "")))
    return bool(words & set(YES_WORDS)) and not words & set(NO_WORDS)


# Decision: SC-028 (a question typed at a yes-or-no prompt is a no for the switch and is kept, not lost)
def asks_instead(text: str) -> bool:
    """Whether an answer to a yes-or-no prompt is really a next question: more than three words and neither a yes word nor a no
    word: "Can I use a bigger fuse on the string?" is, "ok what next" (three words), "no" and "yes, please do" are not."""
    words = set(re.findall(r"[a-z]+", text.lower().replace("'", "")))
    return len(text.split()) > 3 and not words & set(YES_WORDS) and not words & set(NO_WORDS)
