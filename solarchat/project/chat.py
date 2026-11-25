"""The chat: a conversation on a reader and a writer, every reply through the answering door, the history kept (TODO 1.16).

Each reply is the door's: the words, the passages' titles with each source's title and page, and the demo banner in demo
mode; a warn or a stop also shows its rule's words. Ctrl-D or "quit" ends it. The orchestrator: it may call the answer,
model, packs and safety modules, so the command line holds no logic (MOD-02). Decision: SC-019 (amended 2026-11-21).
"""
from pathlib import Path
from typing import Protocol, TextIO

from solarchat.answer.door import answer
from solarchat.answer.stub import NoAnswer
from solarchat.leaf.contract import DEFAULT_PROFILE, DEMO_BANNER, PROFILE_ROLES, PROFILE_SIGN_OFFS, Answerer, Profile, Reply, ReplyKind, Turn, may_answer
from solarchat.model.claude import DEFAULT_MODEL, MODELS, ClaudeAnswerer, ModelError
from solarchat.packs.load import Pack, load_pack
from solarchat.project.intake import equipment_of, parse_option, run_intake
from solarchat.project.keys import ensure_key
from solarchat.project.holds import enforce_holds, held_names, kept_holds, stop_shown
from solarchat.project.proposal import checked_proposal, said_proposal
from solarchat.project.offtopic import plain_if_off_topic
from solarchat.project.repeat import retried
from solarchat.project.reading import asks_instead, read_role, read_signed_off, read_yes, word_matches  # noqa: F401  (moved out for the line limit; still read from here)
from solarchat.project.shown import LOWERED_MARK, SOURCES_MARK, is_lowered, render, rule_label, rule_words, spoken, spoken_aloud, with_rule  # noqa: F401  (moved out for the line limit; still read from here)
from solarchat.project.speech import Speaker
from solarchat.safety.rules import load_rules

PROMPT = "> "
PROFILE_WRONG = "If that is wrong, say so at any point."  # SC-029: a correction is read as any statement is, so quitting is not the way
DEMO_PACK = Path(__file__).resolve().parents[2] / "packs" / "seed-mc4-leads"  # absolute: the launchers do not change the folder
QUIT_WORDS = ("quit",)
MODEL_CHOICES = tuple(MODELS)
# Decision: SC-020 (the same words claude.py tells the model: model's entry points are fixed, MOD-04, so the tables are kept twice
# and a test holds them equal)
ROLE_WORDS = {"new": "new to solar", "crew": "crew member", "qualified": "licensed electrician or engineer"}
SIGN_OFF_WORDS = {"meter": "meter tests", "connector": "connector work", "battery": "battery and controller wiring",
                  "height": "work at height with fall protection"}
ROLE_QUESTION = "Before we start: what is your role? New to solar, crew member, or licensed electrician or engineer?"
ROLE_AGAIN = "I did not catch a role. Are you new to solar, a crew member, or a licensed electrician or engineer?"
SIGN_OFF_QUESTION = ("Which of these has your supervisor signed you off for on this site: meter tests, connector work, battery and "
                     "controller wiring, work at height with fall protection? Say the ones that apply, or none.")


class ProfileChange(Protocol):
    """What the chat reads of a proposed change (the answerer's `ProfileChange`; the model's entry points are fixed, MOD-04, so
    the chat names the fields it reads rather than importing the record): a role or None, the sign-offs added and removed,
    and whether someone new is typing."""

    role: str | None
    add: frozenset[str]
    remove: frozenset[str]
    new_person: bool


SWITCH_REMINDER = "Only switch if your supervisor has signed you off for this on this site."
KEPT_PROFILE = "Kept your profile as it was."
NEW_PERSON_LINE = "Someone new is typing: two quick questions."
CHANGED = "Profile changed: "
GO_AHEAD = "Go ahead: what do you need?"


