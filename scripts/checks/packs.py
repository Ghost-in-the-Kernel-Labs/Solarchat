"""A knowledge pack is well formed, as docs/CONTRACT.md's "The pack format" states it (SC-005, SC-007, HAD-03 to HAD-06).

`problems(folder)` reads one pack folder (manifest.json, passages.json, flows.json, images/) and returns one line per
fault, `[]` for a well-formed pack. It reads the folder's files through scripts/checks/common.py, not the disk's walk
of a clone (C-001). It is not run over `packs/` yet: the demo pack is brought to the format in TODO 1.4. What it cannot
judge stays with the person who admits a pack: whether a licence allows redistribution, whether a passage is true.
"""
import json
import re
from datetime import date
from pathlib import Path

from scripts.checks.common import tracked_files

ID = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
MANIFEST_TEXT = ("id", "title", "make", "model", "version")
SOURCE_TEXT = ("id", "title", "url", "licence", "retrieved")
PICTURE_TEXT = ("file", "source_url", "owner", "licence", "shows")
PASSAGE_TEXT = ("id", "title", "text")
FLOW_TEXT = ("id", "title", "symptom", "fix", "stop")
THIRD_PARTY = "images/third-party/"


def blank(value: object) -> bool:
    """True unless value is a string with something in it: blank(" ") and blank(None) give True, blank("a") False."""
    return not isinstance(value, str) or not value.strip()


def missing(entry: object, fields: tuple[str, ...], where: str) -> list[str]:
    """One line per field of the object that is absent, blank or not text: missing({"id": ""}, ("id",), "x") gives
    ["x: id is missing or empty"]; an entry that is not an object gives one line."""
    if not isinstance(entry, dict):
        return [f"{where}: is not an object"]
    return [f"{where}: {field} is missing or empty" for field in fields if blank(entry.get(field))]


def load(folder: Path, name: str, found: list[str]) -> object:
    """The JSON in folder/name, or None with a line added to `found` when the file is absent or not JSON."""
    path = folder / name
    if not path.is_file():
        found.append(f"{name}: the file is missing")
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except ValueError as error:
        found.append(f"{name}: not valid JSON ({error})")
        return None


def objects(value: object, where: str, found: list[str]) -> list[dict]:
    """The value as a non-empty list of objects, or [] with a line added when it is not one."""
    if not isinstance(value, list) or not value:
        found.append(f"{where}: must be a non-empty list")
        return []
    if not all(isinstance(item, dict) for item in value):
        found.append(f"{where}: every item must be an object")
        return []
    return value


def admission_problems(manifest: dict) -> list[str]:
    """Both admitted_by and admitted_on null (not admitted), or both set: a name, and a date as YYYY-MM-DD (HAD-06)."""
    by, on = manifest.get("admitted_by"), manifest.get("admitted_on")
    if by is None and on is None:
        return []
    found = missing(manifest, ("admitted_by", "admitted_on"), "manifest.json")
    if not blank(on):
        try:
            date.fromisoformat(on)
        except ValueError:
            found.append("manifest.json: admitted_on is not a date as YYYY-MM-DD")
    return found


def source_problems(manifest: dict) -> tuple[list[str], set[str]]:
    """The lines for the manifest's sources and the set of their ids: a source with no licence gives
    "manifest.json source 'S1': licence is missing or empty"."""
    found: list[str] = []
    sources = objects(manifest.get("sources"), "manifest.json: sources", found)
    ids = [str(source.get("id")) for source in sources]
    for source in sources:
        found += missing(source, SOURCE_TEXT, f"manifest.json source {source.get('id')!r}")
    found += [f"manifest.json: source id {i!r} is used twice" for i in sorted(set(ids)) if ids.count(i) > 1]
    return found, set(ids)


def picture_entries(manifest: dict, found: list[str]) -> set[str]:
    """The files the manifest lists as third-party pictures, with a line for each entry that is incomplete."""
    listed = manifest.get("third_party_images", [])
    if not isinstance(listed, list) or not all(isinstance(item, dict) for item in listed):
        found.append("manifest.json: third_party_images must be a list of objects")
        return set()
    for item in listed:
        found += missing(item, PICTURE_TEXT, f"manifest.json third-party picture {item.get('file')!r}")
        if not str(item.get("file", "")).startswith(THIRD_PARTY):
            found.append(f"manifest.json third-party picture {item.get('file')!r}: file must sit under {THIRD_PARTY}")
    return {str(item.get("file")) for item in listed}


