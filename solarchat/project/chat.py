"""The chat: a conversation on a reader and a writer, every reply through the answering door, the history kept (TODO 1.16).

Each reply is the door's: the words, the passages' titles with each source's title and page, and the demo banner in demo
mode; a warn or a stop also shows its rule's words. Ctrl-D or "quit" ends it. The orchestrator: it may call the answer,
model, packs and safety modules, so the command line holds no logic (MOD-02). Decision: SC-019 (amended 2026-11-21).
"""
import re
from pathlib import Path
from typing import TextIO

from solarchat.answer.door import answer
from solarchat.answer.stub import NoAnswer
from solarchat.leaf.contract import (DEFAULT_PROFILE, DEMO_BANNER, PROFILE_SIGN_OFFS, SAFETY_RESPONSES, Answerer, Profile, Reply,
                                     ReplyKind, Turn, may_answer)
from solarchat.model.claude import DEFAULT_MODEL, MODELS, ClaudeAnswerer, ModelError
from solarchat.packs.load import Pack, load_pack
from solarchat.project.keys import ensure_key
from solarchat.project.speech import Speaker
from solarchat.safety.rules import load_rules

PROMPT = "> "
DEMO_PACK = Path(__file__).resolve().parents[2] / "packs" / "seed-mc4-leads"  # absolute: the launchers do not change the folder
QUIT_WORDS = ("quit",)
MODEL_CHOICES = tuple(MODELS)
SOURCES_MARK = "\n\nFrom: "
LOWERED_MARK = ", lowered for your sign-off"
# Decision: SC-020 (the same words claude.py tells the model: model's entry points are fixed, MOD-04, so the tables are kept twice
# and a test holds them equal)
ROLE_WORDS = {"new": "new to solar", "crew": "crew member", "qualified": "licensed electrician or engineer"}
SIGN_OFF_WORDS = {"meter": "meter tests", "connector": "connector work", "battery": "battery and controller wiring",
                  "height": "work at height with fall protection"}
ROLE_QUESTION = "Before we start: what is your role? New to solar, crew member, or licensed electrician or engineer?"
ROLE_AGAIN = "I did not catch a role. Are you new to solar, a crew member, or a licensed electrician or engineer?"
SIGN_OFF_QUESTION = ("Which of these has your supervisor signed you off for on this site: meter tests, connector work, battery and "
                     "controller wiring, work at height with fall protection? Say the ones that apply, or none.")


def spoken(reply: Reply) -> str:
    """What the assistant said, as the history keeps it: the reply without its demo banner and its "From:" lines:
    "DEMO: ...\\n\\nJoin plus to plus.\\n\\nFrom: Step 6 (Pack): Manual, page 15" gives "Join plus to plus."."""
    text = reply.text.removeprefix(DEMO_BANNER).strip()
    return text.split(SOURCES_MARK)[0].strip() if SOURCES_MARK in text else text


def rule_label(reply: Reply, profile: Profile = DEFAULT_PROFILE) -> tuple[str, str]:
    """The rule a warn or a stop names, as ("Safety rule SR-03", "<words>"), or ("", "") for any other reply; a rule the
    profile lowered says so: ("Safety rule SR-11, lowered for your sign-off", "<the lowering's words>") (SC-020)."""
    if reply.kind not in (ReplyKind.WARN, ReplyKind.STOP) or not reply.safety_rule_id:
        return "", ""
    rule = {rule.rule_id: rule for rule in load_rules()}.get(reply.safety_rule_id)
    if rule is None:
        return f"Safety rule {reply.safety_rule_id}", ""
    matching = [lowering for lowering in rule.lowered_for if lowering.matches(profile)]
    if not matching:
        return f"Safety rule {reply.safety_rule_id}", rule.words_shown
    # the door's choice (SC-020): the lowest response of the matching lowerings, whose words the warn then shows
    lowest = min(matching, key=lambda lowering: SAFETY_RESPONSES.index(lowering.response))
    return f"Safety rule {reply.safety_rule_id}{LOWERED_MARK}", lowest.words


def rule_words(reply: Reply, profile: Profile = DEFAULT_PROFILE) -> str:
    """The words of the rule a warn or a stop names, "Safety rule SR-03: <words>", or "" for any other reply."""
    label, words = rule_label(reply, profile)
    return f"{label}: {words}" if words else label


def with_rule(reply: Reply, text: str, profile: Profile = DEFAULT_PROFILE) -> str:
    """`text` under the rule's heading: the door puts the rule's words inside the reply text since 1.9, so then only the
    label ("Safety rule SR-03") goes above it; a reply recorded without them keeps "Safety rule SR-03: <words>" above."""
    label, words = rule_label(reply, profile)
    if not label:
        return text
    return f"{label}\n\n{text}" if not words or words in text else f"{rule_words(reply, profile)}\n\n{text}"


def render(reply: Reply, profile: Profile = DEFAULT_PROFILE) -> str:
    """The reply as shown: the rule's label (and its words, when the text lacks them) first for a warn or a stop, then the
    door's text (which holds the demo banner and the citations): a plain answer renders as its own text."""
    return with_rule(reply, reply.text, profile)


def spoken_aloud(reply: Reply, profile: Profile = DEFAULT_PROFILE) -> str:
    """What --voice reads aloud for a reply: the rule's label first for a warn or a stop, then the reply's words once,
    never the banner or the "From:" lines (the banner is spoken once, at the start)."""
    return with_rule(reply, spoken(reply), profile)


