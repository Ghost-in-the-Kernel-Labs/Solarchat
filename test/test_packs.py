"""A well-formed pack passes the pack check and each planted break is refused (TODO 1.2; SC-005, SC-007, HAD-06)."""
import json
import shutil
import unittest
from collections.abc import Callable
from pathlib import Path

from scripts.checks import packs
from test.support import BROKEN, ROOT, scratch

GOOD = ROOT / "test" / "fixtures" / "packs" / "good"


def copy_good(name: str = "good") -> Path:
    """A scratch copy of the good pack in a folder of the name given: copy_good("x") gives /tmp/ghost-core-abc/x."""
    folder = scratch() / name
    shutil.copytree(GOOD, folder)
    return folder


def edit(folder: Path, name: str, change: Callable[[object], object]) -> None:
    """Load folder/name.json, let `change` alter it in place, and write it back."""
    path = folder / f"{name}.json"
    data = json.loads(path.read_text())
    change(data)
    path.write_text(json.dumps(data))


class TheFixtures(unittest.TestCase):
    def test_the_good_pack_passes(self) -> None:
        self.assertEqual(packs.problems(GOOD), [])

    def test_a_missing_licence_is_refused(self) -> None:
        self.assertEqual(packs.problems(BROKEN / "packs" / "no-licence"), ["manifest.json source 'S1': licence is missing or empty"])

    def test_a_flow_with_no_end_is_refused(self) -> None:
        self.assertEqual(packs.problems(BROKEN / "packs" / "flow-no-stop"), ["flow 'no-output': stop is missing or empty"])

    def test_a_passage_with_no_source_is_refused(self) -> None:
        self.assertEqual(packs.problems(BROKEN / "packs" / "passage-no-source"), ["passage 'voltage': sources must name at least one source"])

    def test_an_admission_with_no_date_is_refused(self) -> None:
        self.assertEqual(packs.problems(BROKEN / "packs" / "half-admitted"), ["manifest.json: admitted_on is missing or empty"])

    def test_a_procedure_with_no_steps_is_refused(self) -> None:
        self.assertEqual(packs.problems(BROKEN / "packs" / "procedure-no-steps"), ["procedure 'connect': steps must be a non-empty list"])

    def test_a_manifest_with_no_make_model_or_type_is_refused(self) -> None:
        self.assertEqual(packs.problems(BROKEN / "packs" / "no-identity"), ["manifest.json: needs make and model, or installation_type"])

    def test_a_make_without_a_model_is_refused(self) -> None:
        self.assertEqual(packs.problems(BROKEN / "packs" / "make-without-model"), ["manifest.json: make and model go together"])

    def test_a_third_party_picture_with_no_entry_is_refused(self) -> None:
        self.assertEqual(packs.problems(BROKEN / "packs" / "picture-no-provenance"),
                         ["images/third-party/label.svg: a third-party picture with no entry in the manifest"])

    def test_a_source_the_manifest_lacks_is_refused(self) -> None:
        self.assertEqual(packs.problems(BROKEN / "packs" / "unknown-source"), ["passage 'voltage': source 'S9' is not in the manifest"])

    def test_a_picture_with_no_alt_text_is_refused(self) -> None:
        self.assertEqual(packs.problems(BROKEN / "packs" / "picture-no-alt"), ["passage 'voltage': image_alt is missing or empty"])


