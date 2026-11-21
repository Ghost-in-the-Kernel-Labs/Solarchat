"""The rule bank passes its check, and each planted break of each rule is refused (TODO 1.19; SC-023, design section 3)."""
import copy
import json
import unittest

from scripts.checks import bank
from solarchat.model.claude import SYSTEM_PROMPT
from test.support import BROKEN, ROOT, scratch

REAL_ASK = json.loads((ROOT / "evals" / "bank" / "ask.json").read_text(encoding="utf-8"))["rules"][0]
LOCATION = "ask.json: rule 'BR-0001'"


def broken(name: str) -> list[str]:
    """The faults the check finds in the planted break test/fixtures/broken/bank/<name>."""
    return bank.problems(BROKEN / "bank" / name)


class TheRealBank(unittest.TestCase):
    def test_the_bank_passes(self) -> None:
        counts: dict[str, int] = {}
        self.assertEqual(bank.problems(counts=counts), [])
        self.assertEqual(sum(counts.values()), 20)

    def test_the_bank_holds_the_families_and_the_five_safety_cases(self) -> None:
        counts: dict[str, int] = {}
        bank.problems(counts=counts)
        self.assertEqual(sorted(counts), ["ask", "pace", "safety", "track"])
        safety = json.loads((ROOT / "evals" / "bank" / "safety.json").read_text(encoding="utf-8"))["rules"]
        self.assertEqual(len(safety), 5)
        for rule in safety:
            self.assertIn("v1", [source["kind"] for source in rule["source"]])

    def test_a_folder_with_no_family_file_is_one_line(self) -> None:
        self.assertEqual(bank.problems(ROOT / "test" / "fixtures" / "broken" / "bank" / "none"),
                         ["the bank has no family file under evals/bank/"])


class TheShape(unittest.TestCase):
    def test_a_missing_field_is_refused(self) -> None:
        self.assertEqual(broken("missing-field"), [f"{LOCATION}: severity is missing"])

    def test_a_reused_id_is_refused(self) -> None:
        self.assertEqual(broken("reused-id"), ["ask.json: BR-0001 is used twice; an id is never reused"])

    def test_an_id_out_of_order_is_refused(self) -> None:
        self.assertEqual(broken("out-of-order-id"), ["ask.json: BR-0001 is out of order, after BR-0002"])

    def test_no_turns_is_refused(self) -> None:
        self.assertEqual(broken("no-turns"), [f"{LOCATION}: turns must be one to three worker turns, each a text"])

    def test_four_turns_are_refused(self) -> None:
        self.assertEqual(broken("four-turns"), [f"{LOCATION}: turns must be one to three worker turns, each a text"])

    def test_a_graded_reply_beyond_the_turns_is_refused(self) -> None:
        self.assertEqual(broken("graded-reply-beyond-turns"), [f'{LOCATION}: graded_reply 3 must be "all" or a reply from 1 to the 2 turns'])

    def test_a_question_without_a_question_mark_is_refused(self) -> None:
        self.assertEqual(broken("question-without-mark"), [f'{LOCATION}: question must end in "?"'])

    def test_a_boolean_is_not_a_reply_number(self) -> None:
        rule = copy.deepcopy(REAL_ASK)
        rule["graded_reply"] = True
        self.assertEqual(len(bank.shape_problems(rule, LOCATION, "ask")), 1)

    def test_a_rule_of_another_family_is_refused(self) -> None:
        self.assertEqual(bank.shape_problems(REAL_ASK, LOCATION, "pace"), [f"{LOCATION}: family 'ask' is not the file's, 'pace'"])

    def test_a_retired_rule_needs_its_reason(self) -> None:
        rule = copy.deepcopy(REAL_ASK)
        rule["status"] = "retired"
        self.assertEqual(bank.shape_problems(rule, LOCATION, "ask"), [f"{LOCATION}: a retired rule needs retired with on and why"])
        rule["retired"] = {"on": "2026-12-01", "why": "reworded as BR-0099"}
        self.assertEqual(bank.shape_problems(rule, LOCATION, "ask"), [])

    def test_a_file_that_is_not_json_is_one_line(self) -> None:
        path = scratch() / "ask.json"
        path.write_text("{not json", encoding="utf-8")
        faults, counted = bank.file_problems(path, set(), bank.Known([], ROOT / "packs", ROOT / "solarchat" / "safety" / "rules.json", set(), ROOT / "evals" / "v1.json"))
        self.assertEqual(len(faults), 1)
        self.assertIn("ask.json: not valid JSON", faults[0])
        self.assertEqual(counted, {})


