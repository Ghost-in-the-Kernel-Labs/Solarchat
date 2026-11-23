"""The evaluation set passes its check, and each planted break of each rule is refused (TODO 1.5; SC-018, SC-015, HAD-03, HAD-04)."""
import hashlib
import json
import unittest
from collections.abc import Callable
from pathlib import Path

from scripts.checks import evals
from solarchat.safety.rules import rules_fired
from test.support import ROOT, scratch

GOOD = ROOT / "test" / "fixtures" / "evals" / "good.json"
REAL_SET = ROOT / "evals" / "v1.json"


def planted(change: Callable[[dict], object]) -> Path:
    """A scratch copy of the good set after `change` altered it in place: planted(lambda d: d.update(version=2))."""
    document = json.loads(GOOD.read_text(encoding="utf-8"))
    change(document)
    path = scratch() / "v1.json"
    path.write_text(json.dumps(document), encoding="utf-8")
    return path


def case_of(document: dict, case_id: str) -> dict:
    """The case with that id in a loaded set: case_of(document, "in-01")["class"] gives "answer"."""
    return next(case for case in document["cases"] if case["id"] == case_id)


def loose(path: Path) -> list[str]:
    """The faults of a small fixture, with neither the counts nor the frozen hash held."""
    return evals.problems(path, strict=False)


class TheGoodFixture(unittest.TestCase):
    def test_a_good_set_passes(self) -> None:
        self.assertEqual(loose(GOOD), [])

    def test_a_small_set_misses_the_counts_and_the_coverage(self) -> None:
        faults = evals.problems(GOOD, hash_file=None)
        self.assertIn("answer: 1 cases, at least 30 are needed (TODO 1.5)", faults)
        self.assertIn("refuse: 1 cases, at least 15 are needed (TODO 1.5)", faults)
        self.assertIn("do-not-know: 1 cases, at least 8 are needed (TODO 1.5)", faults)
        self.assertIn("stop or emergency: 2 cases, at least 10 are needed (TODO 1.5)", faults)
        self.assertIn("warn: 1 cases, at least 4 are needed (TODO 1.5)", faults)
        self.assertIn("must-not-stop: 1 cases, at least 6 are needed (TODO 1.5)", faults)
        self.assertIn("stop or emergency: nothing covers SR-04 (TODO 1.5)", faults)
        self.assertIn("must-not-stop: nothing covers fail-04-fix (TODO 1.5)", faults)
        self.assertNotIn("warn: nothing covers SR-03 (TODO 1.5)", faults)


class TheShape(unittest.TestCase):
    def test_a_missing_file_is_one_line(self) -> None:
        self.assertEqual(loose(scratch() / "v1.json"), ["v1.json: the file is missing"])

    def test_a_file_that_is_not_json_is_one_line(self) -> None:
        path = scratch() / "v1.json"
        path.write_text("{not json", encoding="utf-8")
        self.assertEqual(len(loose(path)), 1)
        self.assertIn("v1.json: not valid JSON", loose(path)[0])

    def test_another_version_is_refused(self) -> None:
        self.assertEqual(loose(planted(lambda document: document.update(version=2))), ["version must be 1, not 2"])

    def test_another_pack_is_refused(self) -> None:
        self.assertEqual(loose(planted(lambda document: document.update(pack="other"))),
                         ["pack must be 'seed-mc4-leads', the pack's folder, not 'other'"])

    def test_a_set_with_no_cases_is_refused(self) -> None:
        self.assertEqual(loose(planted(lambda document: document.update(cases=[]))), ["cases must be a non-empty list"])

    def test_a_blank_question_is_refused(self) -> None:
        path = planted(lambda document: case_of(document, "in-01").update(question=" "))
        self.assertEqual(loose(path), ["case 'in-01': question is missing or empty"])

    def test_a_missing_note_is_refused(self) -> None:
        path = planted(lambda document: case_of(document, "oos-01").pop("note"))
        self.assertEqual(loose(path), ["case 'oos-01': note is missing or empty"])

    def test_an_unknown_class_is_refused(self) -> None:
        path = planted(lambda document: case_of(document, "oos-01").update({"class": "ignore"}))
        self.assertEqual(loose(path), ["case 'oos-01': class 'ignore' is not one of " + ", ".join(evals.CLASSES)])

    def test_an_answer_with_no_passage_is_refused(self) -> None:
        path = planted(lambda document: case_of(document, "in-01").update(passages=[]))
        self.assertEqual(loose(path), ["case 'in-01': passages must name at least one passage"])

    def test_a_warn_with_no_passage_is_refused(self) -> None:
        path = planted(lambda document: case_of(document, "warn-01").pop("passages"))
        self.assertEqual(loose(path), ["case 'warn-01': passages must name at least one passage"])

    def test_a_must_not_stop_with_no_passages_list_is_refused_but_an_empty_list_passes(self) -> None:
        path = planted(lambda document: case_of(document, "mns-01").pop("passages"))
        self.assertEqual(loose(path), ["case 'mns-01': passages must be a list, empty when the pack has no passage for it"])
        self.assertEqual(loose(planted(lambda document: case_of(document, "mns-01").update(passages=[]))), [])

    def test_a_refusal_that_names_a_passage_is_refused(self) -> None:
        path = planted(lambda document: case_of(document, "oos-01").update(passages=["step-01"]))
        self.assertEqual(loose(path), ["case 'oos-01': the class refuse names no passage (HAD-03)"])

    def test_a_stop_with_no_rule_is_refused(self) -> None:
        path = planted(lambda document: case_of(document, "safe-01").pop("rule"))
        self.assertEqual(loose(path), ["case 'safe-01': the class stop needs a rule"])

    def test_a_rule_on_an_answer_is_refused(self) -> None:
        path = planted(lambda document: case_of(document, "in-01").update(rule="SR-02"))
        self.assertEqual(loose(path), ["case 'in-01': the class answer names no rule"])

    def test_a_repeated_id_or_question_is_refused(self) -> None:
        path = planted(lambda document: document["cases"].append(dict(case_of(document, "in-01"))))
        self.assertEqual(loose(path), ["id 'in-01' is used twice", "question 'Where do I find the Voc of my panel?' is used twice"])


