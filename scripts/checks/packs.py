"""A knowledge pack is well formed, as docs/CONTRACT.md's "The pack format" states it (SC-005, SC-007, SC-013, HAD-03 to HAD-06).

`python3 -I scripts/checks/packs.py <pack folder>` prints the faults and, how many pages are still unknown (SC-012). A pack's
`status` is `field` or `demo`; a `field` pack with an unknown page is refused, a `demo` pack is not (SC-013).

A pack may not name a safety rule (`SR-` and digits) or tell the reader to ignore, skip, bypass, override or disregard a
safety rule, a stop or the supervisor (HAD-04, TODO 1.3). The override phrases are a short conservative list: a
paraphrase ("carry on anyway", "the stop does not apply here") passes it, and stays with the person who loads the packs.

`problems(folder)` reads one pack folder (manifest.json, then passages.json, flows.json, procedures.json, images/) and returns one line per
fault, `[]` for a well-formed pack. It reads the folder's files through scripts/checks/common.py, not the disk's walk
of a clone (C-001). `test/test_packs.py` runs it over the seed pack (TODO 1.4). What it cannot
judge stays with the person who loads the packs: whether a licence allows redistribution, whether a passage is true.
"""
import json
import re
import sys
from pathlib import Path

if __name__ == "__main__":  # run as a script from the project's root: the root holds the scripts package
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.checks.common import tracked_files  # noqa: E402
from scripts.checks.coverage import coverage_lines, coverage_problems  # noqa: E402

ID_PATTERN = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
MANIFEST_TEXT_FIELDS = ("id", "title", "version")
SOURCE_TEXT_FIELDS = ("id", "title", "url", "licence", "retrieved")
SOURCE_KINDS = ("document", "web")
UNKNOWN_PAGE = "unknown"
PACK_STATUSES = ("field", "demo")
THIRD_PARTY_PICTURE_TEXT_FIELDS = ("file", "source_url", "owner", "licence", "shows")
PASSAGE_TEXT_FIELDS = ("id", "title", "text")
FLOW_TEXT_FIELDS = ("id", "title", "symptom", "fix", "stop")
PROCEDURE_TEXT_FIELDS = ("id", "title")
STEP_TEXT_FIELDS = ("text", "right_looks_like")
THIRD_PARTY_PICTURE_FOLDER = "images/third-party/"
SAFETY_RULE_ID_IN_TEXT = re.compile(r"\bSR-\d+\b", re.IGNORECASE)
OVERRIDE_VERBS = r"(?:ignore|ignoring|skip|skipping|bypass|bypassing|override|overriding|disregard|disregarding)"
OVERRIDE_TARGETS = (r"(?:safety (?:rules?|checks?|steps?|procedures?|warnings?|instructions?|advice)"
                    r"|(?:the|this|that|a|any|each|every) stops?|supervisor|engineer)")
NO_NEED_TO_ASK = r"(?:no need|(?:do not|don't|dont) need) to (?:ask|call|tell|go to|contact|wait for|check with)"
OVERRIDE_PHRASE = re.compile(rf"\b{OVERRIDE_VERBS}\b(?:\W+\w+){{0,3}}?\W+{OVERRIDE_TARGETS}\b"
                             rf"|\b{NO_NEED_TO_ASK}\W+(?:\w+\W+){{0,2}}?(?:supervisor|engineer)\b", re.IGNORECASE)
NEGATION_WORDS = ("never", "not", "don't", "dont", "cannot", "can't", "nor")


def is_blank(value: object) -> bool:
    """True unless value is a string with something in it: is_blank(" ") and is_blank(None) give True, is_blank("a") False."""
    return not isinstance(value, str) or not value.strip()


def missing_fields(entry: object, fields: tuple[str, ...], location: str) -> list[str]:
    """One line per field of the object that is absent, blank or not text: missing_fields({"id": ""}, ("id",), "x") gives
    ["x: id is missing or empty"]; an entry that is not an object gives one line."""
    if not isinstance(entry, dict):
        return [f"{location}: is not an object"]
    return [f"{location}: {field} is missing or empty" for field in fields if is_blank(entry.get(field))]


def load_json(folder: Path, name: str, faults: list[str]) -> object:
    """The JSON in folder/name, or None with a line added to `faults` when the file is absent or not JSON."""
    path = folder / name
    if not path.is_file():
        faults.append(f"{name}: the file is missing")
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except ValueError as error:
        faults.append(f"{name}: not valid JSON ({error})")
        return None


