"""Writes docs/DIRECTIVE-MAP.md: every directive (each decision of theGhost.md and each invariant of docs/CONTRACT.md)
with the functions that hold it, so a human reviewer can go from a rule to its code and back (SC-011).

A function holds a directive when it cites it, either on comment lines directly above its `def` (or its decorators),
`# Decision: SC-005 (why)` or `# Invariant: HAD-06 (why)`, or on a line of its docstring that starts `Invariant:` or
`Decision:`. A module's own docstring citation names the module, and a shell script's `# Decision:` line names the
script, since neither has a function to point at. A directive no function cites is listed too, with "no function": it is held by a document, a test or a
review, as its own Held by line says.

Run: python3 -I scripts/directive_map.py          (writes the map)
     python3 -I scripts/directive_map.py --check  (exit 1 when the map is stale; test/test_directive_map.py uses it)
"""
import ast
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scripts.checks import contract, ghost  # noqa: E402
from scripts.checks.common import tracked_files  # noqa: E402

CODE_FOLDERS: tuple[str, ...] = ("solarchat", "scripts")
PLANTED_BREAKS_FOLDER = "test/fixtures/"
CITATION_LINE = re.compile(r"^\s*#\s*(?:Decision|Invariant):\s*(.*)$")
SHELL_CITATION = re.compile(r"#\s*(?:Decision|Invariant):\s*(.*)$")
DOCSTRING_CITATION_LINE = re.compile(r"^\s*(?:Decision|Invariant):\s*(.*)$")
DIRECTIVE_ID = re.compile(r"\b(?:C-\d{3}|SC-\d{3}|HAD-\d{2})\b")
HEADER = ("# Directive map: each rule, and the functions that hold it\n\n"
          "Written by `scripts/directive_map.py` from `theGhost.md`, `docs/CONTRACT.md` and the code's citations; do not "
          "edit here. A function holds a directive when it cites it: `# Decision: SC-005 (why)` or `# Invariant: HAD-06 "
          "(why)` directly above its `def`, or an `Invariant:` line in its docstring (SC-011). \"No function\" means the "
          "directive is held by a document, a test or a review: its Held by line in `theGhost.md` or `docs/CONTRACT.md` "
          "says which.\n\n")


def cited_ids(citation_text: str) -> list[str]:
    """The directive ids a citation names before its reason: "C-008, C-012 (a change ...)" gives ["C-008", "C-012"]."""
    ids_part = citation_text.split("(", 1)[0]
    return DIRECTIVE_ID.findall(ids_part)


def comment_citations(source_lines: list[str], first_line_number: int) -> list[str]:
    """The ids on the run of comment lines directly above line `first_line_number` (1-based): a function whose `def`
    follows "# Decision: SC-007 (why)" gives ["SC-007"]."""
    found_ids: list[str] = []
    line_index = first_line_number - 2
    while line_index >= 0 and source_lines[line_index].lstrip().startswith("#"):
        citation = CITATION_LINE.match(source_lines[line_index])
        if citation:
            found_ids = cited_ids(citation.group(1)) + found_ids
        line_index -= 1
    return found_ids


def docstring_citations(function_node: ast.FunctionDef | ast.ClassDef) -> list[str]:
    """The ids on docstring lines that start "Invariant:" or "Decision:": "Invariant: HAD-03 (...)" gives ["HAD-03"]."""
    docstring = ast.get_docstring(function_node) or ""
    found_ids: list[str] = []
    for docstring_line in docstring.splitlines():
        citation = DOCSTRING_CITATION_LINE.match(docstring_line)
        if citation:
            found_ids += cited_ids(citation.group(1))
    return found_ids


def holders_in_file(relative_path: str, source_text: str) -> dict[str, list[str]]:
    """Each directive id cited in one Python file, with the functions and classes that cite it, as "file:name"."""
    source_lines = source_text.splitlines()
    holders: dict[str, list[str]] = {}
    for node in ast.walk(ast.parse(source_text)):
        if not isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            continue
        first_line_number = min([node.lineno] + [decorator.lineno for decorator in node.decorator_list])
        for directive_id in comment_citations(source_lines, first_line_number) + docstring_citations(node):
            holder = f"`{relative_path}:{node.name}`"
            if holder not in holders.setdefault(directive_id, []):
                holders[directive_id].append(holder)
    return holders


