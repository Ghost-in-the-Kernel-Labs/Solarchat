# Findings: what the project's checks prove, written before the result they qualify

A finding is a flaw this repository's own checks prove in an existing tool, metric, document or
practice, with the evidence that proves it (C-014). Not a bug list for this codebase (a bug is a
journal entry of class failure-caught and a test) and not an opinion. Ids are never reused; a
resolved finding is marked, never deleted. A result that depends on a finding cites it.

| Id | Finding | Evidence | Qualifies | Status |
| --- | --- | --- | --- | --- |
| F-001 | Ghost-Core's stamp asks for `docs/CONTRACT.md` to be renamed (its STAMP comment; TODO 0.4's check), but `test/test_contract.py` reads the contract by that exact path, so a renamed contract fails the fast loop. Spellfire Game met the same (its F-04). | `test/test_contract.py`, `test_the_contract_is_numbered` and the test after it open `ROOT / "docs" / "CONTRACT.md"` | TODO 0.4's check (the contract keeps its name); the fix is Ghost-Core's: the test reads the path from `docs/modules.json`, or the STAMP comment stops asking for a rename | open |
