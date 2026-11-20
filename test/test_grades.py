"""The grade map names every grade and a floor (C-036); a model's name elsewhere is not refused here (SC-006)."""
import unittest

from scripts.checks import grades
from test.support import ROOT


class TheRepository(unittest.TestCase):
    def test_the_map_names_every_grade_and_a_floor(self) -> None:
        text = (ROOT / grades.MAP).read_text()
        for row in ("| small | Claude Haiku |", "| mid | Claude Sonnet |", "| strong | Claude Opus |", "| ruling | Claude Fable |"):
            self.assertIn(row, text)
        self.assertRegex(text, r"(?m)^Floor: (small|mid|strong)$")