def load_optional_list(folder: Path, name: str, faults: list[str]) -> list[dict]:
    """The objects in folder/name, a file that may be absent (then []) or hold an empty list; faults add lines."""
    if not (folder / name).is_file():
        return []
    loaded = load_json(folder, name, faults)
    return [] if loaded is None else list_of_objects(loaded, name, faults, empty_list_allowed=True)


def list_of_objects(value: object, location: str, faults: list[str], empty_list_allowed: bool = False) -> list[dict]:
    """The value as a list of objects, non-empty unless empty_list_allowed, or [] with a line added when it is not one."""
    if not isinstance(value, list) or (not value and not empty_list_allowed):
        faults.append(f"{location}: must be a non-empty list")
        return []
    if not all(isinstance(item, dict) for item in value):
        faults.append(f"{location}: every item must be an object")
        return []
    return value


# Decision: SC-013 (a pack is a field pack or a demo pack; no approval is recorded in the manifest)
# Invariant: HAD-06 (a demo pack never answers outside demo mode)
def status_problems(manifest: dict) -> list[str]:
    """The manifest's `status` must be exactly "field" or "demo": a manifest with none, or with "draft", gives
    ['manifest.json: status must be "field" or "demo"']."""
    if manifest.get("status") in PACK_STATUSES:
        return []
    return ['manifest.json: status must be "field" or "demo"']


def identity_problems(manifest: dict) -> list[str]:
    """What the pack covers: make and model together, or installation_type, or all three; never make alone or neither."""
    make_is_blank, model_is_blank = is_blank(manifest.get("make")), is_blank(manifest.get("model"))
    installation_type = manifest.get("installation_type")
    faults = ["manifest.json: installation_type is empty"] if installation_type is not None and is_blank(installation_type) else []
    if make_is_blank != model_is_blank:
        return faults + ["manifest.json: make and model go together"]
    if make_is_blank and is_blank(installation_type):
        faults.append("manifest.json: needs make and model, or installation_type")
    return faults


# Decision: SC-012 (a source says whether it is a document with pages or a web page without)
def kind_problems(source: dict) -> list[str]:
    """A source's `kind` must be "document" or "web": a source with no kind gives
    ["manifest.json source 'S1': kind must be \"document\" or \"web\""]."""
    if source.get("kind") in SOURCE_KINDS:
        return []
    return [f"manifest.json source {source.get('id')!r}: kind must be \"document\" or \"web\""]


# Decision: SC-005 (every source carries its licence, weighed by the person who loads the packs)
# Decision: SC-012 (every source carries its kind, which says how it is cited)
def source_problems(manifest: dict) -> tuple[list[str], dict[str, object]]:
    """The lines for the manifest's sources and a map from each source's id to its kind: a source with no licence gives
    "manifest.json source 'S1': licence is missing or empty"; ids {"S1": "document", "S2": "web"} come back as that map."""
    faults: list[str] = []
    sources = list_of_objects(manifest.get("sources"), "manifest.json: sources", faults)
    source_ids = [str(source.get("id")) for source in sources]
    for source in sources:
        faults += missing_fields(source, SOURCE_TEXT_FIELDS, f"manifest.json source {source.get('id')!r}") + kind_problems(source)
    faults += [f"manifest.json: source id {source_id!r} is used twice" for source_id in sorted(set(source_ids)) if source_ids.count(source_id) > 1]
    return faults, {str(source.get("id")): source.get("kind") for source in sources}


# Decision: SC-007 (a picture from the web is listed with its provenance)
def picture_entries(manifest: dict, faults: list[str]) -> set[str]:
    """The files the manifest lists as third-party pictures, with a line for each entry that is incomplete."""
    listed_picture_files = manifest.get("third_party_images", [])
    if not isinstance(listed_picture_files, list) or not all(isinstance(picture_entry, dict) for picture_entry in listed_picture_files):
        faults.append("manifest.json: third_party_images must be a list of objects")
        return set()
    for picture_entry in listed_picture_files:
        faults += missing_fields(picture_entry, THIRD_PARTY_PICTURE_TEXT_FIELDS, f"manifest.json third-party picture {picture_entry.get('file')!r}")
        if not str(picture_entry.get("file", "")).startswith(THIRD_PARTY_PICTURE_FOLDER):
            faults.append(f"manifest.json third-party picture {picture_entry.get('file')!r}: file must sit under {THIRD_PARTY_PICTURE_FOLDER}")
    return {str(picture_entry.get("file")) for picture_entry in listed_picture_files}


