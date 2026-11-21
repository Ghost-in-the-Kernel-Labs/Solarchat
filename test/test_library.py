"""A well-formed library passes the library check and each planted break is refused (SC-014)."""
import unittest

from scripts.checks import library
from test.support import BROKEN, ROOT

GOOD = ROOT / "test" / "fixtures" / "library" / "good"
FOLDER = "good-source"


def broken(name: str) -> list[str]:
    """The faults the check finds in the planted break test/fixtures/broken/library/<name>."""
    return library.problems(BROKEN / "library" / name)


class TheFixtures(unittest.TestCase):
    def test_the_good_source_passes(self) -> None:
        self.assertEqual(library.problems(GOOD), [])

    def test_a_missing_field_is_refused(self) -> None:
        self.assertEqual(broken("missing-field"), [f"{FOLDER}: publisher is missing or empty"])

    def test_an_unknown_kind_is_refused(self) -> None:
        self.assertEqual(broken("bad-kind"), [f'{FOLDER}: kind must be "document" or "web"'])

    def test_a_document_with_no_page_count_is_refused(self) -> None:
        self.assertEqual(broken("document-no-pages"), [f"{FOLDER}: pages must be a positive whole number for a document"])

    def test_a_licence_off_the_allow_list_is_refused(self) -> None:
        self.assertEqual(len(broken("bad-licence")), 1)
        self.assertIn("licence 'All rights reserved' is not on the allow-list", broken("bad-licence")[0])

    def test_cc_by_without_an_attribution_is_refused(self) -> None:
        self.assertEqual(broken("ccby-no-attribution"), [f"{FOLDER}: a CC BY 4.0 source needs an attribution"])

    def test_a_short_hash_is_refused(self) -> None:
        self.assertEqual(broken("bad-sha"), [f"{FOLDER}: sha256 must be 64 hex characters"])

    def test_a_hash_that_does_not_match_the_original_is_refused(self) -> None:
        self.assertEqual(broken("sha-mismatch"), [f"{FOLDER}: original.html does not match sha256"])

    def test_a_missing_text_is_refused(self) -> None:
        self.assertEqual(broken("no-text"), [f"{FOLDER}: text.txt is missing"])

    def test_an_empty_text_is_refused(self) -> None:
        self.assertEqual(broken("empty-text"), [f"{FOLDER}: text.txt is empty"])

    def test_a_folder_name_that_is_not_the_id_is_refused(self) -> None:
        self.assertEqual(broken("id-mismatch"), [f"{FOLDER}: id 'other-name' is not the folder's name"])

    def test_a_folder_with_no_source_record_is_refused(self) -> None:
        self.assertEqual(broken("no-source-json"), [f"{FOLDER}: source.json is missing"])


class TheLibrary(unittest.TestCase):
    def test_the_library_in_this_repository_passes(self) -> None:
        self.assertEqual(library.problems(ROOT), [])

    def test_the_library_holds_the_sources_ghost_asked_for(self) -> None:
        names = set(library.source_files(ROOT))
        self.assertLessEqual({"osha-1910-s", "osha-1926-k", "osha-1926-m", "osha-1926-cranes-power-lines", "niosh-2009-113", "solar-vic-pv-audit"}, names)

    def test_a_folder_with_no_library_has_no_faults(self) -> None:
        self.assertEqual(library.problems(ROOT / "test" / "fixtures" / "packs"), [])
