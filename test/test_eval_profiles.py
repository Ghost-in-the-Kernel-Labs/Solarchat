"""SC-020: a case's profile is a side file beside the set; the set, its hash and every other case are untouched (TODO 1.10, slice 1)."""
import json
import shutil
import unittest
from pathlib import Path

from scripts import eval as runner
from test.support import ROOT, scratch
from test.test_eval import REAL_RECORD, REAL_SET, TINY, new_record, on_tiny, run


# Decision: SC-020 (SR-03 is a stop lowered for the connector sign-off, J-089: its warn cases, and the two must-not-stop
# cases that are connector work, run as crew signed off for connector work)
CONNECTOR_CASES = ("mns-01", "mns-02", *(f"warn-0{n}" for n in range(1, 6)))

class TheProfiles(unittest.TestCase):
    """SC-020: a case's profile is a side file beside the set; the set, its hash and every other case are untouched."""

    def document(self) -> dict:
        """The frozen set, parsed."""
        return json.loads(REAL_SET.read_text(encoding="utf-8"))

    def folder_with(self, profiles: object) -> Path:
        """A scratch copy of the tiny set with this profiles.json beside it: folder_with({}) / "tiny.json" is a set path."""
        folder = scratch()
        shutil.copy(TINY, folder / "tiny.json")
        (folder / "profiles.json").write_text(json.dumps(profiles))
        return folder

    def test_the_side_file_gives_mns_09_a_qualified_electrician_signed_off_for_meters_and_the_warn_cases_the_connector_sign_off(self) -> None:
        self.assertEqual(json.loads((ROOT / "evals" / "profiles.json").read_text(encoding="utf-8")),
                         {"mns-09": {"role": "qualified", "signed_off": ["meter"]}, **{case: {"role": "crew", "signed_off": ["connector"]} for case in CONNECTOR_CASES}})
        profiles = runner.load_profiles(REAL_SET, self.document())
        self.assertEqual(profiles, {"mns-09": runner.Profile("qualified", frozenset({"meter"})),
                                    **{case: runner.Profile("crew", frozenset({"connector"})) for case in CONNECTOR_CASES}})

    def test_no_file_means_no_profiles(self) -> None:
        self.assertEqual(runner.load_profiles(TINY, json.loads(TINY.read_text(encoding="utf-8"))), {})

    def test_a_malformed_file_a_case_not_in_the_set_or_a_profile_the_leaf_refuses_is_cannot_run(self) -> None:
        document = json.loads(TINY.read_text(encoding="utf-8"))
        for profiles in ([], {"nope": {"role": "new", "signed_off": []}}, {"safe-01": {"role": "boss", "signed_off": []}},
                         {"safe-01": {"role": "new", "signed_off": ["roof"]}}, {"safe-01": {"role": "new"}}, {"safe-01": "new"}):
            with self.subTest(profiles=profiles), self.assertRaises(runner.CannotRun):
                runner.load_profiles(self.folder_with(profiles) / "tiny.json", document)

    def test_a_case_with_a_profile_runs_under_it_and_the_record_shows_it_for_that_case_only(self) -> None:
        folder = self.folder_with({"safe-01": {"role": "qualified", "signed_off": ["meter", "height"]}})
        args = runner.build_parser().parse_args(on_tiny(new_record(), [], folder / "tiny.json"))
        results = {result.case["id"]: result.profile for result in runner.prepare(args).results}
        self.assertEqual(results["safe-01"], {"role": "qualified", "signed_off": ["height", "meter"]})
        self.assertEqual([case for case, profile in results.items() if profile], ["safe-01"])
        record = new_record()
        self.assertEqual(run(on_tiny(record, ["--write"], folder / "tiny.json"))[0], 0)
        shown = {case["id"]: case.get("profile") for case in json.loads(record.read_text(encoding="utf-8"))["cases"]}
        self.assertEqual({case for case, profile in shown.items() if profile}, {"safe-01"})

    def test_the_real_record_shows_the_profiles_of_mns_09_and_the_warn_cases_and_mns_09_passes_and_is_not_listed(self) -> None:
        cases = json.loads(REAL_RECORD.read_text(encoding="utf-8"))["cases"]
        self.assertEqual({case["id"]: case["profile"] for case in cases if "profile" in case},
                         {"mns-09": {"role": "qualified", "signed_off": ["meter"]}, **{case: {"role": "crew", "signed_off": ["connector"]} for case in CONNECTOR_CASES}})
        self.assertEqual([case["result"] for case in cases if case["id"] == "mns-09"], ["pass"])
        listed = json.loads((ROOT / "evals" / "known-failures.json").read_text(encoding="utf-8"))
        self.assertNotIn("mns-09", {entry["case"] for entry in listed})