def parse_signed_off(text: str) -> frozenset[str]:
    """The --signed-off value: "meter,battery" gives both, "none" or "" gives none; a name that is not one of the four raises
    ValueError in words."""
    names = [name.strip().lower() for name in text.split(",") if name.strip()]
    if names == ["none"]:
        return frozenset()
    unknown = [name for name in names if name not in PROFILE_SIGN_OFFS]
    if unknown:
        raise ValueError(f"{', '.join(unknown)} is not one of {', '.join(PROFILE_SIGN_OFFS)}, or none")
    return frozenset(names)


def profile_said_back(profile: Profile) -> str:
    """The profile in one line: Profile("qualified", frozenset({"battery"})) gives "You are a licensed electrician or engineer,
    signed off for battery and controller wiring."; no sign-off gives "... not signed off for any of them."."""
    article = "" if profile.role == "new" else "a "
    signed = ", ".join(SIGN_OFF_WORDS[name] for name in PROFILE_SIGN_OFFS if name in profile.signed_off)
    return f"You are {article}{ROLE_WORDS[profile.role]}, " + (f"signed off for {signed}." if signed else "not signed off for any of them.")


class ChatEnded(Exception):
    """The worker typed "quit" at a question: the chat ends at once, with nothing recorded (SC-029)."""


# Decision: SC-029 ("quit" ends the chat at any question, the opening ones and the switch question included, and is never an answer)
def ask(question: str, stdin: TextIO, stdout: TextIO, speaker: Speaker | None) -> str:
    """Show a question (and speak it), then read one line of the answer: "" at the end of input; "quit" (any case) raises ChatEnded
    after a blank line, so the chat ends: ask("Which?", io.StringIO("quit\\n"), out, None) raises, and "crew member" gives "crew member"."""
    stdout.write(question + "\n")
    stdout.flush()
    if speaker:
        speaker.say(question)
    stdout.write(PROMPT)
    stdout.flush()
    typed = stdin.readline().strip()
    if typed.lower() in QUIT_WORDS:
        stdout.write("\n")
        raise ChatEnded
    return typed


def ask_profile(stdin: TextIO, stdout: TextIO, speaker: Speaker | None = None, role: str | None = None,
                signed_off: frozenset[str] | None = None) -> Profile:
    """The worker's profile: the two questions, each skipped when its answer is given (--role, --signed-off); a role answer that
    names no role is asked once more and then is "new"; a sign-off answer naming nothing known is none; the profile is said
    back in one line, then "If that is wrong, say so at any point." (both spoken); "quit" at either question raises ChatEnded."""
    if role is None:
        role = read_role(ask(ROLE_QUESTION, stdin, stdout, speaker)) or read_role(ask(ROLE_AGAIN, stdin, stdout, speaker)) or "new"
    if signed_off is None:
        signed_off = read_signed_off(ask(SIGN_OFF_QUESTION, stdin, stdout, speaker))
    profile = Profile(role, signed_off)
    line = profile_said_back(profile)
    stdout.write(line + "\n" + PROFILE_WRONG + "\n\n")
    if speaker:
        stdout.flush()
        speaker.say(line)
        speaker.say(PROFILE_WRONG)
    return profile


def applied(profile: Profile, change: ProfileChange) -> Profile:
    """The profile once the change is made: Profile("new", {}) with ProfileChange("crew", {"meter"}) is a crew member signed
    off for meter tests; a sign-off both held and removed is gone."""
    return Profile(change.role or profile.role, (profile.signed_off | change.add) - change.remove)


# Decision: SC-026 (more say is a higher role, new < crew < qualified, or a sign-off the profile lacks; a mixed change is more)
def gives_more_say(profile: Profile, change: ProfileChange) -> bool:
    """Whether a change gives the worker more say: "crew" for a new worker does, "add battery" does, "new" for a crew
    member does not, and removing a sign-off does not; a change that raises one thing and lowers another does."""
    higher = change.role is not None and PROFILE_ROLES.index(change.role) > PROFILE_ROLES.index(profile.role)
    return higher or bool(change.add - profile.signed_off)