def manifest_problems(manifest: object) -> tuple[list[str], set[str], set[str]]:
    """The manifest's lines, its source ids and its listed third-party picture files."""
    if not isinstance(manifest, dict):
        return ["manifest.json: is not an object"], set(), set()
    found = missing(manifest, MANIFEST_TEXT, "manifest.json") + admission_problems(manifest)
    if not blank(manifest.get("id")) and not ID.match(manifest["id"]):
        found.append("manifest.json: id must be lowercase words joined by hyphens")
    more, ids = source_problems(manifest)
    found += more
    listed = picture_entries(manifest, found)
    return found, ids, listed


def picture_problems(entry: dict, where: str, folder: Path) -> list[str]:
    """A picture on a passage or a check: a path under images/ that exists in the pack, and alt text for it."""
    image = entry.get("image")
    if image is None:
        return []
    if blank(image) or not image.startswith("images/") or ".." in Path(image).parts:
        return [f"{where}: image must be a path under images/"]
    found = [] if (folder / image).is_file() else [f"{where}: image {image!r} is not in the pack"]
    return found + missing(entry, ("image_alt",), where)


def reference_problems(entry: dict, where: str, ids: set[str]) -> list[str]:
    """The entry's `sources`: a non-empty list of ids the manifest has ("passage 'p' names no source" is the break)."""
    cited = entry.get("sources")
    if not isinstance(cited, list) or not cited or not all(isinstance(c, str) for c in cited):
        return [f"{where}: sources must name at least one source"]
    return [f"{where}: source {c!r} is not in the manifest" for c in cited if c not in ids]


def passage_problems(passages: list[dict], ids: set[str], folder: Path) -> list[str]:
    """Each passage has an id, title, text, a source from the manifest, and a sound picture if it has one."""
    found: list[str] = []
    for passage in passages:
        where = f"passage {passage.get('id')!r}"
        found += missing(passage, PASSAGE_TEXT, where) + reference_problems(passage, where, ids)
        found += picture_problems(passage, where, folder)
    return found


def check_problems(flow: dict, where: str, folder: Path) -> list[str]:
    """A flow's checks: a non-empty list, each an object with text and, if it has a picture, a sound one."""
    checks = flow.get("checks")
    if not isinstance(checks, list) or not checks:
        return [f"{where}: checks must be a non-empty list"]
    found: list[str] = []
    for number, check in enumerate(checks, start=1):
        found += missing(check, ("text",), f"{where} check {number}")
        found += picture_problems(check, f"{where} check {number}", folder) if isinstance(check, dict) else []
    return found


def flow_problems(flows: list[dict], ids: set[str], folder: Path) -> list[str]:
    """Each flow has a symptom, checks, a fix, a stop (where to send the worker), and a source from the manifest."""
    found: list[str] = []
    for flow in flows:
        where = f"flow {flow.get('id')!r}"
        found += missing(flow, FLOW_TEXT, where) + reference_problems(flow, where, ids)
        found += check_problems(flow, where, folder)
    return found


def id_problems(entries: list[dict]) -> list[str]:
    """Passage and flow ids share one namespace: each is lowercase words with hyphens, and none is used twice."""
    names = [str(entry.get("id")) for entry in entries if not blank(entry.get("id"))]
    found = [f"id {n!r} must be lowercase words joined by hyphens" for n in names if not ID.match(n)]
    return found + [f"id {n!r} is used twice among the passages and flows" for n in sorted(set(names)) if names.count(n) > 1]


def unlisted_pictures(folder: Path, listed: set[str]) -> list[str]:
    """A file under images/third-party/ the manifest does not list, and a listed file that is not there (SC-007)."""
    on_disk = {p.relative_to(folder).as_posix() for p in tracked_files(folder) if p.is_file()}
    present = {name for name in on_disk if name.startswith(THIRD_PARTY)}
    found = [f"{name}: a third-party picture with no entry in the manifest" for name in sorted(present - listed)]
    return found + [f"{name}: listed in the manifest and not in the pack" for name in sorted(listed - on_disk)]


def problems(folder: Path) -> list[str]:
    """Every fault in the pack folder, in a stable order; [] when it is well formed."""
    found: list[str] = []
    manifest = load(folder, "manifest.json", found)
    passages, flows = load(folder, "passages.json", found), load(folder, "flows.json", found)
    more, ids, listed = manifest_problems(manifest) if manifest is not None else ([], set(), set())
    found += more
    if isinstance(manifest, dict) and manifest.get("id") not in (None, folder.name):
        found.append(f"manifest.json: id {manifest.get('id')!r} is not the folder's name {folder.name!r}")
    passage_list = objects(passages, "passages.json", found) if passages is not None else []
    flow_list = objects(flows, "flows.json", found) if flows is not None else []
    found += passage_problems(passage_list, ids, folder) + flow_problems(flow_list, ids, folder)
    return found + id_problems(passage_list + flow_list) + unlisted_pictures(folder, listed)