def manifest_problems(manifest: object) -> tuple[list[str], dict[str, object], set[str]]:
    """The manifest's lines, its sources' kinds by id and its listed third-party picture files."""
    if not isinstance(manifest, dict):
        return ["manifest.json: is not an object"], {}, set()
    faults = missing_fields(manifest, MANIFEST_TEXT_FIELDS, "manifest.json") + identity_problems(manifest) + status_problems(manifest)
    if not is_blank(manifest.get("id")) and not ID_PATTERN.match(manifest["id"]):
        faults.append("manifest.json: id must be lowercase words joined by hyphens")
    manifest_faults, source_kinds = source_problems(manifest)
    faults += manifest_faults
    listed_picture_files = picture_entries(manifest, faults)
    return faults, source_kinds, listed_picture_files


def picture_problems(entry: dict, location: str, folder: Path) -> list[str]:
    """A picture on a passage or a check: a path under images/ that exists in the pack, and alt text for it."""
    image_path = entry.get("image")
    if image_path is None:
        return []
    if is_blank(image_path) or not image_path.startswith("images/") or ".." in Path(image_path).parts:
        return [f"{location}: image must be a path under images/"]
    faults = [] if (folder / image_path).is_file() else [f"{location}: image {image_path!r} is not in the pack"]
    return faults + missing_fields(entry, ("image_alt",), location)


def citation_problems(cited: object, location: str, source_kinds: dict[str, object]) -> list[str]:
    """One citation: a bare id for a web source, or {"source", "page"} for a document source; the break for a bare id of a
    document is "passage 'p': source 'S3' is a document: cite it as {"source": "S3", "page": ...}"."""
    cited_id = cited.get("source") if isinstance(cited, dict) else cited
    if not isinstance(cited_id, str):
        return [f"{location}: each source must be an id, or an object with source and page"]
    if cited_id not in source_kinds:
        return [f"{location}: source {cited_id!r} is not in the manifest"]
    kind = source_kinds[cited_id]
    if kind == "document" and not isinstance(cited, dict):
        return [f"{location}: source {cited_id!r} is a document: cite it as {{\"source\": {cited_id!r}, \"page\": ...}}"]
    if kind == "web" and isinstance(cited, dict):
        return [f"{location}: source {cited_id!r} is a web page: cite it by its id alone, with no page"]
    if isinstance(cited, dict) and kind == "document" and is_blank(cited.get("page")):
        return [f"{location}: source {cited_id!r}: page is missing or empty"]
    return []


# Invariant: HAD-03 (an answer names the passage it came from, and a passage its source)
# Decision: SC-012 (a document source is cited with its page, a web source without)
def reference_problems(entry: dict, location: str, source_kinds: dict[str, object]) -> list[str]:
    """The entry's `sources`: a non-empty list of citations the manifest's sources allow ("passage 'p' names no source" is the break)."""
    citations = entry.get("sources")
    if not isinstance(citations, list) or not citations:
        return [f"{location}: sources must name at least one source"]
    return [fault for cited in citations for fault in citation_problems(cited, location, source_kinds)]


# Decision: SC-012 (a page marked unknown is counted, so the gap is visible)
def unknown_pages(passages: list[dict], flows: list[dict], procedures: list[dict]) -> list[str]:
    """One line per citation whose page is "unknown": ["passage 'p': source 'S3'"] for a passage citing S3 so."""
    lines: list[str] = []
    for kind_name, entries in (("passage", passages), ("flow", flows), ("procedure", procedures)):
        for entry in entries:
            citations = entry.get("sources") if isinstance(entry.get("sources"), list) else []
            lines += [f"{kind_name} {entry.get('id')!r}: source {cited.get('source')!r}" for cited in citations
                      if isinstance(cited, dict) and cited.get("page") == UNKNOWN_PAGE]
    return lines


# Decision: SC-013 (a field pack holds no unknown page; a demo pack may, and the count still shows it)
def unknown_page_problems(manifest: object, passages: list[dict], flows: list[dict], procedures: list[dict]) -> list[str]:
    """One line per unknown page when the pack's status is "field", none for a demo pack:
    "passage 'p': source 'S3': page is unknown; a field pack cites every page (SC-013)"."""
    if not isinstance(manifest, dict) or manifest.get("status") != "field":
        return []
    return [f"{citation}: page is unknown; a field pack cites every page (SC-013)" for citation in unknown_pages(passages, flows, procedures)]


def passage_problems(passages: list[dict], source_kinds: dict[str, object], folder: Path) -> list[str]:
    """Each passage has an id, title, text, a source from the manifest, and a sound picture if it has one."""
    faults: list[str] = []
    for passage in passages:
        location = f"passage {passage.get('id')!r}"
        faults += missing_fields(passage, PASSAGE_TEXT_FIELDS, location) + reference_problems(passage, location, source_kinds)
        faults += picture_problems(passage, location, folder)
    return faults