# Decision: SC-026 (the model proposes; more say is applied only on the person's yes, less say at once, a new person re-asks)
def settle_proposal(change: ProfileChange, profile: Profile, declined: set[tuple[str | None, frozenset[str]]], stdin: TextIO,
                    stdout: TextIO, speaker: Speaker | None, leftover: list[str] | None = None) -> Profile | None:
    """The profile after a proposal, or None when the person kept the old one (the held reply is then shown as it is):
    "no" or a proposal already declined gives None; less say, or "yes", gives the changed profile; someone new typing asks
    both opening questions and gives their answers whole. One question at most. A declined (role, add) is remembered in
    `declined`: ProfileChange("qualified", {"battery"}) answered "no" is not asked again this session. The question carries a
    reminder ("Only switch if your supervisor has signed you off for this on this site."), and an answer that is a next question
    (SC-028: "Can I use a bigger fuse on the string?") is a no whose words are added to `leftover`, to be answered."""
    if change.new_person:
        stdout.write(NEW_PERSON_LINE + "\n")
        if speaker:
            stdout.flush()
            speaker.say(NEW_PERSON_LINE)
        return ask_profile(stdin, stdout, speaker)
    after = applied(profile, change)
    if not gives_more_say(profile, change):
        return after
    key = (change.role, change.add)
    if key in declined:
        return None
    said = profile_said_back(after).removeprefix("You are ").rstrip(".")
    typed = ask(f"You said you are {said}. {SWITCH_REMINDER} Switch to that? yes or no", stdin, stdout, speaker)
    if read_yes(typed):
        return after
    declined.add(key)
    if leftover is not None and asks_instead(typed):
        leftover.append(typed)
    return None


def choose_answerer(name: str, model: str = DEFAULT_MODEL) -> Answerer:
    """The answerer a name stands for: "stub" is the one that says "I do not know" to everything; "claude" is Claude
    Sonnet 5.5 (a missing key raises ModelError)."""
    return NoAnswer() if name == "stub" else ClaudeAnswerer(model=model)


def load_chat_pack(folder: str, demo: bool) -> Pack:
    """The pack, or ValueError in words when it is missing, broken, or a pack that may not answer now (HAD-06):
    a demo pack without demo gives "<id> is a demo pack: run with --demo (HAD-06)"."""
    pack = load_pack(Path(folder))
    if not may_answer(pack.manifest, demo):
        status = pack.manifest["status"]
        raise ValueError(f"{pack.pack_id} is a demo pack: run with --demo (HAD-06)" if status == "demo"
                         else f"{pack.pack_id} has the status {status!r}, which may not answer (HAD-06)")
    return pack


def tell_answerer(answerer: Answerer, held: set[str]) -> None:
    """Give a real answerer the stops that hold, for the held line of its next call (never the system block, SC-028)."""
    if isinstance(answerer, ClaudeAnswerer):
        answerer.held = held_names(held, load_rules())


