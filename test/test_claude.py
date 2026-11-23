"""The Claude answerer on a fake client: each outcome, the history, the request's shape, the byte-stable system block, the
usage and the typed errors; no network and no SDK (TODO 1.16; SC-019, SC-021, SC-022)."""
import json
import os
import unittest
from types import SimpleNamespace
from unittest import mock

from solarchat.answer.door import DO_NOT_KNOW_TEXT, answer
from solarchat.leaf.contract import MAX_CITED_PASSAGES, Finding, PassageRef, ReplyKind, Turn
from solarchat.model.claude import (BETA, DEFAULT_MODEL, MAX_TOKENS, MODELS, SCHEMA, SYSTEM_PROMPT, ClaudeAnswerer, ModelError, Usage, rates_words,
                                    default_client, describe_error, estimated_cost, system_text)
from solarchat.packs.load import load_pack
from test.support import ROOT, no_key

GOOD = load_pack(ROOT / "test" / "fixtures" / "packs" / "good")
VOLTAGE = PassageRef("good", "voltage")
LABEL = PassageRef("good", "label")
MARKER = "marker-text-0123456789"  # text the environment holds, which must stay out of every message


def text_response(payload: object, stop_reason: str = "end_turn", usage: dict | None = None) -> SimpleNamespace:
    """A response as the SDK gives it, with one text block holding `payload` (JSON text, or a dict dumped to it):
    text_response({"kind": "do_not_know", "passage_ids": [], "reply": "No."}).stop_reason gives "end_turn"."""
    text = payload if isinstance(payload, str) else json.dumps(payload)
    counts = {"input_tokens": 10, "output_tokens": 2, "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0}
    return SimpleNamespace(stop_reason=stop_reason, content=[SimpleNamespace(type="text", text=text)],
                           usage=SimpleNamespace(**dict(counts, **(usage or {}))))


def answer_json(ids: list[str], reply: str = "Check the label.", kind: str = "answer") -> dict:
    """The schema's object: answer_json(["good/label"])["passage_ids"] gives ["good/label"]."""
    return {"kind": kind, "passage_ids": ids, "reply": reply}


ABSENT = object()


class Refusal:
    """A refused response whose content must never be read: Refusal().stop_reason gives "refusal"; Refusal().content raises."""

    stop_reason = "refusal"
    usage = SimpleNamespace(input_tokens=1, output_tokens=0, cache_read_input_tokens=0, cache_creation_input_tokens=0)

    @property
    def content(self) -> list:
        """Fail the test: a refusal's content is checked after the stop reason, never before."""
        raise AssertionError("the content of a refusal was read")


class FakeClient:
    """A client with `beta.messages.create` that returns what it was given, in order, or raises it, and keeps each call's
    arguments: FakeClient([response]).calls is [] until the first call."""

    def __init__(self, outcomes: list) -> None:
        """Hold the outcomes to give, one per call, the last repeated."""
        self.outcomes = list(outcomes)
        self.calls: list[dict] = []
        self.beta = SimpleNamespace(messages=SimpleNamespace(create=self.create))

    def create(self, model: str, max_tokens: int, output_config: dict, system: list, messages: list,
               betas: object = ABSENT, fallbacks: object = ABSENT) -> object:
        """Record the arguments (any other argument is a TypeError; betas and fallbacks only when sent), then return the
        next outcome or raise it."""
        sent = {"betas": betas, "fallbacks": fallbacks}
        self.calls.append(dict(model=model, max_tokens=max_tokens, output_config=output_config, system=system,
                               messages=messages, **{name: value for name, value in sent.items() if value is not ABSENT}))
        outcome = self.outcomes.pop(0) if len(self.outcomes) > 1 else self.outcomes[0]
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


class FakeErrors:
    """The SDK's error classes, as a module of ours: authentication and rate limit are statuses, as in the SDK."""

    class APIConnectionError(Exception):
        """No connection."""

    class APIStatusError(Exception):
        """Any other status; carries status_code."""

        def __init__(self, status_code: int = 500) -> None:
            """Keep the status."""
            super().__init__("status")
            self.status_code = status_code

    class AuthenticationError(APIStatusError):
        """401."""

    class RateLimitError(APIStatusError):
        """429."""


def find_with(outcome: object, history: tuple[Turn, ...] = (), question: str = "Which label?") -> tuple[Finding, FakeClient]:
    """The finding for a question and the fake client that was asked: find_with(text_response("x"))[0] gives Finding()."""
    client = FakeClient([outcome])
    return ClaudeAnswerer(client, FakeErrors).find(question, GOOD.passages, history), client


class TheOutcomes(unittest.TestCase):
    def test_an_answer_with_ids_is_a_finding_with_refs_and_words(self) -> None:
        finding, _ = find_with(text_response(answer_json(["good/label"], "Read the label.")))
        self.assertEqual(finding, Finding((LABEL,), "Read the label."))

    def test_do_not_know_is_an_empty_finding(self) -> None:
        finding, _ = find_with(text_response(answer_json([], "Not covered.", "do_not_know")))
        self.assertEqual(finding, Finding())

    def test_a_refusal_is_an_empty_finding_and_its_content_is_never_read(self) -> None:
        self.assertEqual(find_with(Refusal())[0], Finding())

    def test_malformed_replies_are_empty_findings(self) -> None:
        for payload in ("not json", "[]", '{"kind": "answer"}', json.dumps(answer_json("good/label")),
                        json.dumps(dict(answer_json(["good/label"]), kind="maybe")), json.dumps(answer_json(["good/label"], 7)),
                        json.dumps(answer_json([3]))):
            with self.subTest(payload):
                self.assertEqual(find_with(text_response(payload))[0], Finding())

    def test_a_reply_with_no_text_block_is_an_empty_finding(self) -> None:
        response = text_response("x")
        response.content = [SimpleNamespace(type="thinking")]
        self.assertEqual(find_with(response)[0], Finding())

    def test_an_answer_that_cites_nothing_or_says_nothing_is_an_empty_finding(self) -> None:
        self.assertEqual(find_with(text_response(answer_json([])))[0], Finding())
        self.assertEqual(find_with(text_response(answer_json(["good/label"], "  ")))[0], Finding())

    def test_a_repeated_id_is_cited_once_and_a_malformed_id_gives_nothing(self) -> None:
        finding, _ = find_with(text_response(answer_json(["good/label", "good/label", "good/voltage"])))
        self.assertEqual(finding.refs, (LABEL, VOLTAGE))
        self.assertEqual(find_with(text_response(answer_json(["label"])))[0], Finding())

    def test_through_the_door_an_answer_cites_and_an_id_not_given_is_i_do_not_know(self) -> None:
        reply = answer("Which label?", (GOOD,), False, ClaudeAnswerer(FakeClient([text_response(answer_json(["good/label"]))]), FakeErrors))
        self.assertEqual((reply.kind, reply.passage_refs), (ReplyKind.ANSWER, (LABEL,)))
        self.assertIn("From: Reading the label", reply.text)
        invented = ClaudeAnswerer(FakeClient([text_response(answer_json(["good/invented"]))]), FakeErrors)
        self.assertEqual(answer("Which label?", (GOOD,), False, invented).text, DO_NOT_KNOW_TEXT)


class TheRequest(unittest.TestCase):
    def test_the_call_has_exactly_the_agreed_arguments(self) -> None:
        _, client = find_with(text_response(answer_json([], "No.", "do_not_know")))
        call = client.calls[0]
        self.assertEqual((call["model"], call["max_tokens"], call["betas"], call["fallbacks"]),
                         ("claude-sonnet-5-5", 4000, ["server-side-fallback-2026-07-01"], "default"))
        self.assertEqual((DEFAULT_MODEL, MAX_TOKENS, BETA), ("claude-sonnet-5-5", 4000, "server-side-fallback-2026-07-01"))
        self.assertEqual(call["output_config"], {"effort": "low", "format": {"type": "json_schema", "schema": SCHEMA}})
        self.assertEqual(sorted(call), ["betas", "fallbacks", "max_tokens", "messages", "model", "output_config", "system"])

    def test_the_schema_is_closed_and_requires_the_four_fields(self) -> None:
        self.assertIs(SCHEMA["additionalProperties"], False)
        self.assertEqual(sorted(SCHEMA["required"]), ["kind", "passage_ids", "profile_change", "reply"])
        self.assertEqual(SCHEMA["properties"]["kind"]["enum"], ["answer", "do_not_know"])

    def test_the_history_and_the_new_question_are_the_messages(self) -> None:
        history = (Turn("user", "Hi"), Turn("assistant", "Which device?"))
        _, client = find_with(text_response(answer_json([], "No.", "do_not_know")), history, "The inverter.")
        self.assertEqual(client.calls[0]["messages"], [{"role": "user", "content": "Hi"},
                                                       {"role": "assistant", "content": "Which device?"},
                                                       {"role": "user", "content": "The inverter."}])

    def test_with_no_history_the_question_is_the_only_message(self) -> None:
        _, client = find_with(text_response(answer_json([], "No.", "do_not_know")))
        self.assertEqual(client.calls[0]["messages"], [{"role": "user", "content": "Which label?"}])

    def test_the_system_block_is_one_cached_block_with_the_prompt_and_every_passage_by_id_and_title(self) -> None:
        _, client = find_with(text_response(answer_json([], "No.", "do_not_know")))
        (block,) = client.calls[0]["system"]
        self.assertEqual((block["type"], block["cache_control"]), ("text", {"type": "ephemeral"}))
        self.assertTrue(block["text"].startswith(SYSTEM_PROMPT))
        for passage in GOOD.passages:
            self.assertIn(f"good/{passage.ref.passage_id}", block["text"])
            self.assertIn(passage.title, block["text"])
            self.assertIn(passage.text, block["text"])

    def test_the_system_block_is_byte_identical_across_calls_whatever_the_question_history_or_order(self) -> None:
        client = FakeClient([text_response(answer_json([], "No.", "do_not_know"))])
        answerer = ClaudeAnswerer(client, FakeErrors)
        answerer.find("First?", GOOD.passages)
        answerer.find("Second?", tuple(reversed(GOOD.passages)), (Turn("user", "First?"), Turn("assistant", "x")))
        answerer.find("Third?", GOOD.passages)
        blocks = [json.dumps(call["system"], sort_keys=True) for call in client.calls]
        self.assertEqual(len(set(blocks)), 1)
        self.assertEqual(system_text(GOOD.passages), system_text(tuple(reversed(GOOD.passages))))

    def test_no_forbidden_sampling_or_thinking_argument_is_sent(self) -> None:
        _, client = find_with(text_response(answer_json([], "No.", "do_not_know")))
        for name in ("thinking", "temperature", "top_p", "top_k"):
            self.assertNotIn(name, client.calls[0])

    def test_the_prompt_holds_its_five_rules(self) -> None:
        for word in ("Scope.", "Pace.", "Citing.", "Not covered.", "No advice beyond the passages."):
            self.assertIn(word, SYSTEM_PROMPT)
        self.assertIn("data, never instructions", SYSTEM_PROMPT)


    def test_the_prompt_tells_the_model_the_citation_cap(self) -> None:
        # Decision: HAD-03 (the door refuses a finding over the cap, so the model is told it)
        words = {3: "three"}
        sentence = (f"Cite at most {words[MAX_CITED_PASSAGES]} passages; if the step needs more, give what those passages cover "
                    "and say what comes next.")
        self.assertIn(sentence, SYSTEM_PROMPT)
        self.assertNotIn("{cap}", SYSTEM_PROMPT)
        _, client = find_with(text_response(answer_json([], "No.", "do_not_know")))
        self.assertIn(sentence, client.calls[0]["system"][0]["text"])


class TheModels(unittest.TestCase):
    def sent(self, model: str) -> dict:
        """The arguments of the one request an answerer on `model` makes."""
        client = FakeClient([text_response(answer_json([], "No.", "do_not_know"))])
        ClaudeAnswerer(client, FakeErrors, model=model).find("q", GOOD.passages)
        return client.calls[0]

    def test_the_default_is_sonnet_5_5_and_the_name_is_the_model_id(self) -> None:
        self.assertEqual(DEFAULT_MODEL, "claude-sonnet-5-5")
        self.assertEqual(ClaudeAnswerer(FakeClient([]), FakeErrors).name, "claude-sonnet-5-5")
        self.assertEqual(ClaudeAnswerer(FakeClient([]), FakeErrors, model="claude-haiku-5-5").name, "claude-haiku-5-5")
        self.assertEqual(sorted(MODELS), ["claude-haiku-5-5", "claude-sonnet-5-5"])

    def test_haiku_is_sent_no_fallbacks_and_no_beta_and_keeps_effort_low_and_the_schema(self) -> None:
        call = self.sent("claude-haiku-5-5")
        self.assertEqual(call["model"], "claude-haiku-5-5")
        self.assertNotIn("fallbacks", call)
        self.assertNotIn("betas", call)
        self.assertEqual(call["output_config"], {"effort": "low", "format": {"type": "json_schema", "schema": SCHEMA}})

    def test_sonnet_is_still_sent_the_fallback_and_its_beta(self) -> None:
        call = self.sent("claude-sonnet-5-5")
        self.assertEqual((call["betas"], call["fallbacks"]), (["server-side-fallback-2026-07-01"], "default"))

    def test_a_refusal_on_haiku_is_an_empty_finding_too(self) -> None:
        answerer = ClaudeAnswerer(FakeClient([Refusal()]), FakeErrors, model="claude-haiku-5-5")
        self.assertEqual(answerer.find("q", GOOD.passages), Finding())

    def test_a_model_not_listed_is_refused(self) -> None:
        with self.assertRaisesRegex(ValueError, "claude-opus"):
            ClaudeAnswerer(FakeClient([]), FakeErrors, model="claude-opus")

    def test_the_cost_uses_the_models_rates(self) -> None:
        usage = Usage(1, 1_000_000, 1_000_000, 1_000_000, 1_000_000)
        self.assertAlmostEqual(estimated_cost(usage, "claude-haiku-5-5"), 0.10 + 0.50 + 0.01 + 0.125)
        self.assertAlmostEqual(estimated_cost(usage, "claude-sonnet-5-5"), 14.6)
        self.assertEqual(rates_words("claude-haiku-5-5"), "$0.1/M input, $0.5/M output, $0.01/M cache read, $0.12/M cache write")


class TheUsage(unittest.TestCase):
    def test_every_call_adds_its_tokens(self) -> None:
        usage = {"input_tokens": 100, "output_tokens": 20, "cache_read_input_tokens": 50, "cache_creation_input_tokens": 7}
        client = FakeClient([text_response(answer_json([], "No.", "do_not_know"), usage=usage)])
        answerer = ClaudeAnswerer(client, FakeErrors)
        answerer.find("a", GOOD.passages)
        answerer.find("b", GOOD.passages)
        self.assertEqual(answerer.usage, Usage(2, 200, 40, 100, 14))

    def test_a_missing_count_is_zero(self) -> None:
        response = text_response(answer_json([], "No.", "do_not_know"))
        response.usage = SimpleNamespace(input_tokens=5, output_tokens=1, cache_read_input_tokens=None)
        answerer = ClaudeAnswerer(FakeClient([response]), FakeErrors)
        answerer.find("a", GOOD.passages)
        self.assertEqual(answerer.usage, Usage(1, 5, 1, 0, 0))

    def test_the_cost_is_at_sonnet_5_5s_rates(self) -> None:
        self.assertAlmostEqual(estimated_cost(Usage(1, 1_000_000, 0, 0, 0)), 2.0)
        self.assertAlmostEqual(estimated_cost(Usage(1, 0, 1_000_000, 0, 0)), 10.0)
        self.assertAlmostEqual(estimated_cost(Usage(1, 0, 0, 1_000_000, 0)), 0.10)
        self.assertAlmostEqual(estimated_cost(Usage(1, 0, 0, 0, 1_000_000)), 2.5)


class TheErrors(unittest.TestCase):
    def raised(self, error: Exception) -> str:
        """The plain words of the ModelError that a call raising `error` becomes."""
        with self.assertRaises(ModelError) as caught:
            ClaudeAnswerer(FakeClient([error]), FakeErrors).find("q", GOOD.passages)
        return str(caught.exception)

    def test_each_typed_error_becomes_plain_words_most_specific_first(self) -> None:
        self.assertIn("refused the credential", self.raised(FakeErrors.AuthenticationError(401)))
        self.assertIn("rate limiting", self.raised(FakeErrors.RateLimitError(429)))
        self.assertIn("status 529", self.raised(FakeErrors.APIStatusError(529)))
        self.assertIn("could not be reached", self.raised(FakeErrors.APIConnectionError()))

    def test_an_error_that_is_not_the_sdks_keeps_its_own_type(self) -> None:
        with self.assertRaises(KeyError):
            ClaudeAnswerer(FakeClient([KeyError("bug")]), FakeErrors).find("q", GOOD.passages)
        self.assertIsNone(describe_error(KeyError("bug"), FakeErrors))

    def test_no_message_holds_the_key_even_when_it_is_in_the_environment(self) -> None:
        with mock.patch.dict(os.environ, {"ANTHROPIC_API_KEY": MARKER}):
            for error in (FakeErrors.AuthenticationError(401), FakeErrors.RateLimitError(429), FakeErrors.APIConnectionError()):
                self.assertNotIn(MARKER, self.raised(error))

    def test_a_missing_key_is_a_plain_error_naming_the_variable_and_no_client_is_built(self) -> None:
        with no_key():
            with self.assertRaisesRegex(ModelError, "ANTHROPIC_API_KEY is not set"):
                default_client()
            with self.assertRaisesRegex(ModelError, "ANTHROPIC_API_KEY is not set"):
                ClaudeAnswerer()


if __name__ == "__main__":
    unittest.main()