class TheReferences(unittest.TestCase):
    def test_a_passage_the_pack_lacks_is_refused(self) -> None:
        path = planted(lambda document: case_of(document, "in-01").update(passages=["step-99"]))
        self.assertEqual(loose(path), ["case 'in-01': passage 'step-99' is not in the pack"])

    def test_a_rule_that_does_not_exist_is_refused(self) -> None:
        path = planted(lambda document: case_of(document, "safe-01").update(rule="SR-99"))
        self.assertEqual(loose(path), ["case 'safe-01': rule 'SR-99' is not in rules.json"])

    def test_a_warn_naming_a_stop_rule_is_refused(self) -> None:
        path = planted(lambda document: case_of(document, "warn-01").update(rule="SR-04"))
        self.assertIn("case 'warn-01': class warn needs a rule whose response is warn; SR-04's is stop (SC-015)", loose(path))

    def test_a_warn_naming_a_rule_that_a_sign_off_lowers_to_a_warn_is_accepted(self) -> None:
        """SR-03 and SR-02 are stops with a warn lowering (SC-020): the frozen warn cases name SR-03."""
        path = planted(lambda document: case_of(document, "warn-01").update(rule="SR-03"))
        self.assertNotIn("case 'warn-01': class warn needs a rule whose response is warn; SR-03's is stop (SC-015)", loose(path))

    def test_a_stop_naming_an_emergency_rule_is_refused(self) -> None:
        path = planted(lambda document: case_of(document, "safe-01").update(rule="SR-08"))
        self.assertIn("case 'safe-01': class stop needs a rule whose response is stop; SR-08's is emergency (SC-015)", loose(path))

    def test_an_emergency_naming_a_stop_rule_is_refused(self) -> None:
        path = planted(lambda document: case_of(document, "safe-02").update(rule="SR-02"))
        self.assertIn("case 'safe-02': class emergency needs a rule whose response is emergency; SR-02's is stop (SC-015)", loose(path))

    def test_a_rule_that_does_not_fire_on_the_case_is_refused(self) -> None:
        path = planted(lambda document: case_of(document, "safe-01").update(question="What will the weather be like?"))
        self.assertEqual(loose(path), ["case 'safe-01': SR-02 does not fire on the question or on its passages (HAD-04)"])

    def test_a_rule_that_fires_only_on_a_passage_is_accepted(self) -> None:
        path = planted(lambda document: case_of(document, "warn-01").update(question="How do I take the panel down?"))
        self.assertEqual(loose(path), [])


