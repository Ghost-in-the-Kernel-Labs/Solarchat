"""The chat: a conversation on a reader and a writer, every reply through the answering door, the history kept (TODO 1.16).

Each reply is the door's: the words, the passages' titles with each source's title and page, and the demo banner in demo
mode; a warn or a stop also shows its rule's words. Ctrl-D or "quit" ends it. The orchestrator: it may call the answer,
model, packs and safety modules, so the command line holds no logic (MOD-02). Decision: SC-019 (amended 2026-11-21).
"""
from pathlib import Path
from typing import TextIO

from solarchat.answer.door import answer
from solarchat.answer.stub import NoAnswer
from solarchat.leaf.contract import DEMO_BANNER, Answerer, Reply, ReplyKind, Turn, may_answer
from solarchat.model.claude import DEFAULT_MODEL, MODELS, ClaudeAnswerer, ModelError
from solarchat.packs.load import Pack, load_pack
from solarchat.safety.rules import load_rules

PROMPT = "> "
QUIT_WORDS = ("quit",)
MODEL_CHOICES = tuple(MODELS)
SOURCES_MARK = "\n\nFrom: "


def spoken(reply: Reply) -> str:
    """What the assistant said, as the history keeps it: the reply without its demo banner and its "From:" lines:
    "DEMO: ...\\n\\nJoin plus to plus.\\n\\nFrom: Step 6 (Pack): Manual, page 15" gives "Join plus to plus."."""
    text = reply.text.removeprefix(DEMO_BANNER).strip()
    return text.split(SOURCES_MARK)[0].strip() if SOURCES_MARK in text else text


def rule_words(reply: Reply) -> str:
    """The words of the rule a warn or a stop names, "Safety rule SR-03: <words>", or "" for any other reply."""
    if reply.kind not in (ReplyKind.WARN, ReplyKind.STOP) or not reply.safety_rule_id:
        return ""
    rules = {rule.rule_id: rule for rule in load_rules()}
    rule = rules.get(reply.safety_rule_id)
    return f"Safety rule {reply.safety_rule_id}: {rule.words_shown}" if rule else f"Safety rule {reply.safety_rule_id}"


def render(reply: Reply) -> str:
    """The reply as shown: the rule's words first when a warn or a stop has them, then the door's text (which holds the
    demo banner and the citations): a plain answer renders as its own text."""
    words = rule_words(reply)
    return f"{words}\n\n{reply.text}" if words and words not in reply.text else reply.text


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


def converse(pack: Pack, demo: bool, answerer: Answerer, stdin: TextIO, stdout: TextIO, stderr: TextIO) -> None:
    """The loop: read a line, answer it with the history so far, print the reply, keep both turns. A line of "quit", or the
    end of input, ends it; a blank line is skipped; a model that cannot be used is told in words and the turn is not kept."""
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
            reply = answer(question, (pack,), demo, answerer, tuple(history))
        except ModelError as problem:
            stderr.write(f"Sorry: {problem}\n")
            continue
        stdout.write(render(reply) + "\n\n")
        history += [Turn("user", question), Turn("assistant", spoken(reply))]


def start_chat(pack_folder: str, demo: bool, answerer_name: str, stdin: TextIO, stdout: TextIO, stderr: TextIO,
               model: str = DEFAULT_MODEL) -> int:
    """Run a whole chat and return its exit code: 0 when it ended, 2 when it cannot run (a pack that is missing or may not
    answer, or no key for the Claude answerer), with one plain line on stderr. The demo banner is shown at the start."""
    try:
        pack = load_chat_pack(pack_folder, demo)
        answerer = choose_answerer(answerer_name, model)
    except (ValueError, ModelError) as problem:
        stderr.write(f"solarchat: cannot run: {problem}\n")
        return 2
    stdout.write((DEMO_BANNER + "\n\n" if demo else "") + f"{pack.manifest['title']}. Ask a question; type quit to end.\n\n")
    converse(pack, demo, answerer, stdin, stdout, stderr)
    return 0
