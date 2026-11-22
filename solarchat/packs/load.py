"""Loads a knowledge pack from its folder and words the citations of its passages (TODO 1.6; SC-012, SC-019).

A pack folder holds `manifest.json` and `passages.json`; flows and procedures are not read, since their text is in the
passages already (J-038). The loader does not re-run the pack check: `scripts/checks/packs.py` is the check, and a pack
that passed it is trusted here. Standard library and the leaf only.
"""
import json
from dataclasses import dataclass
from pathlib import Path

from solarchat.leaf.contract import Passage, PassageRef, SafetyCoverage

MANIFEST_FIELDS = ("id", "title", "version", "status", "sources")
PASSAGE_FIELDS = ("id", "title", "text", "sources")
UNKNOWN_PAGE = "unknown"


@dataclass(frozen=True)
class Pack:
    """One loaded pack: Pack("seed-mc4-leads", manifest, passages, citations) with `citations` the passage id to its
    `sources` list as written ("S2", or {"source": "S3", "page": "15"}); `coverage` is the manifest's `safety_coverage` as leaf
    records, () when the manifest has none (SC-024)."""

    pack_id: str
    manifest: dict
    passages: tuple[Passage, ...]
    citations: dict[str, list]
    coverage: tuple[SafetyCoverage, ...] = ()


def read_json(path: Path) -> object:
    """The JSON in path; a missing file or a file that is not JSON raises ValueError naming it: read_json(Path("x"))
    raises "x: the file is missing"."""
    if not path.is_file():
        raise ValueError(f"{path}: the file is missing")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except ValueError as error:
        raise ValueError(f"{path}: not valid JSON ({error})") from error


def missing_field(entry: object, fields: tuple[str, ...]) -> str | None:
    """The first of `fields` an entry lacks, or None: missing_field({"id": "a"}, ("id", "text")) gives "text"."""
    if not isinstance(entry, dict):
        return fields[0]
    return next((name for name in fields if name not in entry), None)


def passage_from_entry(pack_id: str, entry: dict) -> Passage:
    """One passages.json entry as a leaf Passage: {"id": "step-01", "title": "T", "text": "x", "sources": []} gives
    Passage(PassageRef(pack_id, "step-01"), "x", "T")."""
    return Passage(PassageRef(pack_id, entry["id"]), entry["text"], entry["title"])


def passage_entries(folder: Path) -> list[dict]:
    """The entries of folder's passages.json, [] when the file is absent; a missing field raises ValueError naming the
    file and passage: a passage with no "text" gives "passages.json: passage 2 has no 'text'"."""
    path = folder / "passages.json"
    entries = read_json(path) if path.exists() else []
    if not isinstance(entries, list):
        raise ValueError(f"{path}: not a list of passages")
    for number, entry in enumerate(entries, start=1):
        absent = missing_field(entry, PASSAGE_FIELDS)
        if absent:
            raise ValueError(f"{path}: passage {number} has no {absent!r}")
    return entries


# Decision: SC-024 (a manifest's safety_coverage is read into leaf records; the pack check is what refuses a bad one)
def coverage_from_manifest(manifest: dict) -> tuple[SafetyCoverage, ...]:
    """The manifest's declarations as SafetyCoverage records, () when absent: {"safety_coverage": [{"rule": "SR-02",
    "response": "warn", "passages": ["a"]}]} gives (SafetyCoverage("SR-02", "warn", ("a",)),). A malformed one raises ValueError."""
    entries = manifest.get("safety_coverage") or []
    if not isinstance(entries, list) or not all(isinstance(entry, dict) for entry in entries):
        raise ValueError("manifest.json: safety_coverage is not a list of declarations")
    return tuple(SafetyCoverage(entry.get("rule"), entry.get("response"), tuple(entry.get("passages") or ()), entry.get("declared"))
                 for entry in entries)


# Decision: SC-019 (load_pack reads manifest and passages and names the file and field that is missing)
def load_pack(folder: Path) -> Pack:
    """The pack in folder; a missing manifest, or a missing field of the manifest or of a passage, raises ValueError
    naming the file ("manifest.json: no 'status'"); no passages.json means no passages. load_pack(Path("packs/x")) gives
    a Pack whose pack_id is the manifest's id."""
    manifest = read_json(folder / "manifest.json")
    absent = missing_field(manifest, MANIFEST_FIELDS)
    if absent:
        raise ValueError(f"{folder / 'manifest.json'}: no {absent!r}")
    entries = passage_entries(folder)
    passages = tuple(passage_from_entry(manifest["id"], entry) for entry in entries)
    citations = {entry["id"]: entry["sources"] for entry in entries}
    return Pack(manifest["id"], manifest, passages, citations, coverage_from_manifest(manifest))


def page_words(page: object) -> str:
    """The words for a page: page_words("15") gives "page 15"; page_words("unknown") gives "page not yet found"."""
    return "page not yet found" if page == UNKNOWN_PAGE else f"page {page}"


# Decision: SC-012 (a document source is cited with its page, "page not yet found" for an unknown one, a web source by title)
def citation_lines(pack: Pack, passage_id: str) -> tuple[str, ...]:
    """One line per source of the passage: ("Trina manual, page 15", "Trina manual, page not yet found", "A web page").
    An unknown passage or source raises ValueError."""
    if passage_id not in pack.citations:
        raise ValueError(f"{pack.pack_id}: no passage {passage_id!r}")
    titles = {source["id"]: source for source in pack.manifest["sources"]}
    lines = []
    for cited in pack.citations[passage_id]:
        cited_id = cited["source"] if isinstance(cited, dict) else cited
        if cited_id not in titles:
            raise ValueError(f"{pack.pack_id}: passage {passage_id!r} cites {cited_id!r}, not in the manifest's sources")
        title = titles[cited_id]["title"]
        lines.append(f"{title}, {page_words(cited['page'])}" if isinstance(cited, dict) else title)
    return tuple(lines)