# Decision: SC-028 (a stop holds for the conversation; the proposal is checked against what was said; a question at the prompt is kept)
# Decision: SC-029 (a repeated answer is asked once more; a lowered warn's precautions are shown in full once per rule; "quit" ends at any question)
def converse(pack: Pack, demo: bool, answerer: Answerer, stdin: TextIO, stdout: TextIO, stderr: TextIO,
             speaker: Speaker | None = None, profile: Profile = DEFAULT_PROFILE) -> None:
    """The loop: read a line, answer it with the history so far, print the reply, keep both turns. A line of "quit", or the
    end of input, ends it; a blank line is skipped; a model that cannot be used is told in words and the turn is not kept.
    With a speaker each reply is shown, then spoken before the next prompt. The profile goes to the door with every question.
    A profile change the answerer proposes (SC-026) is kept only where the worker's message says it (SC-028), never on the first
    turn or the turn after a change, then settled before the reply is shown: "I'm the site electrician, signed off for battery
    wiring" asks "... Switch to that? yes or no", and on yes prints "Profile changed: You are a licensed electrician or engineer,
    signed off for battery and controller wiring." and answers the turn again under it; on no it shows the held reply, and a
    question typed instead of a yes or no is answered after "Kept your profile as it was.". A stop shown is held: a later reply
    that names its topic is the held stop again, until a change lowers the rule or someone new types. An answer that is 85% or more the
    same as the last spoken turn is asked once more with a note (one retry a turn) and the second reply is shown: "Join plus to plus."
    twice shows the second reply. A lowered warn shows its precautions in full the first time for a rule, then "The precautions above
    still apply." until the profile changes. "quit" at a question ends the chat as it does at the prompt."""
    history: list[Turn] = []
    declined: set[tuple[str | None, frozenset[str]]] = set()
    held: set[str] = set()
    rules = load_rules()
    fresh = False  # the turn right after a profile change acts on no proposal (the opening questions' turn does: J-090)
    precautions: set[str] = set()  # rule ids whose lowered warn has been shown in full since the profile last changed (SC-029)
    spent: list[bool] = []  # not empty once this turn has used its retry (SC-029)

    def asked(text: str) -> Reply:
        """The door's reply to `text`, asked once more with the retry note when it repeats the last spoken turn (SC-029)."""
        def call() -> Reply:
            """One ask of the door under the profile and history as they are now."""
            return answer(text, (pack,), demo, answerer, tuple(history), profile)
        first = call()
        if spent:
            return first
        second = retried(first, spoken(first), tuple(history), call, answerer)
        if second is not first:
            spent.append(True)
        return second

    def show(question: str, reply: Reply, notes: list[Turn]) -> None:
        """Print and speak a reply, hold its stop, and keep the turn."""
        reply = plain_if_off_topic(reply, getattr(answerer, "off_topic", False), question, pack.equipment, rules)
        stdout.write(render(reply, profile, precautions) + "\n\n")
        if speaker:
            stdout.flush()
            speaker.say(spoken_aloud(reply, profile, precautions))
        if is_lowered(reply, profile):
            precautions.add(reply.safety_rule_id or "")
        stopped = stop_shown(reply, rules)
        if stopped:
            held.add(stopped)
            tell_answerer(answerer, held)
        history.extend([Turn("user", question), *notes, Turn("assistant", spoken(reply))])

    try:
        while True:
            stdout.write(PROMPT)
            stdout.flush()
            line = stdin.readline()
            question = line.strip()
            if not line or question.lower() in QUIT_WORDS:
                stdout.write("\n")
                return
            if not question:
                continue
            spent.clear()  # a turn has one retry at most (SC-029)
            try:
                reply = asked(question)
            except ModelError as problem:
                stderr.write(f"Sorry: {problem}\n")
                continue
            notes: list[Turn] = []
            proposed = getattr(answerer, "proposal", None)
            change = None if fresh else (checked_proposal(proposed, question, profile) if proposed else None) or said_proposal(
                question, profile)
            fresh, leftover = False, []
            changed = settle_proposal(change, profile, declined, stdin, stdout, speaker, leftover) if change else None
            if changed is not None and (changed != profile or change.new_person):  # a new person gets the turn again even if the same
                held &= kept_holds(held, changed, rules, change.new_person)
                profile, fresh = changed, True
                precautions.clear()  # a changed profile shows the precautions in full again, once (SC-029)
                if isinstance(answerer, ClaudeAnswerer):
                    answerer.profile = profile  # the profile line of the next call, never the system block (SC-020)
                tell_answerer(answerer, held)
                line = CHANGED + profile_said_back(profile)
                try:
                    reply = asked(question)  # the same question, the new profile
                except ModelError as problem:
                    stderr.write(f"Sorry: {problem}\n")
                    continue
                stdout.write(line + "\n\n")
                if speaker:
                    stdout.flush()
                    speaker.say(line)
                notes = [Turn("assistant", line)]
                reply = enforce_holds(reply, held, question, pack, demo, rules)
                if reply.kind is ReplyKind.DO_NOT_KNOW:  # "she's taking over" or "I am signed off for all" asks nothing: invite it
                    stdout.write(GO_AHEAD + "\n\n")
                    if speaker:
                        stdout.flush()
                        speaker.say(GO_AHEAD)
                    history += [Turn("user", question), *notes, Turn("assistant", GO_AHEAD)]
                    continue
            show(question, enforce_holds(reply, held, question, pack, demo, rules), notes)
            if leftover:  # the question typed at the prompt: one more answer, in this same turn
                stdout.write(KEPT_PROFILE + "\n\n")
                if speaker:
                    stdout.flush()
                    speaker.say(KEPT_PROFILE)
                try:
                    reply = asked(leftover[0])
                except ModelError as problem:
                    stderr.write(f"Sorry: {problem}\n")
                    continue
                show(leftover[0], enforce_holds(reply, held, leftover[0], pack, demo, rules), [])
    except ChatEnded:  # "quit" at the switch question or a new person's questions ends the chat (SC-029)
        return


