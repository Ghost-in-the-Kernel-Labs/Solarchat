"""The answering door: `answer()` is the one function every mode answers through (TODO 1.6; SC-019).

The same function in every mode; what changes is the answerer passed in. The door, not the answerer, decides which packs
may answer, the reply's kind and the citations, so an answerer can never skip them. It imports no model client and no
answerer. Step 6 of the design, the safety rules in the answer (TODO 1.9), is here: a cited passage whose text fires a
rule gives that rule's response and words, whatever the answerer said; so does a rule fired by this turn's question
(TODO 1.10), before "I do not know" (a rule that reads the words only fires on the question only). Standard library, the leaf, the packs module and the safety module only.
"""
import re
from dataclasses import replace

from solarchat.leaf.contract import (DEFAULT_PROFILE, DEMO_BANNER, MAX_CITED_PASSAGES, SAFETY_RESPONSES, Answerer, Finding,
                                     Passage, PassageRef, Profile, Reply, ReplyKind, SafetyRule, Turn, may_answer)
from solarchat.packs.load import Pack, citation_lines
from solarchat.safety.rules import load_rules, rules_fired

# Decision: SC-029 (it warns: it restates SR-14's own words, "If you are not sure, do not guess ... Go to your site supervisor or engineer", so it traces
# to SR-14's sources, HSE and OSHA; Ghost, 2026-11-25. Plain words: what the worker can do next, and none of the project's internal words; HAD-03 and the kind do not change)
DO_NOT_KNOW_TEXT = "I don't know this one: it isn't in the manuals I have for this equipment. Don't guess. If you are not sure what to do, stop and ask your site supervisor or engineer before you go on."
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


# Decision: SC-020 (a rule lowers, in response and words, for the profile's sign-off or role, only as its own lowered_for says)
def lowered_for_profile(rule: SafetyRule, profile: Profile) -> SafetyRule:
    """The rule as the profile meets it: the lowest response of the rule's lowerings that match the profile, with that
    lowering's words in place of words_shown; the rule itself when none matches (always so for the default profile and for
    a rule with no lowered_for). The lowered copy keeps the id and carries no lowerings."""
    matching = [lowering for lowering in rule.lowered_for if lowering.matches(profile)]
    if not matching:
        return rule
    lowest = min(matching, key=lambda lowering: SAFETY_RESPONSES.index(lowering.response))
    return replace(rule, response=lowest.response, words_shown=lowest.words, lowered_for=())


# Decision: SC-015 (the most severe response of the rules fired wins, then the lowest id; the answerer cannot skip it)
# Invariant: HAD-04 (a rule fires on the cited passages' text and on the worker's own words, whatever the answerer said)
# Decision: TODO 1.10 (a rule with reads == "words", SR-07, SR-08 and SR-09, fires on the worker's words only, never on a passage's text)
Hit = tuple[SafetyRule, Pack | None, Passage | None]


def most_severe(hits: list[Hit]) -> Hit | None:
    """The hit with the most severe response by its index in SAFETY_RESPONSES, then the lowest rule id; on a tie of the same
    rule a hit that names a passage comes first. None when there are no hits."""
    if not hits:
        return None
    return min(hits, key=lambda hit: (-SAFETY_RESPONSES.index(hit[0].response), hit[0].rule_id, hit[2] is None))


def fired_by_words(question: str, rules: tuple[SafetyRule, ...], profile: Profile = DEFAULT_PROFILE) -> list[Hit]:
    """The rules this turn's question fires, each lowered for the profile (SC-020) and naming no passage:
    fired_by_words("I got a shock", load_rules()) gives one hit, SR-09, with no pack and no passage."""
    by_id = {rule.rule_id: lowered_for_profile(rule, profile) for rule in rules}
    return [(by_id[rule_id], None, None) for rule_id in rules_fired(question, rules)]


def fired_by_citations(finding: Finding, places: dict[PassageRef, tuple[Pack, Passage]],
                       rules: tuple[SafetyRule, ...], profile: Profile = DEFAULT_PROFILE) -> list[Hit]:
    """Each rule fired by a cited passage's text, with the passage that fires it, lowered for the profile (SC-020); an
    rule that reads the words only (reads == "words": SR-07, SR-08, SR-09) never fires on a passage's text: a finding citing
    a passage that lists "smoke" gives []."""
    # Decision: SC-024 (a pack that covers a rule is applied before a lowering, and a profile never lowers a covered rule;
    # the door does not apply coverage yet, TODO 1.26 slice 2: when it does, a covered rule skips lowered_for_profile here).
    by_id = {rule.rule_id: lowered_for_profile(rule, profile) for rule in rules}
    on_text = tuple(rule for rule in rules if rule.reads != "words")
    return [(by_id[rule_id], *places[ref]) for ref in finding.refs for rule_id in rules_fired(places[ref][1].text, on_text)]


