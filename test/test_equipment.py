"""A pack's equipment list: the leaf record, the loader, the pack check's five refusals, and the seed pack's list (TODO 2.14; SC-027)."""
import json
import unittest

from scripts.checks import packs
from solarchat.leaf.contract import Equipment
from solarchat.packs.load import equipment_from_manifest, load_pack
from test.support import BROKEN, ROOT

FIXTURES = ROOT / "test" / "fixtures" / "packs"
SEED = ROOT / "packs" / "seed-mc4-leads"
VICTRON = ("victron-smartsolar-mppt", "controller", "Victron Energy", "SmartSolar MPPT 75/10 to 100/20", ("S4", "S5", "S10"))


class TheLeafRecord(unittest.TestCase):
    def test_a_whole_entry_stands(self) -> None:
        self.assertEqual(Equipment(*VICTRON).sources, ("S4", "S5", "S10"))

    def test_a_bad_id_kind_make_model_or_no_sources_raises(self) -> None:
        for change in ({"id": "Victron 75"}, {"id": ""}, {"kind": "toaster"}, {"make": " "}, {"model": ""}, {"sources": ()}, {"sources": ("",)}):
            fields = dict(zip(("id", "kind", "make", "model", "sources"), VICTRON)) | change
            with self.subTest(change), self.assertRaises(ValueError):
                Equipment(**fields)


class TheLoader(unittest.TestCase):
    def test_a_pack_with_no_list_has_no_equipment(self) -> None:
        self.assertEqual(load_pack(FIXTURES / "good").equipment, ())
        self.assertEqual(equipment_from_manifest({"equipment": []}), ())

    def test_the_list_loads_as_leaf_records_in_order(self) -> None:
        self.assertEqual([each.id for each in load_pack(FIXTURES / "equipped").equipment], ["examplesun-es-100", "any-mc4-connector"])
        self.assertEqual(load_pack(FIXTURES / "equipped").equipment[1].make, "any")

    def test_a_malformed_list_or_entry_raises_value_error(self) -> None:
        for bad in ("x", ["x"], [{"id": "a", "sources": "S1"}], [{"id": "A", "kind": "panel", "make": "m", "model": "m", "sources": ["S1"]}]):
            with self.subTest(bad), self.assertRaises(ValueError):
                equipment_from_manifest({"equipment": bad})


class TheCheck(unittest.TestCase):
    def test_a_good_list_passes(self) -> None:
        self.assertEqual(packs.problems(FIXTURES / "equipped"), [])

    def broken(self, name: str) -> list[str]:
        """The pack check's lines for a planted pack: broken("equipment-bad-kind") gives the one line about its kind."""
        return packs.problems(BROKEN / "packs" / name)

    def test_a_bad_kind_is_refused(self) -> None:
        self.assertEqual(self.broken("equipment-bad-kind"), ["manifest.json equipment 'examplesun-es-100': kind must be one of panel, "
                                                             "controller, power-station, battery, inverter, connector"])

    def test_a_malformed_id_is_refused(self) -> None:
        self.assertEqual(self.broken("equipment-bad-id"), ["manifest.json equipment 'Examplesun ES-100': id must be lowercase words joined by hyphens"])

    def test_a_repeated_id_is_refused(self) -> None:
        self.assertEqual(self.broken("equipment-duplicate-id"), ["manifest.json equipment 'examplesun-es-100': the id is used twice"])

    def test_no_sources_is_refused(self) -> None:
        self.assertEqual(self.broken("equipment-no-sources"),
                         ["manifest.json equipment 'examplesun-es-100': sources must name at least one source of this pack"])

    def test_a_source_the_pack_lacks_is_refused(self) -> None:
        self.assertEqual(self.broken("equipment-unknown-source"), ["manifest.json equipment 'examplesun-es-100': source 'S9' is not in the manifest"])


class TheSeedPacksList(unittest.TestCase):
    def test_four_entries_each_traced_to_sources_the_pack_has(self) -> None:
        pack = load_pack(SEED)
        self.assertEqual([each.id for each in pack.equipment], ["victron-smartsolar-mppt", "ecoflow-r600", "mc4-connector", "crystalline-panel-mc4"])
        self.assertEqual(pack.equipment[0], Equipment(*VICTRON))
        have = {source["id"] for source in pack.manifest["sources"]}
        self.assertTrue(all(set(each.sources) <= have for each in pack.equipment))

    def test_each_entry_rests_on_a_source_whose_publisher_or_title_names_it(self) -> None:
        sources = {source["id"]: source for source in json.loads((SEED / "manifest.json").read_text())["sources"]}
        names = {"victron-smartsolar-mppt": "Victron", "ecoflow-r600": "R600", "mc4-connector": "connector", "crystalline-panel-mc4": "crystalline"}
        for each in load_pack(SEED).equipment:
            for source_id in each.sources:
                text = sources[source_id]["publisher"] + " " + sources[source_id]["title"]
                self.assertIn(names[each.id].lower(), text.lower(), (each.id, source_id))

    def test_the_seed_pack_still_passes_the_check(self) -> None:
        self.assertEqual(packs.problems(SEED), [])
