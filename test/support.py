"""What every doc test shares: the repository root, and a scratch root a planted break is built in."""
import contextlib
import os
import tempfile
from unittest import mock
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BROKEN = ROOT / "test" / "fixtures" / "broken"


def scratch() -> Path:
    """A fresh empty directory with a docs/ folder, e.g. /tmp/ghost-core-abc123."""
    root = Path(tempfile.mkdtemp(prefix="ghost-core-"))
    (root / "docs").mkdir()
    return root


@contextlib.contextmanager
def no_key():
    """No key anywhere: ANTHROPIC_API_KEY empty and the config folder an empty temporary one, so a developer's stored key
    never changes a result (SC-022 6): `with no_key(): ...` yields the folder."""
    with tempfile.TemporaryDirectory() as folder, mock.patch.dict(os.environ, {"ANTHROPIC_API_KEY": "", "SOLARCHAT_CONFIG_DIR": folder}):
        yield folder
