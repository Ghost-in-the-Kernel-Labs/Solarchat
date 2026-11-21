"""A pack loads from its folder with each passage's title, and its citations are worded with the page (TODO 1.6; SC-012, SC-019)."""
import json
import shutil
import unittest
from pathlib import Path

from solarchat.leaf.contract import PassageRef
from solarchat.packs.load import Pack, citation_lines, load_pack
from test.support import ROOT, scratch

GOOD = ROOT / "test" / "fixtures" / "packs" / "good"
SEED = ROOT / "packs" / "seed-mc4-leads"


def copy_of_good() -> Path:
    """A scratch copy of the good fixture pack that a test may break: copy_of_good() / "manifest.json" exists."""
    folder = scratch() / "pack"
    shutil.copytree(GOOD, folder)
    return folder


class TheGoodPack(unittest.TestCase):
    def test_it_loads_with_its_id_manifest_and_passages_in_order(self) -> None:
        pack = load_pack(GOOD)
        self.assertIsInstance(pack, Pack)
        self.assertEqual(pack.pack_id, "good")
        self.assertEqual(pack.manifest["status"], "field")
        self.assertEqual([passage.ref.passage_id for passage in pack.passages], ["voltage", "label"])
        self.assertEqual(pack.passages[0].ref, PassageRef("good", "voltage"))
        self.assertEqual(pack.passages[0].title, "Check the voltages match")

    def test_its_citations_are_the_sources_as_written(self) -> None:
        self.assertEqual(load_pack(GOOD).citations["label"], [{"source": "S1", "page": "1"}, "S2"])

    def test_a_document_source_is_worded_with_its_page_and_a_web_source_by_its_title(self) -> None:
        pack = load_pack(GOOD)
        self.assertEqual(citation_lines(pack, "voltage"), ("Examplesun ES-100 installation manual, page 1",))
        self.assertEqual(citation_lines(pack, "label"), ("Examplesun ES-100 installation manual, page 1",
                                                         "Reading a panel's label (web page)"))

    def test_an_unknown_passage_or_source_is_refused(self) -> None:
        pack = load_pack(GOOD)
        with self.assertRaisesRegex(ValueError, "no passage 'nope'"):
            citation_lines(pack, "nope")
        broken = Pack(pack.pack_id, pack.manifest, pack.passages, {"voltage": ["S9"]})
        with self.assertRaisesRegex(ValueError, "S9"):
            citation_lines(broken, "voltage")


class TheSeedPack(unittest.TestCase):
    def test_it_has_85_passages_with_titles(self) -> None:
        pack = load_pack(SEED)
        self.assertEqual(len(pack.passages), 85)
        self.assertEqual(pack.pack_id, "seed-mc4-leads")
        self.assertTrue(all(passage.title for passage in pack.passages))

    def test_a_document_citation_carries_its_page_and_an_unknown_page_says_so(self) -> None:
        lines = citation_lines(load_pack(SEED), "step-01")
        self.assertEqual(lines[2], "EcoFlow R600 user manual, page 15: solar panel connection, page 15")
        self.assertTrue(lines[0].endswith("2017, page not yet found"))

    def test_a_web_source_has_no_page(self) -> None:
        lines = citation_lines(load_pack(SEED), "step-03")
        self.assertEqual(lines[:2], ("Solar PV audit checklist (print all)", "MC4 connector"))


class TheLoaderRefusals(unittest.TestCase):
    def test_a_missing_manifest_names_the_file(self) -> None:
        folder = copy_of_good()
        (folder / "manifest.json").unlink()
        with self.assertRaisesRegex(ValueError, "manifest.json: the file is missing"):
            load_pack(folder)

    def test_a_missing_manifest_field_names_it(self) -> None:
        folder = copy_of_good()
        manifest = json.loads((folder / "manifest.json").read_text())
        del manifest["status"]
        (folder / "manifest.json").write_text(json.dumps(manifest))
        with self.assertRaisesRegex(ValueError, "manifest.json: no 'status'"):
            load_pack(folder)

    def test_a_missing_passage_field_names_the_passage(self) -> None:
        folder = copy_of_good()
        passages = json.loads((folder / "passages.json").read_text())
        del passages[1]["title"]
        (folder / "passages.json").write_text(json.dumps(passages))
        with self.assertRaisesRegex(ValueError, "passages.json: passage 2 has no 'title'"):
            load_pack(folder)

    def test_no_passages_file_means_no_passages(self) -> None:
        folder = copy_of_good()
        (folder / "passages.json").unlink()
        self.assertEqual(load_pack(folder).passages, ())

    def test_a_manifest_that_is_not_json_is_refused(self) -> None:
        folder = copy_of_good()
        (folder / "manifest.json").write_text("{not json")
        with self.assertRaisesRegex(ValueError, "not valid JSON"):
            load_pack(folder)


if __name__ == "__main__":
    unittest.main()
