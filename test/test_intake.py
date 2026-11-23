"""SC-027: the equipment intake. The list and the question, the model's reading of the answer (checked), the stub's word matching,
`--equipment`, the equipment line in the messages and never in the system block; a fake client and scripted input (TODO 2.14)."""
import contextlib
import io
import json
import unittest
from types import SimpleNamespace
from unittest import mock

from solarchat.cli.main import MENU, main
from solarchat.leaf.contract import Equipment, Turn
from solarchat.model.claude import MAX_TOKENS, SYSTEM_PROMPT, ClaudeAnswerer, ModelError, messages_for
from solarchat.model.lines import equipment_line
from solarchat.packs.load import load_pack
from solarchat.project import chat
from solarchat.project.intake import (QUESTION, equipment_of, equipment_name, list_text, parse_option, read_answer, said_back, word_match)
from solarchat.project.speech import Speaker
from test.support import ROOT
from test.test_claude import FakeClient, FakeErrors, Refusal, answer_json, text_response
from test.test_speech import Fake, found

SEED = ROOT / "packs" / "seed-mc4-leads"
OFFERED = load_pack(SEED).equipment
VICTRON, ECOFLOW, CONNECTOR, GENERAL = OFFERED
VICTRON_NAME = "Victron Energy SmartSolar MPPT 75/10 to 100/20"
NO_PACK = ("I have no pack for that equipment. I can give the general steps for crystalline silicon panels with MC4 leads; "
           "where your maker's manual says otherwise, follow the manual.")
ID = {"ids": ["victron-smartsolar-mppt"]}
DONT_KNOW = text_response(answer_json([], "No.", "do_not_know"))


def talk(client: FakeClient, lines: str, equipment: str | None = None) -> tuple[int, str, str]:
    """A whole chat on the seed pack with the Claude answerer on `client`, the profile given and `equipment` as --equipment gives
    it: talk(FakeClient([...]), "victron\nquit\n") gives (0, stdout, stderr)."""
    out, err = io.StringIO(), io.StringIO()
    with mock.patch("solarchat.model.claude.default_client", lambda: client), mock.patch.dict("os.environ", {"ANTHROPIC_API_KEY": "set-for-the-test"}):
        code = chat.start_chat(str(SEED), True, "claude", io.StringIO(lines), out, err, role="new", signed_off=frozenset(), equipment=equipment)
    return code, out.getvalue(), err.getvalue()


def stub_chat(lines: str, options: tuple[str, ...] = ()) -> tuple[int, str, str]:
    """A whole stub chat through the command, with the profile given on the command line: stub_chat("quit\n", ("--equipment",
    "none")) gives (0, stdout, stderr)."""
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stderr(err):
        code = main(["--pack", str(SEED), "--demo", "--answerer", "stub", "--role", "new", "--signed-off", "none", *options], io.StringIO(lines), out, err)
    return code, out.getvalue(), err.getvalue()


class TheListAndQuestion(unittest.TestCase):
    def test_the_list_is_one_line_per_entry_grouped_by_kind_with_any_makes_as_the_model_alone(self) -> None:
        self.assertEqual(list_text(OFFERED), "\n".join([
            "I can help with:", "- Crystalline silicon panels with MC4 leads (the general steps)", f"- {VICTRON_NAME}", "- EcoFlow R600",
            "- MC4 and MC4-compatible connectors"]))

    def test_after_the_profile_the_list_then_the_question_then_the_first_prompt(self) -> None:
        code, out, _ = stub_chat("not sure\nquit\n")
        self.assertEqual(code, 0)
        positions = [out.index(text) for text in ("You are new to solar", "I can help with:", QUESTION, NO_PACK)]
        self.assertEqual(positions, sorted(positions))
        self.assertTrue(out.index(NO_PACK) < out.rindex("> "))

    def test_list_and_question_and_said_back_are_spoken(self) -> None:
        fake = Fake()
        out, err = io.StringIO(), io.StringIO()
        with mock.patch("solarchat.project.chat.Speaker", lambda stderr: Speaker(stderr, fake, "linux", found)):
            main(["--pack", str(SEED), "--demo", "--answerer", "stub", "--voice", "--role", "new", "--signed-off", "none"],
                 io.StringIO("Victron SmartSolar 75/10\nquit\n"), out, err)
        said = [text for _, text in fake.calls]
        self.assertEqual(said[-3:], [list_text(OFFERED), QUESTION, f"Working with: {VICTRON_NAME}. If that is wrong, say so at any point."])

    def test_a_pack_with_no_equipment_has_no_intake(self) -> None:
        out = io.StringIO()
        code = chat.start_chat(str(ROOT / "test" / "fixtures" / "packs" / "good"), False, "stub", io.StringIO("quit\n"), out, io.StringIO(),
                               role="new", signed_off=frozenset())
        self.assertEqual(code, 0)
        self.assertNotIn("I can help with", out.getvalue())


