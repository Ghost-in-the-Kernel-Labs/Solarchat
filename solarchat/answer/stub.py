"""The offline answerer until TODO 1.8's keyword search replaces it: it never finds anything (SC-019)."""
from solarchat.leaf.contract import Finding, Passage


class NoAnswer:
    """The answerer that always says "I do not know": NoAnswer().find("Where is the Voc?", ()) gives Finding().

    Decision: SC-019 (the stub runs the door and the runner end to end on day one; its score is the floor a search must beat).
    """

    name = "no-answer"

    def find(self, question: str, passages: tuple[Passage, ...]) -> Finding:
        """An empty finding for every question: NoAnswer().find("anything", ()) gives Finding()."""
        return Finding()