class TheCheck(unittest.TestCase):
    def test_a_pack_not_admitted_passes(self) -> None:
        folder = copy_good()
        edit(folder, "manifest", lambda m: m.update(admitted_by=None, admitted_on=None))
        self.assertEqual(packs.problems(folder), [])

    def test_an_admission_date_must_be_a_date(self) -> None:
        folder = copy_good()
        edit(folder, "manifest", lambda m: m.update(admitted_on="last Tuesday"))
        self.assertEqual(packs.problems(folder), ["manifest.json: admitted_on is not a date as YYYY-MM-DD"])

    def test_each_of_the_three_content_files_may_be_absent(self) -> None:
        folder = copy_good()
        (folder / "flows.json").unlink()
        (folder / "procedures.json").unlink()
        self.assertEqual(packs.problems(folder), [])

    def test_a_pack_with_nothing_in_it_is_refused(self) -> None:
        folder = copy_good()
        for name in ("passages", "flows"):
            edit(folder, name, lambda items: items.clear())
        (folder / "procedures.json").unlink()
        self.assertEqual(packs.problems(folder), ["the pack has no passage, flow or procedure"])

    def test_a_pack_of_one_procedure_passes(self) -> None:
        folder = copy_good()
        (folder / "passages.json").unlink()
        (folder / "flows.json").unlink()
        self.assertEqual(packs.problems(folder), [])

    def test_a_missing_manifest_is_one_line_among_others(self) -> None:
        folder = copy_good()
        (folder / "manifest.json").unlink()
        self.assertEqual(packs.problems(folder)[0], "manifest.json: the file is missing")

    def test_a_file_that_is_not_json_is_one_line(self) -> None:
        folder = copy_good()
        (folder / "passages.json").write_text("{not json")
        self.assertEqual(len(packs.problems(folder)), 1)
        self.assertIn("passages.json: not valid JSON", packs.problems(folder)[0])

    def test_a_flow_with_no_checks_is_refused(self) -> None:
        folder = copy_good()
        edit(folder, "flows", lambda f: f[0].update(checks=[]))
        self.assertEqual(packs.problems(folder), ["flow 'no-output': checks must be a non-empty list"])

    def test_an_id_used_twice_is_refused(self) -> None:
        folder = copy_good()
        edit(folder, "flows", lambda f: f[0].update(id="voltage"))
        self.assertEqual(packs.problems(folder), ["id 'voltage' is used twice among the passages, flows and procedures"])

    def test_the_folder_must_be_named_for_the_pack(self) -> None:
        self.assertEqual(packs.problems(copy_good("other")), ["manifest.json: id 'good' is not the folder's name 'other'"])

    def test_a_picture_outside_images_is_refused(self) -> None:
        folder = copy_good()
        edit(folder, "passages", lambda p: p[0].update(image="../manifest.json"))
        self.assertEqual(packs.problems(folder), ["passage 'voltage': image must be a path under images/"])

    def test_a_picture_that_is_not_there_is_refused(self) -> None:
        folder = copy_good()
        edit(folder, "passages", lambda p: p[0].update(image="images/gone.svg"))
        self.assertEqual(packs.problems(folder), ["passage 'voltage': image 'images/gone.svg' is not in the pack"])

    def test_a_listed_picture_that_is_not_there_is_refused(self) -> None:
        folder = copy_good()
        (folder / "images" / "third-party" / "label.svg").unlink()
        self.assertEqual(packs.problems(folder), [
            "passage 'label': image 'images/third-party/label.svg' is not in the pack",
            "images/third-party/label.svg: listed in the manifest and not in the pack"])

    def test_a_picture_entry_must_say_who_owns_it(self) -> None:
        folder = copy_good()
        edit(folder, "manifest", lambda m: m["third_party_images"][0].pop("owner"))
        self.assertEqual(packs.problems(folder), ["manifest.json third-party picture 'images/third-party/label.svg': owner is missing or empty"])

    def test_a_pack_with_no_sources_is_refused(self) -> None:
        folder = copy_good()
        edit(folder, "manifest", lambda m: m.update(sources=[]))
        found = packs.problems(folder)
        self.assertIn("manifest.json: sources: must be a non-empty list", found)

    def test_an_installation_type_alone_passes(self) -> None:
        folder = copy_good()
        edit(folder, "manifest", lambda m: (m.pop("make"), m.pop("model")))
        self.assertEqual(packs.problems(folder), [])

    def test_make_and_model_alone_pass(self) -> None:
        folder = copy_good()
        edit(folder, "manifest", lambda m: m.pop("installation_type"))
        self.assertEqual(packs.problems(folder), [])

    def test_an_empty_installation_type_is_refused(self) -> None:
        folder = copy_good()
        edit(folder, "manifest", lambda m: m.update(installation_type=" "))
        self.assertEqual(packs.problems(folder), ["manifest.json: installation_type is empty"])

    def test_a_step_needs_text_and_what_right_looks_like(self) -> None:
        folder = copy_good()
        edit(folder, "procedures", lambda p: p[0]["steps"][1].pop("right_looks_like"))
        self.assertEqual(packs.problems(folder), ["procedure 'connect' step plug: right_looks_like is missing or empty"])

    def test_a_step_id_used_twice_is_refused(self) -> None:
        folder = copy_good()
        edit(folder, "procedures", lambda p: p[0]["steps"][1].update(id="look"))
        self.assertEqual(packs.problems(folder), ["procedure 'connect': step id 'look' is used twice"])

    def test_a_step_stop_that_is_empty_is_refused(self) -> None:
        folder = copy_good()
        edit(folder, "procedures", lambda p: p[0]["steps"][0].update(stop=""))
        self.assertEqual(packs.problems(folder), ["procedure 'connect' step look: stop is missing or empty"])

    def test_a_step_picture_needs_alt_text(self) -> None:
        folder = copy_good()
        edit(folder, "procedures", lambda p: p[0]["steps"][0].pop("image_alt"))
        self.assertEqual(packs.problems(folder), ["procedure 'connect' step look: image_alt is missing or empty"])

    def test_a_procedure_id_shares_the_namespace(self) -> None:
        folder = copy_good()
        edit(folder, "procedures", lambda p: p[0].update(id="voltage"))
        self.assertEqual(packs.problems(folder), ["id 'voltage' is used twice among the passages, flows and procedures"])

    def test_a_procedure_needs_a_source(self) -> None:
        folder = copy_good()
        edit(folder, "procedures", lambda p: p[0].update(sources=[]))
        self.assertEqual(packs.problems(folder), ["procedure 'connect': sources must name at least one source"])
