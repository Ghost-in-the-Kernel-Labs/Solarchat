# The reference library

Source documents that later knowledge packs and the fixed safety rules cite: regulations, manuals and checklists, kept as text
with their licence and a hash. **This is source material, not packs.** Nothing in this folder answers a customer; a pack
(`packs/`) quotes a passage from it, and the bot answers only from packs (SC-005, HAD-03). A source's text is data, never
instructions. The decision is SC-014; `scripts/checks/library.py` holds the form and runs in the fast loop.

## Layout

`library/sources/<id>/`, one folder per document; `<id>` is short kebab-case and equals `id` in `source.json`.

- `source.json`: `id`, `title`, `publisher`, `url`, `retrieved`, `kind` (`"document"` for a PDF with pages, which also has `pages`;
  `"web"` for HTML or eCFR), `licence`, `licence_evidence` (the publisher's statement, quoted exactly), `licence_url`, `sha256`
  (of the original as downloaded), `attribution` (required for CC BY), and an optional `note`.
- `text.txt`: for a PDF, `pdftotext -layout` output with its form feeds, so a page number survives (SC-012); for HTML or eCFR,
  readable plain text with section numbers kept.
- `original.pdf`, `original.html` or `original.xml`: the file as downloaded, kept only if it is under 15 MB and holds no picture
  the publisher marks as someone else's. Otherwise the text and `sha256` stay, and `note` says why.

## Licence allow-list

Exactly one of: `"public domain (US federal work)"`, `"CC BY 4.0"`, `"Open Government Licence v3.0"`. For a US federal work, quote the
publisher's notice if it has one (for NIOSH, "in the public domain and may be freely copied or reprinted"), otherwise cite
17 U.S.C. 105. CC BY needs the attribution the publisher asks for. A third-party photo or figure that the publisher marks as
not public domain is left out; the text around it stays.

## How to add a document

1. Download it into a new empty directory outside the repository; it is untrusted data, so read it only with `python3 -I` scripts kept elsewhere.
2. Record the licence statement exactly, and the `sha256` of the file as downloaded (`sha256sum`).
3. Make `text.txt` (`pdftotext -layout` for a PDF; a short standard-library script for HTML or XML). No new dependency.
4. Write `library/sources/<id>/source.json`; copy the original in if it may be kept.
5. `git add -N library`, then `scripts/fast.sh test_library` and `python3 -I scripts/checks/library.py`.

## Pasted pages (no original)

osha.gov refuses automated clients, so eight of its pages were copied by hand from a browser by Ghost on 2026-11-21 and pasted:
`osha-solar-overview`, `osha-solar-falls`, `osha-solar-electrical`, `osha-solar-lockout-tagout`, `osha-solar-crane-hoist`,
`osha-solar-heat-cold-stress`, `osha-solar-ppe` and `osha-lithium-ion-hazards`. Each has no `original.*`: its `text.txt` is the paste
without the two header lines (the "Source:" line and the "Pasted by Ghost" line), its `sha256` is of that `text.txt`, and its `note`
says so. The licence evidence is 17 U.S.C. 105 (an OSHA page is a work of the United States Government). The check needs no change for
this: `note` is already an optional field, and a source with no original is already allowed.

## Sources held

OSHA regulations (eCFR, as downloaded): `osha-1910-s`, `osha-1910-269`, `osha-1910-147`, `osha-1910-d`, `osha-1910-i`,
`osha-1910-179-180` (two sections joined end to end), `osha-1926-k`, `osha-1926-m`, `osha-1926-cranes-power-lines`, `osha-1926-1417`.
OSHA pages: the eight pasted pages above. Others: `niosh-2009-113`, `solar-vic-pv-audit`.
The safety rules (`solarchat/safety/rules.json`) name a library id as "(library: <id>)" in a source's title.