def module_holders(relative_path: str, source_text: str) -> dict[str, list[str]]:
    """The ids a file cites as a whole: a Python module's docstring citations, or a shell script's `# Decision:` lines;
    each names the file itself, e.g. {"SC-009": ["`scripts/commit.sh`"]}."""
    if relative_path.endswith(".py"):
        module_docstring = ast.get_docstring(ast.parse(source_text)) or ""
        citations = [DOCSTRING_CITATION_LINE.match(line) for line in module_docstring.splitlines()]
    else:
        citations = [SHELL_CITATION.search(line) for line in source_text.splitlines()]
    found_ids = [directive_id for citation in citations if citation for directive_id in cited_ids(citation.group(1))]
    return {directive_id: [f"`{relative_path}`"] for directive_id in dict.fromkeys(found_ids)}


def all_holders(root: Path) -> dict[str, list[str]]:
    """Every directive id cited in the tracked Python and shell under CODE_FOLDERS (the planted breaks excluded), with
    its holders: modules and scripts first, then functions."""
    holders: dict[str, list[str]] = {}
    for path in sorted(tracked_files(root)):
        relative_path = path.relative_to(root).as_posix()
        in_code_folder = relative_path.split("/", 1)[0] in CODE_FOLDERS
        if path.suffix not in (".py", ".sh") or not in_code_folder or relative_path.startswith(PLANTED_BREAKS_FOLDER):
            continue
        source_text = path.read_text(encoding="utf-8")
        file_holders = module_holders(relative_path, source_text)
        if path.suffix == ".py":
            for directive_id, function_holders in holders_in_file(relative_path, source_text).items():
                file_holders.setdefault(directive_id, []).extend(function_holders)
        for directive_id, each_holder in file_holders.items():
            holders.setdefault(directive_id, []).extend(each_holder)
    return holders


def directive_titles(root: Path) -> dict[str, str]:
    """Each directive id with its title, decisions first in theGhost.md's order, then the contract's invariants."""
    titles: dict[str, str] = {}
    for decision_id, entry in ghost.split_entries((root / "theGhost.md").read_text(encoding="utf-8")).items():
        titles[decision_id] = entry.split("\n", 1)[0].split(": ", 1)[1]
    contract_text = (root / "docs" / "CONTRACT.md").read_text(encoding="utf-8")
    for invariant_id in contract.invariants(contract_text):
        heading = re.search(rf"^## {invariant_id} (.*)$", contract_text, re.MULTILINE)
        titles[invariant_id] = heading.group(1) if heading else ""
    return titles


def render(root: Path) -> str:
    """The map's text: a header, a count, and one table row per directive with its holders or "no function"."""
    holders = all_holders(root)
    titles = directive_titles(root)
    rows = [f"| {directive_id} | {title} | {', '.join(holders.get(directive_id, [])) or 'no function'} |"
            for directive_id, title in titles.items()]
    held_count = sum(1 for directive_id in titles if holders.get(directive_id))
    unknown_ids = sorted(set(holders) - set(titles))
    summary = f"{held_count} of {len(titles)} directives are cited by a function.\n\n"
    unknown = f"Cited in code but not a directive: {', '.join(unknown_ids)}.\n\n" if unknown_ids else ""
    table = "| Directive | Title | Held in code by |\n| --- | --- | --- |\n" + "\n".join(rows) + "\n"
    return HEADER + summary + unknown + table


def main(arguments: list[str]) -> int:
    """Writes the map, or with --check compares it: 0 when current, 1 when stale."""
    root = Path(__file__).resolve().parent.parent
    wanted_text = render(root)
    map_path = root / "docs" / "DIRECTIVE-MAP.md"
    if "--check" in arguments:
        is_current = map_path.exists() and map_path.read_text(encoding="utf-8") == wanted_text
        print("DIRECTIVE-MAP.md is current" if is_current else "DIRECTIVE-MAP.md is stale: run scripts/directive_map.py")
        return 0 if is_current else 1
    map_path.write_text(wanted_text, encoding="utf-8")
    print(f"wrote {map_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
