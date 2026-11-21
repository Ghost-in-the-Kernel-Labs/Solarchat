"""The live part of the evaluation runner: the Claude answerer on every case, each failure as a concrete block, the tokens
and cost, and the replies written for replay (TODO 1.16; SC-019, SC-021).

`--live` is the only way the model is called, by hand, and no gate script names it (SC-002). This file imports no model
client: `scripts/eval.py` builds the answerer here only when `--live` is given, and `solarchat.model.claude` loads the SDK
when it first needs it. The replies file is the design's 6.5 (`docs/designs/answering-door.md`), `RecordedAnswerer`'s.
"""
import json
from datetime import date
from pathlib import Path

from scripts.eval_core import ROOT, CannotRun, Result, Run, display
from scripts.eval_record import failed, table_lines
from solarchat.leaf.contract import DEMO_BANNER, Finding, Passage, Turn

REPLIES_PATH = ROOT / "evals" / "recorded" / "claude-sonnet-5-5.json"


class Recording:
    """An answerer that asks another and remembers each finding by question: Recording(inner).find("q", ()) gives what
    inner gives, and `findings["q"]` holds it. `name` is the inner answerer's."""

    def __init__(self, inner: object) -> None:
        """Wrap the answerer to record; start with no findings."""
        self.inner = inner
        self.name = inner.name
        self.findings: dict[str, Finding] = {}

    def find(self, question: str, passages: tuple[Passage, ...], history: tuple[Turn, ...] = ()) -> Finding:
        """Ask the inner answerer, keep the finding under the question's text, and return it."""
        finding = self.inner.find(question, passages, history)
        self.findings[question] = finding
        return finding

    @property
    def usage(self) -> object:
        """The inner answerer's token counts."""
        return self.inner.usage


def live_answerer() -> Recording:
    """The Claude answerer, recording; no key in the environment raises CannotRun (exit 2) in plain words."""
    from solarchat.model.claude import ClaudeAnswerer, ModelError  # only a live run loads the model module
    try:
        return Recording(ClaudeAnswerer())
    except ModelError as problem:
        raise CannotRun(str(problem)) from problem


def cited_ids(result: Result) -> str:
    """The passage ids a reply cites, "none" for no passage: a reply citing step-06 and step-07 gives "step-06, step-07"."""
    refs = result.reply.passage_refs if result.reply else ()
    return ", ".join(ref.passage_id for ref in refs) or "none"


def failure_block(result: Result, known: dict[str, dict]) -> list[str]:
    """One failure as the lines a worker of the evaluation reads: the case id and class, the question, what was expected,
    the kind the reply was and the passages and the rule it named, and the reply's words (the demo banner left out), with
    a note for a known failure. A failing "stop" case answered in words reads "got kind: answer"."""
    case, reply = result.case, result.reply
    lines = [f"FAIL {case['id']} [{case['class']}]", f"  question:  {case['question']}", f"  expected:  {result.expected}",
             f"  got kind:  {reply.kind.value if reply else 'none'} ({result.got})", f"  cited:     {cited_ids(result)}"]
    if reply and reply.safety_rule_id:
        lines.append(f"  rule:      {reply.safety_rule_id}")
    if case["id"] in known:
        lines.append(f"  known:     {known[case['id']]['why']}, until {known[case['id']]['until']}")
    words = (reply.text if reply else "").removeprefix(DEMO_BANNER).strip().splitlines()
    return lines + ["  reply:     " + (words[0] if words else "")] + [f"             {line}".rstrip() for line in words[1:]]


def usage_lines(usage: object) -> list[str]:
    """The tokens used and the estimated cost at Sonnet 5.5's rates, two lines: "tokens: 90 calls, input ..." then the
    dollars with the rates they rest on."""
    from solarchat.model.claude import estimated_cost
    return [f"tokens: {usage.calls} calls, input {usage.input_tokens}, output {usage.output_tokens}, cache read "
            f"{usage.cache_read_tokens}, cache write {usage.cache_write_tokens}",
            f"estimated cost: ${estimated_cost(usage):.4f} at $2/M input, $10/M output, $0.10/M cache read, $2.50/M cache write"]


def live_report(run: Run) -> list[str]:
    """What a live run prints before its verdict line: each failure's block, the score table, then the tokens and cost."""
    blocks: list[str] = []
    for result in failed(run):
        blocks += failure_block(result, run.known) + [""]
    return blocks + table_lines(run) + usage_lines(run.answerer.usage)


def finding_entry(finding: Finding) -> dict:
    """A finding as the replies file holds it: Finding(refs, "Join.", 0.0) gives {"refs": [[pack, passage]], "text": "Join.",
    "score": 0.0}."""
    return {"refs": [[ref.pack_id, ref.passage_id] for ref in finding.refs], "text": finding.text, "score": finding.score}


def replies_text(run: Run) -> str:
    """The replies file's text: `replies` by question text, which `RecordedAnswerer` replays, and `by_case`, the same
    findings by case id so a reader can find a case; every case of the run is in both."""
    recording = run.answerer
    cases = run.document["cases"]
    entries = {case["question"]: finding_entry(recording.findings.get(case["question"], Finding())) for case in cases}
    by_case = {case["id"]: dict(entries[case["question"]], question=case["question"]) for case in cases}
    document = {"version": 1, "set_sha256": run.set_sha, "answerer": recording.name, "recorded_on": date.today().isoformat(),
                "replies": entries, "by_case": by_case}
    return json.dumps(document, sort_keys=True, indent=2, ensure_ascii=False) + "\n"


def save_replies(run: Run, path: Path) -> str:
    """Write the replies file and say where: it may not be the set itself (CannotRun, the design's 6.6)."""
    if path.resolve() == run.set_path.resolve():
        raise CannotRun(f"--record-replies {path} is the set itself, which is never written (docs/designs/answering-door.md 6.6)")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(replies_text(run), encoding="utf-8")
    return f"replies written to {display(path)} ({len(run.results)} cases, by question and by case id)"