class TheModelsReading(unittest.TestCase):
    def test_a_match_is_said_back_and_told_to_the_answerer_in_the_messages_beside_the_profile_line(self) -> None:
        client = FakeClient([text_response(ID), DONT_KNOW])
        code, out, _ = talk(client, "victron 75 10\nWhat now?\nquit\n")
        self.assertEqual(code, 0)
        self.assertIn(f"Working with: {VICTRON_NAME}. If that is wrong, say so at any point.", out)
        self.assertEqual(client.calls[1]["messages"][-1]["content"],
                         f"The worker: new to solar; signed off for: none.\nThe equipment: {VICTRON_NAME} (controller).\n\nWhat now?")

    def test_the_identifying_call_has_its_own_short_system_text_and_schema_and_its_tokens_count(self) -> None:
        client = FakeClient([text_response(ID), DONT_KNOW])
        answerer = ClaudeAnswerer(client, FakeErrors)
        self.assertEqual(answerer.identify("smart solar mppt", OFFERED), ("victron-smartsolar-mppt",))
        call = client.calls[0]
        self.assertEqual(call["output_config"]["format"]["schema"], {
            "type": "object", "properties": {"ids": {"type": "array", "items": {"type": "string", "enum": [each.id for each in OFFERED]}}},
            "required": ["ids"], "additionalProperties": False})
        self.assertEqual(len(call["system"]), 1)
        self.assertNotIn("cache_control", call["system"][0])
        self.assertNotIn("passage", call["system"][0]["text"].lower().replace("passages", ""))  # no passages in this call
        self.assertLess(len(call["system"][0]["text"]), len(SYSTEM_PROMPT))
        self.assertLess(call["max_tokens"], MAX_TOKENS)
        self.assertIn("smart solar mppt", call["messages"][0]["content"])
        self.assertEqual((answerer.usage.calls, answerer.usage.input_tokens, answerer.usage.output_tokens), (1, 10, 2))

    def test_no_match_says_so_and_offers_the_general_steps_and_the_answerer_is_told_none_covered(self) -> None:
        client = FakeClient([text_response({"ids": []}), DONT_KNOW])
        _, out, _ = talk(client, "a Solarex 300\nWhat now?\nquit\n")
        self.assertIn(NO_PACK, out)
        self.assertTrue(client.calls[1]["messages"][-1]["content"].startswith("The worker: new to solar; signed off for: none.\nThe equipment: not one the packs cover."))

    def test_not_sure_is_no_match_with_no_call(self) -> None:
        for answer in ("not sure", "I don't know", "", "No idea"):
            with self.subTest(answer=answer):
                client = FakeClient([DONT_KNOW])
                _, out, _ = talk(client, f"{answer}\nquit\n")
                self.assertEqual(client.calls, [])
                self.assertIn(NO_PACK, out)

    def test_an_id_off_the_list_is_dropped_and_a_listed_one_kept(self) -> None:
        client = FakeClient([text_response({"ids": ["nope", "victron-smartsolar-mppt", "victron-smartsolar-mppt"]}), DONT_KNOW])
        _, out, _ = talk(client, "victron\nquit\n")
        self.assertIn(f"Working with: {VICTRON_NAME}.", out)
        self.assertEqual(ClaudeAnswerer(FakeClient([text_response({"ids": ["nope"]})]), FakeErrors).identify("x", OFFERED), ())

    def test_a_refusal_a_bad_reply_and_a_model_error_are_no_match_and_the_chat_goes_on(self) -> None:
        for outcome in (Refusal(), text_response("not json"), text_response({"ids": "r600"}), text_response([1])):
            with self.subTest(outcome=type(outcome).__name__):
                _, out, err = talk(FakeClient([outcome, DONT_KNOW]), "victron\nWhat now?\nquit\n")
                self.assertIn(NO_PACK, out)
                self.assertIn("I do not know", out)
                self.assertEqual(err, "")

    def test_the_system_block_is_the_same_bytes_whatever_the_equipment(self) -> None:
        blocks = set()
        for ids in ([], ["victron-smartsolar-mppt"], ["ecoflow-r600", "mc4-connector"]):
            client = FakeClient([text_response({"ids": ids}), DONT_KNOW])
            talk(client, "something\nWhat now?\nquit\n")
            blocks.add(json.dumps(client.calls[1]["system"], sort_keys=True))
        self.assertEqual(len(blocks), 1)
        self.assertNotIn("Victron Energy", next(iter(blocks)).replace("Victron controller", ""))

    def test_the_prompt_paragraph_is_fixed_text_between_depth_and_citing(self) -> None:
        self.assertIn("Equipment. The message may name the worker's equipment.", SYSTEM_PROMPT)
        self.assertTrue(SYSTEM_PROMPT.index("Profile.") < SYSTEM_PROMPT.index("Equipment.") < SYSTEM_PROMPT.index("Citing."))


