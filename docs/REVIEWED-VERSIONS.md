# Reviewed versions: the record of every dependency update

One row per update read in by `docs/DEPENDENCY-REVIEW.md` (C-035). "From" is the last version the
project reviewed before this one, so the next review reads the whole range from "To". Verdict is the
reviewer's (SAFE, UNSAFE, UNSURE); Reputation is CLEAN or CONCERN; Decision is `automatic`, or
`Ghost: <the question, and the answer>`; a large bundled package says `large-bundle` in Notes.
`test/test_reviewed_versions.py` holds the shape, and `scripts/checks/dependency_review.py` fails the
fast loop on any pin with no row (a lockfile entry, a workflow's action, a Dockerfile's image digest, a
vendored manifest's row). On adoption every pin already held gets an `unreviewed baseline` row (Kind
`baseline`, From, Verdict and Reputation `—`): the pin is the first review's old side, taken as held
and not as read. The workflow's action and the Java starter's image are Ghost-Core's baseline rows, carried by the stamp
(Solarchat has no Dockerfile). The founding lockfile's pins are baseline rows (J-004); the rows for click, coverage,
libcst, mutmut and their dependencies stay as the record after the mutation run was removed (SC-008) and the lock no
longer holds them. The Anthropic SDK and the 15 packages it brought are `new` rows, each read in full (J-045, SC-021).

