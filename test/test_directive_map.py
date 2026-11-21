"""docs/DIRECTIVE-MAP.md is current, and the map finds a citation above a function and in its docstring (SC-011)."""
import ast
import unittest

from scripts import directive_map
from test.support import ROOT

PLANTED_SOURCE = '''
# Decision: SC-005, SC-007 (a planted citation above a function)
def admits_a_pack() -> None:
    """A function cited from above."""


def walks_a_flow() -> None:
    """A function cited in its docstring.

    Invariant: HAD-04 (a planted citation in a docstring).
    """


def holds_nothing() -> None:
    """A function that cites no directive; SC-009 named in prose is not a citation."""
'''


class TheRepository(unittest.TestCase):
    def test_the_map_is_current(self) -> None:
        self.assertEqual(directive_map.main(["--check"]), 0, "run: python3 -I scripts/directive_map.py")

    def test_every_cited_id_is_a_directive(self) -> None:
        self.assertNotIn("Cited in code but not a directive", (ROOT / "docs" / "DIRECTIVE-MAP.md").read_text())


class TheCitations(unittest.TestCase):
    def test_a_comment_and_a_docstring_citation_are_found_and_prose_is_not(self) -> None:
        holders = directive_map.holders_in_file("x.py", PLANTED_SOURCE)
        self.assertEqual(holders, {"SC-005": ["`x.py:admits_a_pack`"], "SC-007": ["`x.py:admits_a_pack`"],
                                   "HAD-04": ["`x.py:walks_a_flow`"]})

    def test_a_module_docstring_and_a_shell_decision_line_name_the_file(self) -> None:
        self.assertEqual(directive_map.module_holders("m.py", '"""A module.\n\nInvariant: HAD-01 (why)."""\n'), {"HAD-01": ["`m.py`"]})
        self.assertEqual(directive_map.module_holders("s.sh", "X=1  # Decision: SC-009 (why)\n# SC-001 in prose\n"), {"SC-009": ["`s.sh`"]})

    def test_ids_are_read_before_the_reason_only(self) -> None:
        self.assertEqual(directive_map.cited_ids("C-008, C-012 (unlike C-024)"), ["C-008", "C-012"])

    def test_a_docstring_line_must_start_with_the_label(self) -> None:
        function_node = ast.parse('def f() -> None:\n    """Not a citation: Invariant: HAD-01."""\n').body[0]
        self.assertEqual(directive_map.docstring_citations(function_node), [])