class TheEquipmentLine(unittest.TestCase):
    def test_none_not_asked_nothing_covered_one_and_several(self) -> None:
        self.assertEqual(equipment_line(None), "")
        self.assertEqual(equipment_line(()), "The equipment: not one the packs cover.")
        self.assertEqual(equipment_line((VICTRON,)), f"The equipment: {VICTRON_NAME} (controller).")
        self.assertEqual(equipment_line((ECOFLOW, CONNECTOR)), "The equipment: EcoFlow R600 (power-station); MC4 and MC4-compatible connectors (connector).")

    def test_the_messages_begin_with_the_lines_that_exist(self) -> None:
        self.assertEqual(messages_for("Next?", (Turn("user", "Hi"),), None, (ECOFLOW,))[-1]["content"], "The equipment: EcoFlow R600 (power-station).\n\nNext?")
        self.assertEqual(messages_for("Next?", ())[-1]["content"], "Next?")


class TheStubsWordMatching(unittest.TestCase):
    def names(self, text: str) -> list[str]:
        """The ids word_match gives for a text: names("ECOFLOW r600") gives ["ecoflow-r600"]."""
        return [entry.id for entry in word_match(text, OFFERED)]

    def test_whole_words_of_four_letters_or_more_of_the_make_or_the_models_first_word(self) -> None:
        self.assertEqual(self.names("Victron SmartSolar 75/10"), ["victron-smartsolar-mppt"])
        self.assertEqual(self.names("my smartsolar"), ["victron-smartsolar-mppt"])
        self.assertEqual(self.names("ECOFLOW r600"), ["ecoflow-r600"])
        self.assertEqual(self.names("a crystalline panel"), ["crystalline-panel-mc4"])

    def test_short_words_partial_words_and_any_never_match(self) -> None:
        for text in ("mc4 and any panel", "victr", "victronic", "my R60", "the panel on the roof"):
            with self.subTest(text=text):
                self.assertEqual(self.names(text), [])

    def test_the_stub_chat_says_the_match_back_and_not_sure_is_no_match(self) -> None:
        self.assertIn(f"Working with: {VICTRON_NAME}.", stub_chat("Victron SmartSolar 75/10\nquit\n")[1])
        self.assertIn(NO_PACK, stub_chat("not sure\nquit\n")[1])

    def test_read_answer_uses_identify_when_the_answerer_has_it_and_keeps_only_listed_entries(self) -> None:
        answerer = SimpleNamespace(identify=lambda text, equipment: ("ecoflow-r600", "ghost"))
        self.assertEqual(read_answer("anything", OFFERED, answerer), (ECOFLOW,))

        def failing(text: str, equipment: tuple[Equipment, ...]) -> tuple[str, ...]:
            """An identify that fails: failing("victron", OFFERED) raises ModelError."""
            raise ModelError("the model service could not be reached")
        self.assertEqual(read_answer("victron", OFFERED, SimpleNamespace(identify=failing)), ())

    def test_a_typed_sdk_error_in_the_identifying_call_is_a_model_error_the_chat_reads_as_no_match(self) -> None:
        answerer = ClaudeAnswerer(FakeClient([FakeErrors.APIConnectionError()]), FakeErrors)
        with self.assertRaisesRegex(ModelError, "could not be reached"):
            answerer.identify("victron", OFFERED)
        self.assertEqual(read_answer("victron", OFFERED, answerer), ())


