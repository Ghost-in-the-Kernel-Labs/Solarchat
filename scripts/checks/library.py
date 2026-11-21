"""The reference library's sources are well formed (SC-014; licences as SC-005 and SC-012 treat them for packs).

`python3 -I scripts/checks/library.py [root]` prints one line per fault in `<root>/library/sources/*/` (root defaults to the
project's root) and exits 1 on any. Each source folder holds `source.json`, `text.txt` and, when the original is small and
licensed for it, `original.*`. The check holds that: `source.json` has every required field; `kind` is "document" or "web"
and a document has a page count; `licence` is one of the allow-list of three; a CC BY source carries an attribution;
`sha256` is 64 hex characters and, when an `original.*` is present, is the hash of its bytes; `text.txt` exists and is not
empty; and the folder's name is the source's `id`.

It reads the files through scripts/checks/common.py, so a file a clone would not hold is not read (C-001). What it cannot
judge stays with the person who loads the library: whether the quoted `licence_evidence` is the publisher's own words,
whether a third-party picture was left out, and whether the text is true to the original.
"""
import hashlib
import json
import re
import sys
from pathlib import Path

if __name__ == "__main__":  # run as a script from the project's root: the root holds the scripts package
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.checks.common import tracked_files  # noqa: E402

SOURCES_PARTS = ("library", "sources")
REQUIRED_TEXT_FIELDS = ("id", "title", "publisher", "url", "retrieved", "kind", "licence", "licence_evidence", "licence_url", "sha256")
SOURCE_KINDS = ("document", "web")
LICENCES = ("public domain (US federal work)", "CC BY 4.0", "Open Government Licence v3.0")
CC_BY = "CC BY 4.0"
SHA256_PATTERN = re.compile(r"^[0-9a-fA-F]{64}$")


def is_blank(value: object) -> bool:
    """True unless value is a string with something in it: is_blank(" ") and is_blank(None) give True, is_blank("a") False."""
    return not isinstance(value, str) or not value.strip()


# Decision: SC-014 (every source states what it is, who published it, where it came from, and under what licence)
def field_problems(record: dict) -> list[str]:
    """One line per required text field that is absent or blank: a record with no `url` gives ["url is missing or empty"]."""
    return [f"{field} is missing or empty" for field in REQUIRED_TEXT_FIELDS if is_blank(record.get(field))]


# Decision: SC-014 (a source is a document with pages or a web page without, as SC-012 says of a pack's sources)
def kind_problems(record: dict) -> list[str]:
    """`kind` must be "document" or "web", and a document needs `pages`, a positive whole number: kind "document" with
    pages "x" gives ["pages must be a positive whole number for a document"]."""
    kind = record.get("kind")
    if kind not in SOURCE_KINDS:
        return [] if is_blank(kind) else ['kind must be "document" or "web"']
    pages = record.get("pages")
    if kind == "document" and (not isinstance(pages, int) or isinstance(pages, bool) or pages < 1):
        return ["pages must be a positive whole number for a document"]
    return []


# Decision: SC-014 (only three licences are on the allow-list; a CC BY source carries the attribution its publisher asks for)
def licence_problems(record: dict) -> list[str]:
    """`licence` must be on the allow-list, and a "CC BY 4.0" source needs a non-blank `attribution`: licence "All rights
    reserved" gives ["licence 'All rights reserved' is not on the allow-list (...)"]."""
    licence = record.get("licence")
    if is_blank(licence):
        return []
    if licence not in LICENCES:
        return [f"licence {licence!r} is not on the allow-list ({'; '.join(LICENCES)})"]
    if licence == CC_BY and is_blank(record.get("attribution")):
        return ["a CC BY 4.0 source needs an attribution"]
    return []


# Decision: SC-014 (the hash is the original's identity; a kept original must match it)
def hash_problems(record: dict, originals: list[Path]) -> list[str]:
    """`sha256` must be 64 hex characters, and equal the SHA-256 of each `original.*` kept: a hash of 63 characters gives
    ["sha256 must be 64 hex characters"]; a kept file that differs gives ["original.html does not match sha256"]."""
    sha = record.get("sha256")
    if is_blank(sha):
        return []
    if not SHA256_PATTERN.match(sha):
        return ["sha256 must be 64 hex characters"]
    return [f"{path.name} does not match sha256" for path in originals if hashlib.sha256(path.read_bytes()).hexdigest() != sha.lower()]


# Decision: SC-014 (text.txt is what later packs and the safety rules cite, so it must exist)
def text_problems(text_path: Path | None) -> list[str]:
    """text.txt must exist and hold something besides whitespace: no file gives ["text.txt is missing"]; a file of
    spaces gives ["text.txt is empty"]."""
    if text_path is None:
        return ["text.txt is missing"]
    if not text_path.read_text(encoding="utf-8", errors="replace").strip():
        return ["text.txt is empty"]
    return []


def read_record(path: Path | None, faults: list[str]) -> dict | None:
    """The object in source.json, or None with a line added to `faults` when it is absent, not JSON or not an object."""
    if path is None:
        faults.append("source.json is missing")
        return None
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
    except ValueError as error:
        faults.append(f"source.json is not valid JSON ({error})")
        return None
    if not isinstance(record, dict):
        faults.append("source.json is not an object")
        return None
    return record


# Decision: SC-014 (the folder's name is the source's id, so a citation finds its folder)
def source_problems(name: str, files: dict[str, Path]) -> list[str]:
    """Every fault in one source folder called `name` whose files, by name, are `files`; [] when it is well formed. A line
    starts with the folder's name: "bad-id: id 'x' is not the folder's name"."""
    faults: list[str] = []
    record = read_record(files.get("source.json"), faults)
    if record is not None:
        originals = [path for file_name, path in sorted(files.items()) if file_name.startswith("original.")]
        faults += field_problems(record) + kind_problems(record) + licence_problems(record) + hash_problems(record, originals)
        if not is_blank(record.get("id")) and record.get("id") != name:
            faults.append(f"id {record.get('id')!r} is not the folder's name")
    faults += text_problems(files.get("text.txt"))
    return [f"{name}: {fault}" for fault in faults]


def source_files(root: Path) -> dict[str, dict[str, Path]]:
    """The files of each source folder under root/library/sources, from git's list: {"a": {"source.json": Path(...)}}."""
    found: dict[str, dict[str, Path]] = {}
    for path in tracked_files(root):
        parts = path.relative_to(root).parts
        if parts[:2] == SOURCES_PARTS and len(parts) == 4:
            found.setdefault(parts[2], {})[parts[3]] = path
    return found


def problems(root: Path) -> list[str]:
    """Every fault in the library under root, folder by folder in name order; [] for a library with none (or no sources)."""
    faults: list[str] = []
    for name, files in sorted(source_files(root).items()):
        faults += source_problems(name, files)
    return faults


def main(arguments: list[str]) -> int:
    """Print the library's faults; exit 1 on a fault: `library.py` prints "ok" for a clean library."""
    root = Path(arguments[0]) if arguments else Path(__file__).resolve().parents[2]
    faults = problems(root)
    print("\n".join(faults) if faults else f"ok: {len(source_files(root))} source(s) well formed")
    return 1 if faults else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
