"""The opening of docs/GHOST-IN-THE-KERNEL.md is Ghost's manifesto, word for word: it may not drift (Ghost,
2026-11-21, J-023). The opening runs from the first line through the signature line `*The Ghost in The Kernel*`; the
sections after it are this project's own and are not held here. To change the opening on Ghost's word, change the text
and the hash together, citing his word in the commit."""
import hashlib
import unittest

from test.support import ROOT

SIGNATURE_LINE = "*The Ghost in The Kernel*"
MANIFESTO_SHA256 = "8cb514c4d4c2d6aa0b7aceb6bddb5e2c1468d1fe1177b40cf8bbc74a10be4f8e"


def manifesto_opening(document_text: str) -> str:
    """The document's text from its first line through the signature line and the blank line after it, e.g. the
    manifesto alone; the whole text when the signature is missing, so the hash fails rather than the test erroring."""
    signature_at = document_text.find(SIGNATURE_LINE)
    if signature_at < 0:
        return document_text
    return document_text[: signature_at + len(SIGNATURE_LINE)] + "\n\n"


def opening_digest(document_text: str) -> str:
    """The SHA-256 of the manifesto opening of a document's text, as hex."""
    return hashlib.sha256(manifesto_opening(document_text).encode("utf-8")).hexdigest()


class TheManifesto(unittest.TestCase):
    def test_the_opening_is_ghost_s_text_word_for_word(self) -> None:
        document_text = (ROOT / "docs" / "GHOST-IN-THE-KERNEL.md").read_text(encoding="utf-8")
        self.assertEqual(opening_digest(document_text), MANIFESTO_SHA256)

    def test_a_changed_word_is_caught(self) -> None:
        document_text = (ROOT / "docs" / "GHOST-IN-THE-KERNEL.md").read_text(encoding="utf-8")
        changed_text = document_text.replace("People leave.", "People stay.", 1)
        self.assertNotEqual(opening_digest(changed_text), MANIFESTO_SHA256)

    def test_the_project_s_own_sections_are_not_held(self) -> None:
        document_text = (ROOT / "docs" / "GHOST-IN-THE-KERNEL.md").read_text(encoding="utf-8")
        self.assertEqual(opening_digest(document_text + "\nA later line.\n"), MANIFESTO_SHA256)
