"""The rule bank run's deterministic half: the sample, the ledger line and the door-fault cross-check (TODO 1.20; SC-023).

No model is called and no model client is imported; `docs/designs/rule-bank-and-triage.md` sections 4.1, 4.4 and 5.1 say
what each part is. TODO 1.21 adds the model roles and the `--live` command line to this file's parts.

- `sample(rules, ledger, seed, size)`: the rule ids of a run, a function of the bank, the ledger and the seed alone.
- `ledger_line(meta, results, rules)` and `append_ledger(path, line)`: one line of 5.1's shape, the last 60 runs kept.
- `door_faults(exchanges, packs, demo_mode)`: replays each worker turn through the door with `NoAnswer`; `report_faults`
  prints each fault as `DOOR FAULT <rule> on "<worker words>"` and gives the exit code, 1 on any (4.4).
- `play(rule, interrogator, bot)`: the rule's conversation, one worker turn at a time, against injected parts.
"""
import json
import random
import sys
from collections.abc import Callable
from itertools import accumulate
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if __name__ == "__main__":  # run as a script from the project's root: the root holds the scripts and solarchat packages
    sys.path.insert(0, str(ROOT))
from scripts.checks.bank import BANK_FOLDER  # noqa: E402
from solarchat.answer.door import answer  # noqa: E402
from solarchat.answer.stub import NoAnswer  # noqa: E402
from solarchat.leaf.contract import Reply, ReplyKind, Turn  # noqa: E402
from solarchat.packs.load import Pack  # noqa: E402

LEDGER_PATH = BANK_FOLDER / "ledger.jsonl"
WINDOW = 60
DEFAULT_SAMPLE = 40
LAST_SAMPLINGS = 5
SEVERITY_WEIGHT = {"safety": 3.0, "core": 1.5, "manner": 1.0}
VERDICTS = ("yes", "no", "unclear")
LINE_FIELDS = ("run", "date", "seed", "bot_model", "interrogator_model", "grader_model", "check_model", "bank_sha256",
               "prompt_sha256", "grader_sha256", "packs", "rules_sha256", "results", "by_family", "by_severity",
               "canaries", "agreement", "door_faults", "tokens", "cost")
DERIVED_FIELDS = ("results", "by_family", "by_severity")


def load_bank(folder: Path = BANK_FOLDER) -> list[dict]:
    """Every rule of every family file of the bank, retired ones included, ordered by id: load_bank() gives rules whose
    first id is "BR-0001"."""
    rules = [rule for path in sorted(folder.glob("*.json")) if path.name != "canaries.json"
             for rule in json.loads(path.read_text(encoding="utf-8"))["rules"]]
    return sorted(rules, key=lambda rule: rule["id"])


def read_ledger(path: Path = LEDGER_PATH) -> list[dict]:
    """The ledger's lines, oldest first; a missing file is an empty ledger: read_ledger(Path("nowhere.jsonl")) gives []."""
    if not path.is_file():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def verdict_history(ledger: list[dict]) -> dict[str, list[str]]:
    """Each rule's verdicts across the ledger, oldest first: a ledger of one run whose results hold {"BR-0001": ["no", "x"]}
    gives {"BR-0001": ["no"]}. A rule a run did not sample has no entry for it."""
    history: dict[str, list[str]] = {}
    for line in ledger:
        for rule_id, outcome in line["results"].items():
            history.setdefault(rule_id, []).append(outcome[0])
    return history


# Decision: SC-023 (design 4.1: severity x (1 + 2 x failure share over the last five samplings) x 2 when never sampled)
def weight(rule: dict, verdicts: list[str]) -> float:
    """A rule's weight: its severity's weight (safety 3, core 1.5, manner 1), times 1 plus twice its share of "no" over its
    last five samplings (an "unclear" counts as a sampling and is no failure), times 2 when it was never sampled: a core rule
    never sampled weighs 3.0; a core rule whose last two samplings were "no" and "yes" weighs 3.0; a safety rule whose
    last sampling was "no" weighs 9.0."""
    recent = verdicts[-LAST_SAMPLINGS:]
    failure_share = recent.count("no") / len(recent) if recent else 0.0
    return SEVERITY_WEIGHT[rule["severity"]] * (1 + 2 * failure_share) * (1 if recent else 2)


