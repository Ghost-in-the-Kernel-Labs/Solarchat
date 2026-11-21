"""The key commands: store a key, or forget it, and say so without ever showing it (TODO 2.5; SC-022 point 6).

The orchestrator for `solarchat --key` and `solarchat --forget-key`: the storing is the model module's (MOD-02).
Decision: SC-022 (6).
"""
import getpass
from typing import Callable, TextIO

from solarchat.model.key import forget_key, key_path, save_key

ASK = "Paste the key (it is not shown): "


def store_key_command(value: str, stdout: TextIO, stderr: TextIO, ask: Callable[[str], str] = getpass.getpass) -> int:
    """Store the key and return the exit code (0 saved, 2 refused). A value of "" asks for it hidden through `ask`; the
    output says that a key was saved and where, and never the key."""
    try:
        key = value or ask(ASK)
        path = save_key(key)
    except (ValueError, OSError, EOFError) as problem:
        stderr.write(f"solarchat: the key was not saved: {problem}\n")
        return 2
    stdout.write(f"Key saved in {path}. It stays on this computer; `solarchat --forget-key` removes it.\n")
    return 0


def forget_key_command(stdout: TextIO, stderr: TextIO) -> int:
    """Delete the stored key and return the exit code (0 done, 2 the folder is refused)."""
    try:
        path = key_path()
        gone = forget_key()
    except (ValueError, OSError) as problem:
        stderr.write(f"solarchat: the key was not removed: {problem}\n")
        return 2
    stdout.write(f"Key removed from {path}.\n" if gone else f"No stored key at {path}.\n")
    return 0