def start_chat(pack_folder: str, demo: bool, answerer_name: str, stdin: TextIO, stdout: TextIO, stderr: TextIO,
               model: str = DEFAULT_MODEL, voice: bool = False, role: str | None = None,
               signed_off: frozenset[str] | None = None, equipment: str | None = None) -> int:
    """Run a whole chat and return its exit code: 0 when it ended, 2 when it cannot run (a pack that is missing or may not
    answer, an equipment id clash or an unknown `equipment` id, or no key for the Claude answerer), with one plain line on stderr. The demo banner is shown at the start; with
    `voice` the chat is also spoken (a missing engine is one line on stderr and the chat goes on in text). After the banner the two profile questions are asked (SC-020), unless `role` and `signed_off` give the answers. Then the equipment intake (SC-027): the pack's equipment is listed and its make
    and model asked, unless `equipment` ("victron-smartsolar-mppt" or "none") gives the match; a pack with no list has no intake."""
    if answerer_name == "claude":
        ensure_key(stdin, stdout, stderr)  # no key: ask here and store it; an empty line leaves the exit 2 below
    try:
        pack = load_chat_pack(pack_folder, demo)
        answerer = choose_answerer(answerer_name, model)
        offered = equipment_of((pack,))
        chosen = None if equipment is None else parse_option(equipment, offered)
    except (ValueError, ModelError) as problem:
        stderr.write(f"solarchat: cannot run: {problem}\n")
        return 2
    stdout.write((DEMO_BANNER + "\n\n" if demo else "") + f"{pack.manifest['title']}. Ask a question; type quit to end.\n\n")
    speaker = Speaker(stderr) if voice else None
    if speaker and demo:
        stdout.flush()
        speaker.say(DEMO_BANNER)  # spoken once, here; every reply still shows it on screen (HAD-06)
    try:
        profile = ask_profile(stdin, stdout, speaker, role, signed_off)
        if isinstance(answerer, ClaudeAnswerer):
            answerer.profile = profile  # built before the questions so a missing key ends the chat before any is asked
        matched = run_intake(offered, chosen, answerer, stdin, stdout, speaker, ask)
    except ChatEnded:  # "quit" at an opening question: no profile, no match and no answer is kept (SC-029)
        return 0
    if isinstance(answerer, ClaudeAnswerer) and offered:
        answerer.equipment = matched  # the equipment line of every call, never the system block (SC-027)
    converse(pack, demo, answerer, stdin, stdout, stderr, speaker, profile)
    return 0
