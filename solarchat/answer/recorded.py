"""The answerer that replays a replies file: deterministic, offline, the model mode in tests (SC-019; roadmap 3.3).

A replies file is `{"version": 1, "set_sha256": "...", "answerer": "claude-...", "recorded_on": "2026-12-01",
"replies": {"<question text>": {"refs": [["seed-mc4-leads", "step-06"]], "text": "...", "score": 4.5}}}`; `score` is optional.
"""
import json
from pathlib import Path

from solarchat.leaf.contract import Finding, Passage, PassageRef

REPLIES_VERSION = 1


def finding_from_entry(entry: dict) -> Finding:
    """One recorded reply as a Finding: {"refs": [["p", "step-06"]], "text": "Join."} gives
    Finding((PassageRef("p", "step-06"),), "Join.", 0.0); a malformed entry raises ValueError."""
    refs = tuple(PassageRef(pack_id, passage_id) for pack_id, passage_id in entry["refs"])
    return Finding(refs, entry["text"], float(entry.get("score", 0.0)))


class RecordedAnswerer:
    """Replays recorded findings by the exact question text; a question not recorded gets Finding().

    RecordedAnswerer(Path("evals/recorded/run.json")).name is the file's `answerer`; `set_sha256` is the set it was
    recorded against, which the runner holds equal to the set's. Decision: SC-019.
    """

    def __init__(self, path: Path) -> None:
        """Read the replies file at path; one that is missing, not JSON or the wrong shape raises ValueError naming it."""
        try:
            document = json.loads(Path(path).read_text(encoding="utf-8"))
            if document["version"] != REPLIES_VERSION:
                raise ValueError(f"version {document['version']!r}, not {REPLIES_VERSION}")
            self.name = str(document["answerer"])
            self.set_sha256 = str(document["set_sha256"])
            self.findings = {question: finding_from_entry(entry) for question, entry in document["replies"].items()}
        except (OSError, ValueError, KeyError, TypeError, AttributeError) as error:
            raise ValueError(f"{path}: not a replies file ({error})") from error

    def find(self, question: str, passages: tuple[Passage, ...]) -> Finding:
        """The recorded finding for this exact question, else an empty one: find("not recorded", ()) gives Finding()."""
        return self.findings.get(question, Finding())
