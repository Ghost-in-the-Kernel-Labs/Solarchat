"""A manifest's `equipment` list is well formed, as docs/CONTRACT.md's "The equipment list" states it (SC-027).

`scripts/checks/packs.py` calls `equipment_problems` with the manifest and the sources' kinds by id. Standard library only.
"""
import re

ID_PATTERN = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
EQUIPMENT_KINDS = ("panel", "controller", "power-station", "battery", "inverter", "connector")


def blank(value: object) -> bool:
    """True unless value is a string with something in it: blank(" ") and blank(None) give True, blank("a") False."""
    return not isinstance(value, str) or not value.strip()


def entry_problems(entry: dict, location: str, source_ids: set[str]) -> list[str]:
    """The lines for one entry: its id's shape, its kind, its make and model, and its sources, each one of the pack's own:
    an entry with "sources": ["S9"] in a pack with no S9 gives "<location>: source 'S9' is not in the manifest"."""
    faults = [f"{location}: {name} is missing or empty" for name in ("make", "model") if blank(entry.get(name))]
    if entry.get("kind") not in EQUIPMENT_KINDS:
        faults.append(f"{location}: kind must be one of {', '.join(EQUIPMENT_KINDS)}")
    named = entry.get("sources")
    if not isinstance(named, list) or not named:
        return faults + [f"{location}: sources must name at least one source of this pack"]
    return faults + [f"{location}: source {name!r} is not in the manifest" for name in named if not isinstance(name, str) or name not in source_ids]


# Decision: SC-027 (the packs' own lists say what the bot covers: each entry traces to the pack's sources, and ids are unique)
def equipment_problems(manifest: object, source_kinds: dict[str, object]) -> list[str]:
    """The lines for the manifest's `equipment` (absent or empty: none): a bad kind, a malformed or repeated id, an empty
    `sources`, a source the pack does not have; a repeated id gives "manifest.json equipment 'r600': the id is used twice"."""
    if not isinstance(manifest, dict) or manifest.get("equipment") in (None, []):
        return []
    entries = manifest["equipment"]
    if not isinstance(entries, list) or not all(isinstance(entry, dict) for entry in entries):
        return ["manifest.json: equipment must be a list of objects"]
    ids = [entry.get("id") for entry in entries]
    faults: list[str] = []
    for number, entry in enumerate(entries):
        location = f"manifest.json equipment {entry.get('id')!r}"
        if blank(entry.get("id")) or not ID_PATTERN.match(entry["id"]):
            faults.append(f"{location}: id must be lowercase words joined by hyphens")
        elif ids.count(entry["id"]) > 1 and ids.index(entry["id"]) != number:
            faults.append(f"{location}: the id is used twice")
        faults += entry_problems(entry, location, set(source_kinds))
    return faults
