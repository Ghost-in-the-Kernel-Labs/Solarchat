"""Writes docs/SAFETY-RULES.md, the safety rules as Ghost reads them, from solarchat/safety/rules.json (TODO 1.3, HAD-04).

The data is the one source of truth; this document is generated from it through the safety module's own loader, so the
two cannot disagree. It opens by saying the site's own safety procedures come first and that the rules sit outside
every pack, then lists each rule's id, title, when it applies, the words the worker is shown, its response (SC-015), its latest change (SC-016), its sources, and any
point marked "Engineer to confirm".

Run: python3 -I scripts/safety_rules_doc.py          (writes the document)
     python3 -I scripts/safety_rules_doc.py --check  (exit 1 when the document is stale; test/test_safety.py uses it)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from solarchat.leaf.contract import SafetyRule  # noqa: E402
from solarchat.safety.rules import load_rules  # noqa: E402

HEADER = (
    "# The safety rules, version 1\n\n"
    "Written by `scripts/safety_rules_doc.py` from `solarchat/safety/rules.json`; do not edit here: change the data "
    "and run the script.\n\n"
    "**The site's own safety procedures come first.** These rules never replace the site's procedures, permits, "
    "training, the equipment maker's instructions or the site supervisor's instructions. Where they differ, the site "
    "wins, and the worker stops and asks (SR-01).\n\n"
    "**The rules sit outside every pack.** They are Solarchat's own text, kept in the `safety` module, never in a "
    "knowledge pack. They apply in every mode. A pack may add more places to stop; it cannot name, remove, reword or "
    "switch off a rule, and the pack check refuses a pack that tries (`docs/CONTRACT.md` HAD-04, `docs/ROADMAP.md` "
    "P-17).\n\n"
    "They are written for the newest contractor on a site (F-01): short, plain words for a phone and a tired person "
    "(P-18). When one applies, Hadley gives the rule's response (SC-015): a **warn** shows the words below and the walk "
    "continues, a **stop** shows them with why, the safe next action and what to bring the supervisor, an **emergency** "
    "tells the worker to step back and call for help. Each rule's triggers are the words that, found in a step's text, "
    "make it apply; the walker uses them from TODO 1.7. Each rule's latest change is shown (SC-016); a point marked "
    "**Engineer to confirm** waits for the engineer's final review (F-16), and an entry whose role is not an electrical "
    "engineer is Ghost's or the agent's judgement, pending that review.\n\n"
    "Status: a draft for Ghost to read (TODO 1.3 stays open until Ghost has read it). The sources are public guidance the rules "
    "rest on; no rule claims more than its sources say, and none is a substitute for training.\n\n"
)


# Decision: SC-016 (the document shows each rule's latest change, so a reader sees who last judged it and in what role)
def change_line(rule: SafetyRule) -> str:
    """The rule's latest change as one line: "2026-11-21, Ghost (maintainer): <why> Evidence: <evidence>."; a role that is
    not an electrical engineer ends with " Pending engineer."."""
    latest = rule.changes[-1]
    pending = "" if latest.role == "electrical engineer" else " Pending engineer."
    return f"{latest.date}, {latest.by} ({latest.role}): {latest.why.rstrip('.')}. Evidence: {latest.evidence}.{pending}"


def rule_section(rule: SafetyRule) -> str:
    """One rule as a Markdown section: its heading "## SR-01 The site's own ...", then when it applies, the words shown
    as a quote, its response, its triggers, its latest change, its sources as links, and an "Engineer to confirm"
    line when it has one."""
    source_lines = "\n".join(f"- [{source.title}]({source.url})" for source in rule.sources)
    trigger_list = ", ".join(f"`{trigger}`" for trigger in rule.triggers)
    confirm_line = f"\n**Engineer to confirm:** {rule.engineer_to_confirm}\n" if rule.engineer_to_confirm else ""
    return (f"## {rule.rule_id} {rule.title}\n\n"
            f"**When it applies:** {rule.applies_when}\n\n"
            f"**The worker is shown:**\n\n> {rule.words_shown}\n\n"
            f"**Response:** {rule.response}\n\n"
            f"**Triggers:** {trigger_list}\n\n"
            f"**Latest change:** {change_line(rule)}\n\n"
            f"**Sources:**\n\n{source_lines}\n{confirm_line}\n")


def render(rules: tuple[SafetyRule, ...]) -> str:
    """The document's text: the header, a one-line list of the rules, then one section per rule."""
    rule_index = "\n".join(f"- {rule.rule_id} {rule.title}" for rule in rules)
    return HEADER + f"## The rules at a glance\n\n{rule_index}\n\n" + "".join(rule_section(rule) for rule in rules).rstrip("\n") + "\n"


def main(arguments: list[str]) -> int:
    """Writes the document, or with --check compares it: 0 when current, 1 when stale."""
    document_path = Path(__file__).resolve().parent.parent / "docs" / "SAFETY-RULES.md"
    wanted_text = render(load_rules())
    if "--check" in arguments:
        is_current = document_path.exists() and document_path.read_text(encoding="utf-8") == wanted_text
        print("SAFETY-RULES.md is current" if is_current else "SAFETY-RULES.md is stale: run scripts/safety_rules_doc.py")
        return 0 if is_current else 1
    document_path.write_text(wanted_text, encoding="utf-8")
    print(f"wrote {document_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
