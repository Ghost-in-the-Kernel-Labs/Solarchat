"""The answering door: `answer()` is the one function every mode answers through (TODO 1.6; SC-019).

The same function in every mode; what changes is the answerer passed in. The door, not the answerer, decides which packs
may answer, the reply's kind and the citations, so an answerer can never skip them. It imports no model client and no
answerer. Step 6 of the design, the safety rules in the answer, is TODO 1.9's and is not here: until it is built no
reply of this door is a stop or a warn. Standard library, the leaf and the packs module only.
"""
from dataclasses import replace

from solarchat.leaf.contract import (DEMO_BANNER, MAX_CITED_PASSAGES, Answerer, Finding, Passage, PassageRef, Reply,
                                     ReplyKind, may_answer)
from solarchat.packs.load import Pack, citation_lines

DO_NOT_KNOW_TEXT = "I do not know. The packs switched on do not cover this."
NO_PACK_TEXT = "I do not know. No pack switched on may answer here."


def do_not_know(text: str) -> Reply:
    """An "I do not know" reply with these words: do_not_know(DO_NOT_KNOW_TEXT).passage_refs gives ()."""
    return Reply(ReplyKind.DO_NOT_KNOW, text)


# Decision: SC-010 (every screen shown in demo mode carries the banner, whatever the reply's kind)
def with_banner(reply: Reply, demo_mode: bool) -> Reply:
    """The reply with DEMO_BANNER and a blank line before its text in demo mode, unchanged otherwise:
    with_banner(do_not_know("No."), True).text starts with "DEMO: not reviewed"."""
    if not demo_mode:
        return reply
    return replace(reply, text=f"{DEMO_BANNER}\n\n{reply.text}")


# Invariant: HAD-03 (an answerer that cites a passage it was not given, a repeat or too many is answered "I do not know")
def breaks_contract(finding: Finding, given: tuple[Passage, ...]) -> bool:
    """True when the finding cites a ref not among the given passages, one ref twice, or more than MAX_CITED_PASSAGES:
    a finding of four refs gives True; a finding of one given ref gives False."""
    allowed = {passage.ref for passage in given}
    refs = finding.refs
    return len(refs) > MAX_CITED_PASSAGES or len(set(refs)) != len(refs) or not set(refs) <= allowed


def source_line(pack: Pack, passage: Passage) -> str:
    """One citation line: "From: Check the voltages match (Pack title): Manual, page 15; Web page"; a passage with no
    sources gives "From: Check the voltages match (Pack title)"."""
    title = passage.title or passage.ref.passage_id
    lines = citation_lines(pack, passage.ref.passage_id)
    tail = f": {'; '.join(lines)}" if lines else ""
    return f"From: {title} ({pack.manifest['title']}){tail}"


# Invariant: HAD-03 (an answer names the passages it came from; the page is read from the pack, SC-012)
def answer_body(finding: Finding, places: dict[PassageRef, tuple[Pack, Passage]]) -> str:
    """The finding's words, a blank line, then one "From:" line per cited ref, in the finding's order."""
    lines = [source_line(*places[ref]) for ref in finding.refs]
    return finding.text + "\n\n" + "\n".join(lines)


def usable_places(packs: tuple[Pack, ...], demo_mode: bool) -> dict[PassageRef, tuple[Pack, Passage]]:
    """Each passage of each pack that may answer, by its ref, packs in the order given; a refused pack adds none."""
    places: dict[PassageRef, tuple[Pack, Passage]] = {}
    for pack in packs:
        if may_answer(pack.manifest, demo_mode):
            places.update({passage.ref: (pack, passage) for passage in pack.passages})
    return places


# Decision: SC-019 (one door, an answerer passed in; the steps in order, each returning at once when it gives a reply)
# Invariant: HAD-06 (only may_answer lets a pack's passages reach the answerer)
def answer(question: str, packs: tuple[Pack, ...], demo_mode: bool, answerer: Answerer) -> Reply:
    """The reply to a question: answer("", packs, True, NoAnswer()) is "I do not know" with the banner and the answerer
    is never called; a finding citing one given passage is an ANSWER with its sources. Steps: empty question; packs that
    may answer; find; hold the answerer to the contract; "I do not know"; the answer; the demo banner. (Step 6, the
    safety rules, is TODO 1.9's.) What the answerer raises is a bug and reaches the caller."""
    if not question.strip():
        return with_banner(do_not_know(DO_NOT_KNOW_TEXT), demo_mode)
    places = usable_places(packs, demo_mode)
    if not places:
        return with_banner(do_not_know(NO_PACK_TEXT), demo_mode)
    given = tuple(passage for _, passage in places.values())
    finding = answerer.find(question, given)
    if breaks_contract(finding, given) or not finding.refs:
        return with_banner(do_not_know(DO_NOT_KNOW_TEXT), demo_mode)
    reply = Reply(ReplyKind.ANSWER, answer_body(finding, places), finding.refs)
    return with_banner(reply, demo_mode)