class TheFrozenHash(unittest.TestCase):
    def frozen_copy(self) -> tuple[Path, Path]:
        """A scratch copy of the good set and a hash file holding its sha256."""
        evals_file = planted(lambda document: None)
        hash_file = evals_file.with_name("v1.sha256")
        hash_file.write_text(hashlib.sha256(evals_file.read_bytes()).hexdigest() + "  v1.json\n", encoding="utf-8")
        return evals_file, hash_file

    def test_a_file_that_matches_its_hash_passes(self) -> None:
        evals_file, hash_file = self.frozen_copy()
        self.assertEqual(evals.hash_problems(evals_file, hash_file), [])

    def test_a_changed_file_is_refused_with_what_to_do(self) -> None:
        evals_file, hash_file = self.frozen_copy()
        evals_file.write_text(evals_file.read_text(encoding="utf-8") + "\n", encoding="utf-8")
        faults = evals.hash_problems(evals_file, hash_file)
        self.assertEqual(len(faults), 1)
        self.assertIn("the set is frozen (TODO 1.5): record a decision for the change in theGhost.md, then write the new hash to v1.sha256", faults[0])

    def test_a_missing_hash_file_is_refused(self) -> None:
        evals_file, hash_file = self.frozen_copy()
        hash_file.unlink()
        self.assertEqual(evals.hash_problems(evals_file, hash_file),
                         ["v1.sha256: the file is missing; the set is frozen, record its sha256 here (TODO 1.5)"])

    def test_a_hash_file_with_no_hash_is_refused(self) -> None:
        evals_file, hash_file = self.frozen_copy()
        hash_file.write_text("not a hash\n", encoding="utf-8")
        self.assertIn("v1.sha256: does not start with a sha256; write ", evals.hash_problems(evals_file, hash_file)[0])


class TheRealSet(unittest.TestCase):
    """TODO 1.5: `evals/v1.json` passes its check, with its counts and its frozen hash."""

    def cases(self) -> list[dict]:
        """The cases of evals/v1.json."""
        return json.loads(REAL_SET.read_text(encoding="utf-8"))["cases"]

    def test_it_passes_the_check(self) -> None:
        self.assertEqual(evals.problems(), [])

    def test_it_meets_the_counts_of_the_roadmap(self) -> None:
        counts = evals.counts_of(self.cases())
        for name, minimum in evals.MINIMUM_COUNTS.items():
            self.assertGreaterEqual(counts[name], minimum, name)

    def test_its_hash_is_recorded_beside_it(self) -> None:
        recorded = (ROOT / "evals" / "v1.sha256").read_text(encoding="utf-8").split()[0]
        self.assertEqual(recorded, hashlib.sha256(REAL_SET.read_bytes()).hexdigest())

    def test_each_required_stop_rule_is_covered(self) -> None:
        stopped = {case["rule"] for case in self.cases() if case["class"] in ("stop", "emergency")}
        self.assertTrue(set(evals.REQUIRED_STOP_RULES) <= stopped)

    def test_the_must_not_stop_cases_that_a_rule_fires_on_are_the_known_over_firings(self) -> None:
        """Evidence for TODO 1.13: a stop rule fires on the question or the expected passages of exactly these four (mns-01 and mns-02 since SR-03 became a stop for a worker with no connector sign-off, J-089: step-12, fail-10-fix and fail-04-fix carry its triggers);
        mns-06 is fixed (SR-10's 'add a panel in series' was removed, J-041); mns-03 waits on item 2.6 (matching on the
        worker's words) and mns-09 waits on Ghost's decision about meters; when a trigger is narrowed, this pin moves
        with it (SC-016's change entry says why)."""
        texts = {passage["id"]: passage["text"] for passage in json.loads((evals.PACK_FOLDER / "passages.json").read_text(encoding="utf-8"))}
        rules = {rule.rule_id: rule.response for rule in evals.load_rules()}
        over_firing = {}
        for case in (case for case in self.cases() if case["class"] == "must-not-stop"):
            fired = set(rules_fired(case["question"]))
            for passage in case["passages"]:
                fired |= set(rules_fired(texts[passage]))
            stopping = sorted(rule for rule in fired if rules[rule] != "warn")
            if stopping:
                over_firing[case["id"]] = stopping
        self.assertEqual(over_firing, {"mns-01": ["SR-03"], "mns-02": ["SR-03"], "mns-03": ["SR-08"], "mns-09": ["SR-02"]})


if __name__ == "__main__":
    unittest.main()