def stop_note(rule: SafetyRule, pack: Pack | None, passage: Passage | None) -> str:
    """"What to bring your supervisor: rule SR-07; Title, Manual, page 15" for the passage that fired a stop; with no
    passage (the worker's words fired it) "What to bring your supervisor: rule SR-07"."""
    if pack is None or passage is None:
        return f"What to bring your supervisor: rule {rule.rule_id}"
    bring = "; ".join(citation_lines(pack, passage.ref.passage_id))
    title = passage.title or passage.ref.passage_id
    return f"What to bring your supervisor: rule {rule.rule_id}; {title}" + (f", {bring}" if bring else "")


def safety_reply(hit: Hit, finding: Finding | None, places: dict[PassageRef, tuple[Pack, Passage]]) -> Reply:
    """The reply a fired rule gives: an emergency is the rule's words alone; a stop is the words, a blank line and
    "What to bring your supervisor: rule SR-07; Title, Manual, page 15"; a warn is the words, a blank line and the answer's
    body, citing the finding's passages. A warn fired by the worker's words when the answerer cited no passage (finding is
    None) names no passage, so it is an "I do not know" whose text is the warn's words, a blank line and DO_NOT_KNOW_TEXT
    (TODO 1.10, corrected by the coordinator, J-079)."""
    rule, pack, passage = hit
    if rule.response == "emergency":
        return Reply(ReplyKind.STOP, rule.words_shown, (), rule.rule_id)
    if rule.response == "stop":
        return Reply(ReplyKind.STOP, f"{rule.words_shown}\n\n{stop_note(rule, pack, passage)}", (), rule.rule_id)
    if finding is None:
        return do_not_know(f"{rule.words_shown}\n\n{DO_NOT_KNOW_TEXT}")
    return Reply(ReplyKind.WARN, f"{rule.words_shown}\n\n{answer_body(finding, places)}", finding.refs, rule.rule_id)


STILL_STOPPED = "This is still stopped for you."
ASK_OTHER = "Is there something else I can help with?"
SENTENCE_END = re.compile(r"(?<=[.!?])\s+")


# Decision: SC-028 (a held stop is the rule's stop again, short: STOP, naming the rule and no passage, HAD-03)
def held_stop(rule: SafetyRule, demo_mode: bool) -> Reply:
    """The reply for a topic a stop still holds: for SR-11 a STOP naming "SR-11" and no passage whose text is "This is still
    stopped for you. Go to your site supervisor or engineer. Is there something else I can help with?", a blank line and "What
    to bring your supervisor: rule SR-11" (the middle sentence is the rule's own last sentence); the banner first in demo mode."""
    last = SENTENCE_END.split(rule.words_shown.strip())[-1]
    text = f"{STILL_STOPPED} {last} {ASK_OTHER}\n\n{stop_note(rule, None, None)}"
    return with_banner(Reply(ReplyKind.STOP, text, (), rule.rule_id), demo_mode)


# Decision: SC-019 (one door, an answerer passed in; the steps in order, each returning at once when it gives a reply)
# Invariant: HAD-06 (only may_answer lets a pack's passages reach the answerer)
def answer(question: str, packs: tuple[Pack, ...], demo_mode: bool, answerer: Answerer,
           history: tuple[Turn, ...] = (), profile: Profile = DEFAULT_PROFILE) -> Reply:
    """The reply to a question: answer("", packs, True, NoAnswer()) is "I do not know" with the banner and the answerer
    is never called; a finding citing one given passage is an ANSWER with its sources. Steps: empty question; packs that
    may answer; find; the safety rules on this turn's question and on the cited passages' text, when the finding keeps the contract
    (a stop, an emergency or a warn, SC-015; SR-07, SR-08 and SR-09 fire on the question only; a stop or emergency is given even when
    nothing is cited); "I do not know"; the answer; the demo banner. `history` is the turns so far, passed to the answerer unchanged (SC-019, amended
    2026-11-21); the door's other steps do not read it. `profile` is who is asking (SC-020): the default is the newest contractor, which
    gives the replies there were before it; a rule lowers for a profile only as its own lowered_for says. What the answerer raises is a bug and reaches the caller."""
    if not question.strip():
        return with_banner(do_not_know(DO_NOT_KNOW_TEXT), demo_mode)
    places = usable_places(packs, demo_mode)
    if not places:
        return with_banner(do_not_know(NO_PACK_TEXT), demo_mode)
    given = tuple(passage for _, passage in places.values())
    finding = answerer.find(question, given, history)
    rules = load_rules()
    hits = fired_by_words(question, rules, profile)
    cited = bool(finding.refs) and not breaks_contract(finding, given)
    if cited:
        hits += fired_by_citations(finding, places, rules, profile)
    hit = most_severe(hits)
    if hit:
        return with_banner(safety_reply(hit, finding if cited else None, places), demo_mode)
    if not cited:
        return with_banner(do_not_know(DO_NOT_KNOW_TEXT), demo_mode)
    reply = Reply(ReplyKind.ANSWER, answer_body(finding, places), finding.refs)
    return with_banner(reply, demo_mode)
