"""The safety module: the project's own fixed safety rules, held outside every pack (TODO 1.3).

Invariant: HAD-04 (the safety rules are this module's text, never a pack's; no pack can remove or change one).
`rules.json` is the rules' one source of truth; `rules.py` reads it. `docs/SAFETY-RULES.md` is written from it.
"""