def draw(chooser: random.Random, pool: list[tuple[dict, float]], count: int) -> list[dict]:
    """`count` rules drawn without replacement, each draw in proportion to the weights left, in the order drawn:
    draw(random.Random(1), [({"id": "a"}, 1.0)], 5) gives [{"id": "a"}], the pool being smaller than the count."""
    left = list(pool)
    chosen: list[dict] = []
    for _ in range(min(count, len(left))):
        edges = list(accumulate(each for _, each in left))
        point = chooser.random() * edges[-1]
        index = next((place for place, edge in enumerate(edges) if point < edge), len(left) - 1)
        chosen.append(left.pop(index)[0])
    return chosen


# Decision: SC-023 (a run is a sample, repeatable from the bank, the ledger and the seed; safety first up to a quarter)
def sample(rules: list[dict], ledger: list[dict], seed: int, size: int = DEFAULT_SAMPLE,
           families: tuple[str, ...] = ()) -> list[str]:
    """The ids of the rules a run asks, in the order drawn: the active rules (of `families` when given, else of all),
    safety-severity rules first, up to size // 4 of them (all of them when the bank has fewer), then the rest of the sample
    from every rule left; `random.Random(seed)` does the drawing, so the same bank, ledger and seed give the same ids.
    A sample larger than the bank is the whole bank."""
    history = verdict_history(ledger)
    pool = sorted((rule for rule in rules if rule["status"] == "active" and (not families or rule["family"] in families)),
                  key=lambda rule: rule["id"])
    weighted = [(rule, weight(rule, history.get(rule["id"], []))) for rule in pool]
    chooser = random.Random(seed)
    first = draw(chooser, [pair for pair in weighted if pair[0]["severity"] == "safety"], size // 4)
    taken = {rule["id"] for rule in first}
    rest = draw(chooser, [pair for pair in weighted if pair[0]["id"] not in taken], size - len(first))
    return [rule["id"] for rule in first + rest]


def tally(results: dict[str, list[str]], rules: list[dict], key: str) -> dict[str, dict[str, int]]:
    """The verdicts of a run counted by a rule field, "family" or "severity": {"ask": {"yes": 1, "no": 0, "unclear": 0}}
    for one passing ask rule; every group of a sampled rule is there, each verdict counted from zero."""
    group_of = {rule["id"]: rule[key] for rule in rules}
    counts: dict[str, dict[str, int]] = {}
    for rule_id, outcome in sorted(results.items()):
        counts.setdefault(group_of[rule_id], dict.fromkeys(VERDICTS, 0))[outcome[0]] += 1
    return counts


# Decision: SC-023 (design 5.1: one line per run, with the fields of 5.1)
def ledger_line(meta: dict, results: dict[str, list[str]], rules: list[dict]) -> dict:
    """One ledger line: `meta` holds every field of 5.1 but `results`, `by_family` and `by_severity`, which are made from
    `results` ({"BR-0042": ["no", "asked nothing; gave step-06 at once"]}) and the bank; a missing or unknown field, an
    unknown rule or a verdict that is not yes, no or unclear raises ValueError naming it."""
    wanted = [name for name in LINE_FIELDS if name not in DERIVED_FIELDS]
    missing = [name for name in wanted if name not in meta]
    unknown = [name for name in meta if name not in wanted]
    if missing or unknown:
        raise ValueError(f"the ledger line lacks {missing or 'nothing'} and has unknown {unknown or 'nothing'}")
    known = {rule["id"] for rule in rules}
    for rule_id, outcome in results.items():
        if rule_id not in known or len(outcome) != 2 or outcome[0] not in VERDICTS:
            raise ValueError(f"{rule_id}: a result is [verdict, reason] for a rule of the bank, the verdict yes, no or unclear")
    return dict(meta, results=results, by_family=tally(results, rules, "family"), by_severity=tally(results, rules, "severity"))


def ledger_text(ledger: list[dict]) -> str:
    """The ledger as the file holds it: one sorted-key JSON object per line, the last WINDOW lines, a newline at the end."""
    return "".join(json.dumps(line, sort_keys=True, ensure_ascii=False) + "\n" for line in ledger[-WINDOW:])


# Decision: SC-023 (the ledger is a window of the last 60 runs; git keeps the older lines, J-051)
def append_ledger(path: Path, line: dict) -> int:
    """Append one run's line to the ledger file and drop all but the last 60 lines; gives the lines now in the file. The
    line is written as given: build it with ledger_line."""
    ledger = read_ledger(path) + [line]
    path.write_text(ledger_text(ledger), encoding="utf-8")
    return min(len(ledger), WINDOW)


@dataclass(frozen=True)
class Fault:
    """A door fault: the rule the door's fixed rules fire on the worker's words, and those words."""

    rule: str
    words: str


def replay_reply(words: str, packs: tuple[Pack, ...], demo_mode: bool) -> Reply:
    """The door's reply to the worker's words with `NoAnswer`, the deterministic layer alone: replay_reply("", (), True) is
    "I do not know"."""
    return answer(words, packs, demo_mode, NoAnswer())


# Decision: SC-023 (design 4.4: the door fault is the one red; the same deterministic code must agree with itself)
def door_faults(exchanges: list[tuple[str, Reply]], packs: tuple[Pack, ...], demo_mode: bool,
                replay: Callable[[str, tuple[Pack, ...], bool], Reply] = replay_reply) -> list[Fault]:
    """One fault for each exchange (the worker's words, the bot's live reply) whose replay through the door with `NoAnswer`
    is a stop or an emergency naming a rule that the live reply does not carry. A replay that gives no stop is no
    expectation, so the live reply may be anything, a rule fired by its cited passage included. Since TODO 1.10 the door
    reads the worker's words, so a replay with `NoAnswer` is a stop or an emergency whenever the words fire one, and a
    live reply that does not carry that rule is a fault."""
    faults = []
    for words, live in exchanges:
        expected = replay(words, packs, demo_mode)
        if expected.kind is ReplyKind.STOP and expected.safety_rule_id and live.safety_rule_id != expected.safety_rule_id:
            faults.append(Fault(expected.safety_rule_id, words))
    return faults


def report_faults(faults: list[Fault]) -> int:
    """Print `DOOR FAULT <rule> on "<worker words>"` for each fault and give the exit code, 1 with any and 0 with none."""
    for fault in faults:
        print(f'DOOR FAULT {fault.rule} on "{fault.words}"')
    return 1 if faults else 0


def play(rule: dict, interrogator: Callable[[dict, list[Turn]], str], bot: Callable[[str, tuple[Turn, ...]], Reply]) -> list[tuple[str, Reply]]:
    """The rule's conversation: exactly len(turns) worker turns, each written by `interrogator(rule, turns so far)` and
    answered by `bot(worker words, history)`; gives (worker words, reply) for each. The interrogator is given the rule
    and the transcript so far, never the bot's system prompt, and the bot only the worker's words and the history."""
    transcript: list[Turn] = []
    exchanges: list[tuple[str, Reply]] = []
    for _ in rule["turns"]:
        words = interrogator(rule, list(transcript))
        reply = bot(words, tuple(transcript))
        transcript += [Turn("user", words), Turn("assistant", reply.text)]
        exchanges.append((words, reply))
    return exchanges