# Decision: SC-020 (the answers are read by plain word matching, never by the model; the safest reading wins when words clash)
def read_role(text: str) -> str | None:
    """The role an answer names, or None: "I'm the site engineer" gives "qualified", "crew" gives "crew", "new to solar"
    gives "new"; an answer with several (new before crew before engineer) gives the one with the least say; no role word gives None."""
    words = set(re.findall(r"[a-z]+", text.lower()))
    if "new" in words:
        return "new"
    if "crew" in words:
        return "crew"
    return "qualified" if words & {"electrician", "engineer"} else None


def read_signed_off(text: str) -> frozenset[str]:
    """The sign-offs an answer names: "battery and meter" gives {"battery", "meter"}; "none", or nothing known, gives the empty
    set, and "none" beside others wins (fewer sign-offs is the safe reading)."""
    words = re.findall(r"[a-z]+", text.lower())
    if "none" in words:
        return frozenset()
    prefixes = {"meter": "meter", "connector": "connector", "battery": "battery", "batteries": "battery", "controller": "battery",
                "height": "height", "roof": "height"}
    return frozenset(sign for word in words for start, sign in prefixes.items() if word.startswith(start))


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


def ask(question: str, stdin: TextIO, stdout: TextIO, speaker: Speaker | None) -> str:
    """Show a question (and speak it), then read one line of the answer: "" at the end of input."""
    stdout.write(question + "\n")
    stdout.flush()
    if speaker:
        speaker.say(question)
    stdout.write(PROMPT)
    stdout.flush()
    return stdin.readline().strip()


def ask_profile(stdin: TextIO, stdout: TextIO, speaker: Speaker | None = None, role: str | None = None,
                signed_off: frozenset[str] | None = None) -> Profile:
    """The worker's profile: the two questions, each skipped when its answer is given (--role, --signed-off); a role answer that
    names no role is asked once more and then is "new"; a sign-off answer naming nothing known is none; the profile is said
    back in one line (and spoken)."""
    if role is None:
        role = read_role(ask(ROLE_QUESTION, stdin, stdout, speaker)) or read_role(ask(ROLE_AGAIN, stdin, stdout, speaker)) or "new"
    if signed_off is None:
        signed_off = read_signed_off(ask(SIGN_OFF_QUESTION, stdin, stdout, speaker))
    profile = Profile(role, signed_off)
    line = profile_said_back(profile)
    stdout.write(line + "\n\n")
    if speaker:
        stdout.flush()
        speaker.say(line)
    return profile


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


def converse(pack: Pack, demo: bool, answerer: Answerer, stdin: TextIO, stdout: TextIO, stderr: TextIO,
             speaker: Speaker | None = None, profile: Profile = DEFAULT_PROFILE) -> None:
    """The loop: read a line, answer it with the history so far, print the reply, keep both turns. A line of "quit", or the
    end of input, ends it; a blank line is skipped; a model that cannot be used is told in words and the turn is not kept.
    With a speaker each reply is shown, then spoken before the next prompt. The profile goes to the door with every question."""
    history: list[Turn] = []
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
        try:
            reply = answer(question, (pack,), demo, answerer, tuple(history), profile)
        except ModelError as problem:
            stderr.write(f"Sorry: {problem}\n")
            continue
        stdout.write(render(reply, profile) + "\n\n")
        if speaker:
            stdout.flush()
            speaker.say(spoken_aloud(reply, profile))
        history += [Turn("user", question), Turn("assistant", spoken(reply))]


def start_chat(pack_folder: str, demo: bool, answerer_name: str, stdin: TextIO, stdout: TextIO, stderr: TextIO,
               model: str = DEFAULT_MODEL, voice: bool = False, role: str | None = None,
               signed_off: frozenset[str] | None = None) -> int:
    """Run a whole chat and return its exit code: 0 when it ended, 2 when it cannot run (a pack that is missing or may not
    answer, or no key for the Claude answerer), with one plain line on stderr. The demo banner is shown at the start; with
    `voice` the chat is also spoken (a missing engine is one line on stderr and the chat goes on in text). After the banner the two profile questions are asked (SC-020), unless `role` and `signed_off` give the answers."""
    if answerer_name == "claude":
        ensure_key(stdin, stdout, stderr)  # no key: ask here and store it; an empty line leaves the exit 2 below
    try:
        pack = load_chat_pack(pack_folder, demo)
        answerer = choose_answerer(answerer_name, model)
    except (ValueError, ModelError) as problem:
        stderr.write(f"solarchat: cannot run: {problem}\n")
        return 2
    stdout.write((DEMO_BANNER + "\n\n" if demo else "") + f"{pack.manifest['title']}. Ask a question; type quit to end.\n\n")
    speaker = Speaker(stderr) if voice else None
    if speaker and demo:
        stdout.flush()
        speaker.say(DEMO_BANNER)  # spoken once, here; every reply still shows it on screen (HAD-06)
    profile = ask_profile(stdin, stdout, speaker, role, signed_off)
    if isinstance(answerer, ClaudeAnswerer):
        answerer.profile = profile  # built before the questions so a missing key ends the chat before any is asked
    converse(pack, demo, answerer, stdin, stdout, stderr, speaker, profile)
    return 0