def check_problems(flow: dict, location: str, folder: Path) -> list[str]:
    """A flow's checks: a non-empty list, each an object with text and, if it has a picture, a sound one."""
    flow_checks = flow.get("checks")
    if not isinstance(flow_checks, list) or not flow_checks:
        return [f"{location}: checks must be a non-empty list"]
    faults: list[str] = []
    for check_number, flow_check in enumerate(flow_checks, start=1):
        faults += missing_fields(flow_check, ("text",), f"{location} check {check_number}")
        faults += picture_problems(flow_check, f"{location} check {check_number}", folder) if isinstance(flow_check, dict) else []
    return faults


# Invariant: HAD-04 (a flow ends at a stop that sends the worker to the supervisor)
def flow_problems(flows: list[dict], source_kinds: dict[str, object], folder: Path) -> list[str]:
    """Each flow has a symptom, checks, a fix, a stop (where to send the worker), and a source from the manifest."""
    faults: list[str] = []
    for flow in flows:
        location = f"flow {flow.get('id')!r}"
        faults += missing_fields(flow, FLOW_TEXT_FIELDS, location) + reference_problems(flow, location, source_kinds)
        faults += check_problems(flow, location, folder)
    return faults


def step_problems(procedure: dict, location: str, folder: Path) -> list[str]:
    """A procedure's steps: a non-empty list; each has an id unique in the procedure, text, right_looks_like, a sound
    picture if it has one, and, if it has a stop, words in it."""
    steps = procedure.get("steps")
    if not isinstance(steps, list) or not steps:
        return [f"{location}: steps must be a non-empty list"]
    faults: list[str] = []
    step_ids = [str(step.get("id")) for step in steps if isinstance(step, dict)]
    for step_number, step in enumerate(steps, start=1):
        step_label = f"{location} step {step.get('id') if isinstance(step, dict) and step.get('id') else step_number}"
        faults += missing_fields(step, ("id",) + STEP_TEXT_FIELDS, step_label)
        if isinstance(step, dict):
            faults += picture_problems(step, step_label, folder)
            faults += missing_fields(step, ("stop",), step_label) if "stop" in step else []
    return faults + [f"{location}: step id {step_id!r} is used twice" for step_id in sorted(set(step_ids)) if step_ids.count(step_id) > 1]


def procedure_problems(procedures: list[dict], source_kinds: dict[str, object], folder: Path) -> list[str]:
    """Each procedure has an id, a title, a source from the manifest and sound steps."""
    faults: list[str] = []
    for procedure in procedures:
        location = f"procedure {procedure.get('id')!r}"
        faults += missing_fields(procedure, PROCEDURE_TEXT_FIELDS, location) + reference_problems(procedure, location, source_kinds)
        faults += step_problems(procedure, location, folder)
    return faults


def id_problems(entries: list[dict]) -> list[str]:
    """Passage, flow and procedure ids share one namespace: each is lowercase words with hyphens, and none is used twice."""
    entry_ids = [str(entry.get("id")) for entry in entries if not is_blank(entry.get("id"))]
    faults = [f"id {entry_id!r} must be lowercase words joined by hyphens" for entry_id in entry_ids if not ID_PATTERN.match(entry_id)]
    return faults + [f"id {entry_id!r} is used twice among the passages, flows and procedures" for entry_id in sorted(set(entry_ids)) if entry_ids.count(entry_id) > 1]


# Decision: SC-007 (a picture from the web is listed with its provenance)
def unlisted_pictures(folder: Path, listed_picture_files: set[str]) -> list[str]:
    """A file under images/third-party/ the manifest does not list, and a listed file that is not there (SC-007)."""
    files_in_pack = {path.relative_to(folder).as_posix() for path in tracked_files(folder) if path.is_file()}
    third_party_files = {file_name for file_name in files_in_pack if file_name.startswith(THIRD_PARTY_PICTURE_FOLDER)}
    faults = [f"{file_name}: a third-party picture with no entry in the manifest" for file_name in sorted(third_party_files - listed_picture_files)]
    return faults + [f"{file_name}: listed in the manifest and not in the pack" for file_name in sorted(listed_picture_files - files_in_pack)]


def entry_texts(value: object) -> list[str]:
    """Every string anywhere in a pack entry, nested checks and steps included: {"a": "x", "b": [{"c": "y"}]} gives ["x", "y"]."""
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        return [text for nested in value.values() for text in entry_texts(nested)]
    if isinstance(value, list):
        return [text for nested in value for text in entry_texts(nested)]
    return []