class TheSources(unittest.TestCase):
    def test_a_pack_passage_the_pack_lacks_is_refused(self) -> None:
        self.assertEqual(broken("unresolved-pack-passage"), [f"{LOCATION}: source pack 'seed-mc4-leads/step-99' is not a passage of the pack"])

    def test_a_safety_rule_that_is_not_in_the_rules_is_refused(self) -> None:
        self.assertEqual(broken("unresolved-safety-rule"), [f"{LOCATION}: source safety-rule 'SR-99' is not in rules.json"])

    def test_a_library_id_that_is_not_a_source_folder_is_refused(self) -> None:
        self.assertEqual(broken("unresolved-library-id"), [f"{LOCATION}: source library 'no-such-source' is not a source folder of the library"])

    def test_a_frozen_case_that_is_not_in_the_set_is_refused(self) -> None:
        self.assertEqual(broken("unresolved-frozen-case"), [f"{LOCATION}: source v1 'safe-99' is not a case of the frozen set"])

    def test_the_library_ids_are_the_source_folders(self) -> None:
        self.assertIn("osha-solar-electrical", bank.library_ids(ROOT, ROOT / "library" / "sources"))


class TheSystemPrompt(unittest.TestCase):
    def test_a_question_quoting_the_prompt_is_refused(self) -> None:
        self.assertEqual(broken("quotes-system-prompt"),
                         [f"{LOCATION}: question quotes the bot's system prompt: 'give the one next thing the' (SC-023)"])

    def test_a_turn_quoting_the_prompt_is_refused_whatever_its_punctuation_and_case(self) -> None:
        self.assertEqual(broken("quotes-system-prompt-in-a-turn"),
                         [f"{LOCATION}: turns[0] quotes the bot's system prompt: 'and wait no preamble no summary' (SC-023)"])

    def test_a_fact_quoting_the_prompt_is_refused(self) -> None:
        self.assertEqual(broken("quotes-system-prompt-in-a-fact"),
                         [f"{LOCATION}: worker quotes the bot's system prompt: 'a phone in a few seconds' (SC-023)"])

    def test_five_words_in_common_are_allowed_and_six_are_not(self) -> None:
        five = "next thing the worker needs"
        six = "one next thing the worker needs"
        self.assertIn(five, SYSTEM_PROMPT.lower())
        self.assertIn(six, SYSTEM_PROMPT.lower())
        rule = {"question": f"Did it say the {five}?"}
        self.assertEqual(bank.quoting_problems(rule, "rule 'a'"), [])
        self.assertEqual(len(bank.quoting_problems({"question": f"Did it say the {six}?"}, "rule 'a'")), 1)

    def test_words_are_letters_and_digits_in_lower_case(self) -> None:
        self.assertEqual(bank.words_of("Stop, then WAIT -- 22.4 V."), ["stop", "then", "wait", "22", "4", "v"])


class TheCommand(unittest.TestCase):
    def test_the_script_says_ok_for_the_bank(self) -> None:
        self.assertEqual(bank.main([]), 0)

    def test_the_script_refuses_arguments(self) -> None:
        self.assertEqual(bank.main(["x"]), 2)


if __name__ == "__main__":
    unittest.main()