class TheOption(unittest.TestCase):
    def test_an_id_skips_the_list_question_and_reading_and_is_said_back(self) -> None:
        client = FakeClient([DONT_KNOW])
        _, out, _ = talk(client, "What now?\nquit\n", equipment="victron-smartsolar-mppt")
        self.assertNotIn("I can help with", out)
        self.assertNotIn(QUESTION, out)
        self.assertIn(f"Working with: {VICTRON_NAME}.", out)
        self.assertEqual(len(client.calls), 1)  # no identifying call
        self.assertIn(f"The equipment: {VICTRON_NAME} (controller).", client.calls[0]["messages"][-1]["content"])

    def test_several_ids_and_none(self) -> None:
        self.assertEqual(parse_option("ecoflow-r600, mc4-connector", OFFERED), (ECOFLOW, CONNECTOR))
        self.assertEqual(parse_option("none", OFFERED), ())
        _, out, _ = stub_chat("quit\n", ("--equipment", "none"))
        self.assertIn(NO_PACK, out)

    def test_an_unknown_id_is_an_error_naming_the_offered_ids_and_exit_2(self) -> None:
        code, out, err = stub_chat("quit\n", ("--equipment", "toaster"))
        self.assertEqual(code, 2)
        self.assertIn("toaster is not equipment on the list; the ids are victron-smartsolar-mppt, ecoflow-r600, mc4-connector, crystalline-panel-mc4, or none", err)
        self.assertEqual(out, "")

    def test_the_menu_names_the_option(self) -> None:
        self.assertIn("--equipment <ids>", MENU)


class TheClash(unittest.TestCase):
    def test_an_id_in_two_packs_is_refused_in_words(self) -> None:
        other = load_pack(ROOT / "test" / "fixtures" / "packs" / "equipped")
        clashing = type(other)("second", other.manifest, other.passages, other.citations, other.coverage, (VICTRON,))
        with self.assertRaisesRegex(ValueError, "equipment id 'victron-smartsolar-mppt' is in both second and second"):
            equipment_of((clashing, clashing))
        first = type(other)("first", other.manifest, other.passages, other.citations, other.coverage, (VICTRON,))
        with self.assertRaisesRegex(ValueError, "equipment id 'victron-smartsolar-mppt' is in both first and second"):
            equipment_of((first, clashing))
        self.assertEqual(len(equipment_of((load_pack(SEED), other))), 6)

    def test_the_names_and_the_no_general_entry_words(self) -> None:
        self.assertEqual(equipment_name(CONNECTOR), "MC4 and MC4-compatible connectors")
        self.assertEqual(said_back((), (VICTRON,)), "I have no pack for that equipment. I can only help with the equipment listed above.")


if __name__ == "__main__":
    unittest.main()