| Date | Package | From | To | Kind | Verdict | Reputation | Decision | Journal | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-11-07 | actions/checkout | — | 11d5960a326750d5838078e36cf38b85af677262 | baseline | — | — | unreviewed baseline | J-071 | v4.4.0, pinned in the workflow before the record; the first review reads from this pin |
| 2026-11-07 | gradle:8.14.3-jdk21-noble | — | sha256:21bd311ed01360c189b8870c6b6e988199ff10f72d445d02fb39d3cff9da91d7 | baseline | — | — | unreviewed baseline | J-071 | the Java starter's image, pinned before the record; the first review reads from this pin |
| 2026-11-20 | click | — | 8.5.1 | baseline | — | — | unreviewed baseline | J-004 | pinned in requirements.lock before the record; the first review reads from this pin |
| 2026-11-20 | coverage | — | 7.17.3 | baseline | — | — | unreviewed baseline | J-004 | pinned in requirements.lock before the record; the first review reads from this pin |
| 2026-11-20 | iniconfig | — | 2.3.1 | baseline | — | — | unreviewed baseline | J-004 | pinned in requirements.lock before the record; the first review reads from this pin |
| 2026-11-20 | libcst | — | 1.9.0 | baseline | — | — | unreviewed baseline | J-004 | pinned in requirements.lock before the record; the first review reads from this pin |
| 2026-11-20 | linkify-it-py | — | 2.2.0 | baseline | — | — | unreviewed baseline | J-004 | pinned in requirements.lock before the record; the first review reads from this pin |
| 2026-11-20 | markdown-it-py | — | 4.3.0 | baseline | — | — | unreviewed baseline | J-004 | pinned in requirements.lock before the record; the first review reads from this pin |
| 2026-11-20 | mdit-py-plugins | — | 0.7.0 | baseline | — | — | unreviewed baseline | J-004 | pinned in requirements.lock before the record; the first review reads from this pin |
| 2026-11-20 | mdurl | — | 0.1.2 | baseline | — | — | unreviewed baseline | J-004 | pinned in requirements.lock before the record; the first review reads from this pin |
| 2026-11-20 | mutmut | — | 3.8.1 | baseline | — | — | unreviewed baseline | J-004 | pinned in requirements.lock before the record; the first review reads from this pin |
| 2026-11-20 | packaging | — | 26.3 | baseline | — | — | unreviewed baseline | J-004 | pinned in requirements.lock before the record; the first review reads from this pin |
| 2026-11-20 | platformdirs | — | 4.14.5 | baseline | — | — | unreviewed baseline | J-004 | pinned in requirements.lock before the record; the first review reads from this pin |
| 2026-11-20 | pluggy | — | 1.7.0 | baseline | — | — | unreviewed baseline | J-004 | pinned in requirements.lock before the record; the first review reads from this pin |
| 2026-11-20 | pygments | — | 2.21.0 | baseline | — | — | unreviewed baseline | J-004 | pinned in requirements.lock before the record; the first review reads from this pin |
| 2026-11-20 | pytest | — | 9.2.0 | baseline | — | — | unreviewed baseline | J-004 | pinned in requirements.lock before the record; the first review reads from this pin |
| 2026-11-20 | pyyaml | — | 6.0.3 | baseline | — | — | unreviewed baseline | J-004 | pinned in requirements.lock before the record; the first review reads from this pin |
| 2026-11-20 | rich | — | 15.0.0 | baseline | — | — | unreviewed baseline | J-004 | pinned in requirements.lock before the record; the first review reads from this pin |
| 2026-11-20 | ruff | — | 0.17.5 | baseline | — | — | unreviewed baseline | J-004 | pinned in requirements.lock before the record; the first review reads from this pin |
| 2026-11-20 | setproctitle | — | 1.3.8 | baseline | — | — | unreviewed baseline | J-004 | pinned in requirements.lock before the record; the first review reads from this pin |
| 2026-11-20 | textual | — | 8.2.8 | baseline | — | — | unreviewed baseline | J-004 | pinned in requirements.lock before the record; the first review reads from this pin |
| 2026-11-20 | typing-extensions | — | 4.16.0 | baseline | — | — | unreviewed baseline | J-004 | pinned in requirements.lock before the record; the first review reads from this pin |
| 2026-11-21 | annotated-types | — | 0.8.0 | new | SAFE | CLEAN | Ghost: approved 2026-11-21 in chat | J-045 | new, transitive |
| 2026-11-21 | anthropic | — | 2.8.0 | new | SAFE | CLEAN | Ghost: approved 2026-11-21 in chat | J-045 | new dependency, direct (SC-021); whole package read; the `exec` is the opt-in agent toolset's bash session, not imported by Solarchat; no PyPI attestation to compare |
| 2026-11-21 | anyio | — | 4.16.0 | new | SAFE | CLEAN | Ghost: approved 2026-11-21 in chat | J-045 | new, transitive |
| 2026-11-23 | colorama | — | 0.4.6 | new | SAFE | CONCERN | Ghost: approved 2026-11-23 in chat ("Add colorama (Recommended)"; the CONCERN: "Land it (Recommended)") | J-083 | new, transitive via pytest, Windows only (`sys_platform == 'win32'`); whole package read (wheel and sdist), no install hook or startup file; the CONCERN (low) is Checkmarx's 2024 report of a trojaned colorama-0.4.6.tar.gz on the lookalike domain files.pypihosted.org, not PyPI, which does not apply: the lock's hashes match pypi.org's; no PyPI attestation to compare |
| 2026-11-21 | docstring-parser | — | 0.18.0 | new | SAFE | CLEAN | Ghost: approved 2026-11-21 in chat | J-045 | new, transitive |
| 2026-11-21 | h11 | — | 0.16.0 | new | SAFE | CLEAN | Ghost: approved 2026-11-21 in chat | J-045 | new, transitive |
| 2026-11-21 | httpcore2 | — | 2.16.0 | new | SAFE | CLEAN | Ghost: approved 2026-11-21 in chat | J-045 | new, through httpx2; CVE-2026-84381 fixed before 2.16.0; no PyPI attestation to compare |
| 2026-11-21 | httpx2 | — | 2.16.0 | new | SAFE | CLEAN | Ghost: approved 2026-11-21 in chat | J-045 | new, through anthropic; the pydantic project's fork of httpx; its `_alias.py` import hook runs only if called; CVE-2026-84378, -84379, -84380, -84382 fixed before 2.16.0; no PyPI attestation to compare |
| 2026-11-21 | idna | — | 3.20 | new | SAFE | CLEAN | Ghost: approved 2026-11-21 in chat | J-045 | new, transitive |
| 2026-11-21 | jiter | — | 0.19.0 | new | SAFE | CLEAN | Ghost: approved 2026-11-21 in chat | J-045 | new, through anthropic; the compiled .so was not read, the wheel was fetched against the lock's PyPI hash |
| 2026-11-21 | opentelemetry-api | — | 1.45.2 | new | SAFE | CLEAN | Ghost: approved 2026-11-21 in chat | J-045 | new, transitive |
| 2026-11-21 | pydantic | — | 2.14.3 | new | SAFE | CLEAN | Ghost: approved 2026-11-21 in chat | J-045 | new, transitive |
| 2026-11-21 | pydantic-core | — | 2.50.4 | new | SAFE | CLEAN | Ghost: approved 2026-11-21 in chat | J-045 | new, through pydantic; the compiled .so was not read, the wheel was fetched against the lock's PyPI hash |
| 2026-11-21 | sniffio | — | 1.3.1 | new | SAFE | CLEAN | Ghost: approved 2026-11-21 in chat | J-045 | new, transitive |
| 2026-11-21 | truststore | — | 0.10.5 | new | SAFE | CLEAN | Ghost: approved 2026-11-21 in chat | J-045 | new, transitive |
| 2026-11-21 | typing-inspection | — | 0.4.5 | new | SAFE | CLEAN | Ghost: approved 2026-11-21 in chat | J-045 | new, transitive |