def override_phrases(text: str) -> list[str]:
    """The phrases in text that tell the reader to set aside a safety rule, a stop or the supervisor, unless negated just
    before: "You can skip the stop here" gives ["skip the stop"]; "Never ignore a stop" gives []."""
    found_phrases: list[str] = []
    for phrase_match in OVERRIDE_PHRASE.finditer(text):
        words_before = text[:phrase_match.start()].lower().split()[-2:]
        if not any(word.strip(".,;:!?") in NEGATION_WORDS for word in words_before):
            found_phrases.append(phrase_match.group(0))
    return found_phrases


# Invariant: HAD-04 (the safety rules are the safety module's: a pack cannot name, remove, reword or switch one off)
def safety_rule_problems(entries: list[tuple[str, dict]]) -> list[str]:
    """A passage, flow or procedure that names a safety rule by id, or tells the reader to ignore, skip, bypass, override
    or disregard a rule, a stop or the supervisor: a passage saying "SR-02 does not apply" gives
    "passage 'p': names safety rule SR-02; the rules are the safety module's, never a pack's (HAD-04)"."""
    faults: list[str] = []
    for location, entry in entries:
        entry_text = "\n".join(entry_texts(entry))
        for rule_id in dict.fromkeys(rule_id.upper() for rule_id in SAFETY_RULE_ID_IN_TEXT.findall(entry_text)):
            faults.append(f"{location}: names safety rule {rule_id}; the rules are the safety module's, never a pack's (HAD-04)")
        for phrase in dict.fromkeys(override_phrases(entry_text)):
            faults.append(f"{location}: tells the reader to set aside a safety rule, a stop or the supervisor ({phrase!r}) (HAD-04)")
    return faults


def located_entries(passages: list[dict], flows: list[dict], procedures: list[dict]) -> list[tuple[str, dict]]:
    """Each content entry with its location as the faults name it: [("passage 'voltage'", {...}), ("flow 'no-output'", {...})]."""
    kinds = (("passage", passages), ("flow", flows), ("procedure", procedures))
    return [(f"{kind} {entry.get('id')!r}", entry) for kind, kind_entries in kinds for entry in kind_entries]


def problems(folder: Path) -> list[str]:
    """Every fault in the pack folder, in a stable order; [] when it is well formed."""
    faults: list[str] = []
    manifest = load_json(folder, "manifest.json", faults)
    manifest_faults, source_kinds, listed_picture_files = manifest_problems(manifest) if manifest is not None else ([], {}, set())
    faults += manifest_faults
    if isinstance(manifest, dict) and manifest.get("id") not in (None, folder.name):
        faults.append(f"manifest.json: id {manifest.get('id')!r} is not the folder's name {folder.name!r}")
    passages, flows = load_optional_list(folder, "passages.json", faults), load_optional_list(folder, "flows.json", faults)
    procedures = load_optional_list(folder, "procedures.json", faults)
    if not (passages or flows or procedures):
        faults.append("the pack has no passage, flow or procedure")
    faults += coverage_problems(manifest, passages, source_kinds)
    faults += passage_problems(passages, source_kinds, folder) + flow_problems(flows, source_kinds, folder)
    faults += procedure_problems(procedures, source_kinds, folder)
    faults += safety_rule_problems(located_entries(passages, flows, procedures))
    faults += unknown_page_problems(manifest, passages, flows, procedures)
    return faults + id_problems(passages + flows + procedures) + unlisted_pictures(folder, listed_picture_files)


# Decision: SC-012 (the count of unknown pages is shown, so the gap in a draft pack is visible)
def unknown_page_count(folder: Path) -> int:
    """How many citations in the pack's passages, flows and procedures have the page "unknown"; 0 for a pack with none."""
    ignored_faults: list[str] = []
    contents = [load_optional_list(folder, name, ignored_faults) for name in ("passages.json", "flows.json", "procedures.json")]
    return len(unknown_pages(*contents))


def main(arguments: list[str]) -> int:
    """Print the pack's faults, then its unknown-page count; exit 1 on a fault: `packs.py packs/x` prints "ok" for a clean pack."""
    if len(arguments) != 1:
        print("usage: python3 -I scripts/checks/packs.py <pack folder>")
        return 2
    folder = Path(arguments[0])
    faults = problems(folder)
    print("\n".join(faults) if faults else "ok: the pack is well formed")
    for line in coverage_lines(folder) if not faults else []:
        print(f"covers {line}")
    unknown_count = unknown_page_count(folder)
    if unknown_count:
        print(f"{unknown_count} page(s) unknown: fill them before relying on the citations (SC-012)")
    return 1 if faults else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
