"""One piece of equipment a pack's manuals describe (SC-027), moved out of contract.py to keep that file under 400 lines.

`solarchat.leaf.contract` still names `Equipment` and its two constants, so every import of them is unchanged. Standard library only (HAD-01).
"""
import re
from dataclasses import dataclass

EQUIPMENT_KINDS = ("panel", "controller", "power-station", "battery", "inverter", "connector")
EQUIPMENT_ID_PATTERN = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


@dataclass(frozen=True)
class Equipment:
    """One piece of equipment a pack's manuals describe, refused at construction when incomplete.

    Decision: SC-027 (the packs name what they cover; `sources` are the pack's own source ids; no safety coverage is declared).
    Equipment("victron-smartsolar-mppt", "controller", "Victron Energy", "SmartSolar MPPT 75/10", ("S4",)) stands; an id with a
    capital, a kind outside EQUIPMENT_KINDS, a blank make or model, or no sources raises ValueError.
    """

    id: str
    kind: str
    make: str
    model: str
    sources: tuple[str, ...]

    def __post_init__(self) -> None:
        """Raise ValueError when the record breaks SC-027 (the examples are in the class docstring)."""
        if not (isinstance(self.id, str) and EQUIPMENT_ID_PATTERN.match(self.id)) or self.kind not in EQUIPMENT_KINDS or not self.sources \
                or any(not isinstance(word, str) or not word.strip() for word in (self.make, self.model, *self.sources)):
            raise ValueError(f"equipment {self.id!r}: an id of lowercase words, one of {', '.join(EQUIPMENT_KINDS)}, a make, a model and sources (SC-027)")
