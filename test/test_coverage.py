"""A pack's declarations of coverage are checked: six refusals, each planted (TODO 1.26; SC-024, SC-016, HAD-04)."""
import json
import shutil
import unittest
from collections.abc import Callable
from pathlib import Path

from scripts.checks import coverage, packs
from test.support import BROKEN, ROOT, scratch

GOOD = ROOT / "test" / "fixtures" / "packs" / "good"


def edit(folder: Path, name: str, change: Callable[[object], object]) -> None:
    """Load folder/name.json, let `change` alter it in place, and write it back."""
    path = folder / f"{name}.json"
    data = json.loads(path.read_text())
    change(data)
    path.write_text(json.dumps(data))


COVERED = ROOT / "test" / "fixtures" / "packs" / "covered"


class TheCoverage(unittest.TestCase):
    """SC-024: a make-and-model pack may declare that its own passages cover a general rule; six refusals, each planted."""

    def test_the_covered_pack_passes_and_lists_each_declaration_with_its_sources(self) -> None:
        self.assertEqual(packs.problems(COVERED), [])
        self.assertEqual(coverage.coverage_lines(COVERED), [
            "SR-02 warn: passage 'live-panel' (Examplesun ES-100 installation manual, page 3, 4)",
            "SR-08 emergency: passage 'heat-smoke' (Examplesun ES-100 installation manual, page 5-6)"])

    def test_the_good_pack_declares_nothing(self) -> None:
        self.assertEqual(coverage.coverage_lines(GOOD), [])

    def test_a_rule_that_is_not_a_general_rule_is_refused(self) -> None:
        self.assertEqual(packs.problems(BROKEN / "packs" / "coverage-unknown-rule"),
                         ["manifest.json safety_coverage 'SR-99': not the id of a general safety rule"])

    def test_a_rule_declared_twice_is_refused(self) -> None:
        folder = scratch() / "covered"
        shutil.copytree(COVERED, folder)
        edit(folder, "manifest", lambda m: m["safety_coverage"].append(dict(m["safety_coverage"][0])))
        self.assertEqual(packs.problems(folder), ["manifest.json safety_coverage 'SR-02': a rule is declared once"])

    def test_a_passage_that_is_not_the_packs_or_an_empty_list_is_refused(self) -> None:
        self.assertEqual(packs.problems(BROKEN / "packs" / "coverage-foreign-passage"),
                         ["manifest.json safety_coverage 'SR-02': passage 'elsewhere' is not a passage of this pack"])
        folder = scratch() / "covered"
        shutil.copytree(COVERED, folder)
        edit(folder, "manifest", lambda m: m["safety_coverage"][0].update(passages=[]))
        self.assertEqual(packs.problems(folder), ["manifest.json safety_coverage 'SR-02': passages must name at least one passage of this pack"])

    def test_a_covering_passage_with_no_numbered_document_page_is_refused(self) -> None:
        self.assertEqual(packs.problems(BROKEN / "packs" / "coverage-no-page"),
                         ["manifest.json safety_coverage 'SR-02': passage 'unpaged' cites no document source with a page that is a number"])

    def test_an_unknown_page_never_covers_in_a_demo_pack(self) -> None:
        folder = scratch() / "covered"
        shutil.copytree(COVERED, folder)
        edit(folder, "passages", lambda p: p[2].update(sources=[{"source": "S1", "page": "unknown"}]))
        self.assertEqual(packs.problems(folder), ["manifest.json safety_coverage 'SR-02': passage 'live-panel' cites no document source with a page that is a number"])

    def test_a_page_that_is_not_a_number_is_refused_and_numbers_pass(self) -> None:
        passage = {"sources": [{"source": "S1", "page": "A-3"}]}
        self.assertFalse(coverage.covers_with_a_page(passage, {"S1": "document"}))
        for page in ("3", "3, 14", "5-6", "3, 5-6"):
            with self.subTest(page=page):
                self.assertTrue(coverage.covers_with_a_page({"sources": [{"source": "S1", "page": page}]}, {"S1": "document"}))

    def test_coverage_in_an_installation_type_pack_is_refused(self) -> None:
        self.assertEqual(packs.problems(BROKEN / "packs" / "coverage-type-pack"),
                         ["manifest.json: safety_coverage needs make and model; an installation_type pack cannot declare coverage (SC-024)"])

    def test_a_response_out_of_place_is_refused(self) -> None:
        self.assertEqual(packs.problems(BROKEN / "packs" / "coverage-wrong-response"),
                         ["manifest.json safety_coverage 'SR-08': response must be 'emergency'"])
        folder = scratch() / "covered"
        shutil.copytree(COVERED, folder)
        edit(folder, "manifest", lambda m: m["safety_coverage"][0].update(response="emergency"))
        self.assertEqual(packs.problems(folder), ["manifest.json safety_coverage 'SR-02': response must be 'warn' or 'stop'"])

    def test_a_demo_declaration_must_be_signed_by_the_maintainer(self) -> None:
        self.assertEqual(packs.problems(BROKEN / "packs" / "coverage-demo-unsigned"),
                         ["manifest.json safety_coverage 'SR-02': declared needs by, role, date, evidence, each with something in it (SC-016)"])
        folder = scratch() / "covered"
        shutil.copytree(COVERED, folder)
        edit(folder, "manifest", lambda m: m["safety_coverage"][0]["declared"].update(role="engineer"))
        self.assertEqual(packs.problems(folder), ["manifest.json safety_coverage 'SR-02': a demo pack's declaration is made by the maintainer: role must be 'maintainer' (SC-024)"])

    def test_a_field_pack_needs_no_declared_but_a_given_one_must_be_whole(self) -> None:
        folder = scratch() / "covered"
        shutil.copytree(COVERED, folder)
        edit(folder, "manifest", lambda m: (m.update(status="field"), [d.pop("declared") for d in m["safety_coverage"]]))
        self.assertEqual(packs.problems(folder), [])
        edit(folder, "manifest", lambda m: m["safety_coverage"][0].update(declared={"by": "Ghost"}))
        self.assertEqual(len(packs.problems(folder)), 1)
