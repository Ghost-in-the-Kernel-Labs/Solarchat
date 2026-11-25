"""A repeated reply is caught and the answerer asked once more (SC-029; docs/designs/conversation-quality.md section 2 (2)).

The orchestrator's helper for chat.py. The comparison is on the spoken text (the reply without its demo banner and "From:" lines),
by Python's `difflib.SequenceMatcher`; the model is never asked whether it repeated itself. Standard library and the leaf only.
"""
import difflib
from collections.abc import Callable

from solarchat.leaf.contract import Reply, ReplyKind, Turn

REPEAT_RATIO = 0.85
RETRY_NOTE = "You just said that. Move on to the next step, or say plainly what you still need."


def previous_said(history: tuple[Turn, ...]) -> str | None:
    """The text of the last turn if the assistant spoke it, else None: (Turn("user", "Hi"), Turn("assistant", "Hello")) gives "Hello"."""
    return history[-1].text if history and history[-1].role == "assistant" else None


# Decision: SC-029 (only an answer is checked, by the spoken words of both turns, at 85% or more alike)
def is_repeat(reply: Reply, said: str, history: tuple[Turn, ...]) -> bool:
    """Whether a reply says what the assistant said last: an ANSWER whose spoken text `said` is 85% or more the same as the previous
    assistant turn is; "Join plus to plus." after "Join plus to plus." is, "Now the cable." after it is not; a stop, a warn, "I do not
    know" and a first turn never are."""
    before = previous_said(history)
    if reply.kind is not ReplyKind.ANSWER or before is None:
        return False
    return difflib.SequenceMatcher(None, before, said).ratio() >= REPEAT_RATIO


# Decision: SC-029 (one retry at most per turn; the note goes in that call's messages only, and the second reply is shown whatever it is)
def retried(reply: Reply, said: str, history: tuple[Turn, ...], again: Callable[[], Reply], answerer: object) -> Reply:
    """The reply to show: `reply` unless it repeats the last assistant turn, then `again()`, the same question asked once more with
    the answerer's `note` set to RETRY_NOTE for that call alone and set back to "" after, even when the call raises. An answerer with
    no `note` is simply asked again."""
    if not is_repeat(reply, said, history):
        return reply
    had_note = hasattr(answerer, "note")
    if had_note:
        answerer.note = RETRY_NOTE  # type: ignore[attr-defined]
    try:
        return again()
    finally:
        if had_note:
            answerer.note = ""  # type: ignore[attr-defined]
