"""The key commands: store a key, forget it, or ask whether one is set, and say so without ever showing it (TODO 2.5; SC-022 point 6).

The orchestrator for `solarchat --key` and `solarchat --forget-key`: the storing is the model module's (MOD-02).
Decision: SC-022 (6).
"""
import os
import sys
from typing import TextIO

from solarchat.model.key import forget_key, key_path, resolve_key, save_key

ASK = "Type or paste your Anthropic key and press Enter (it is shown as you type, and never saved in shell history): "


def store_key_command(value: str, stdout: TextIO, stderr: TextIO, stdin: TextIO | None = None) -> int:
    """Store the key and return the exit code (0 saved, 2 refused). A value of "" reads the key from a line of `stdin`
    (visible, so a paste can be seen; TODO 2.11, Ghost 2026-11-23); the output says that a key was saved and where, and
    never the key."""
    try:
        if value:
            key = value
        else:
            stdout.write(ASK)
            stdout.flush()
            key = (stdin or sys.stdin).readline()
        path = save_key(key)
    except (ValueError, OSError) as problem:
        stderr.write(f"solarchat: the key was not saved: {problem}\n")
        return 2
    stdout.write(f"\nKey saved in {path}. It stays on this computer; `solarchat --forget-key` removes it.\n")
    return 0


def ensure_key(stdin: TextIO, stdout: TextIO, stderr: TextIO) -> bool:
    """When no key is set, ask for one right here and store it (TODO 2.11): True when a key is set afterwards. An empty
    line or a refused folder leaves it unset (the caller then exits 2 naming `solarchat --key`)."""
    try:
        if resolve_key():
            return True
    except (ValueError, OSError):
        return False
    stdout.write("No Anthropic key is set yet.\n")
    return store_key_command("", stdout, stderr, stdin) == 0


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


def has_key_command(stdout: TextIO, stderr: TextIO) -> int:
    """Say whether a key would be found, never which: 0 when ANTHROPIC_API_KEY is set or a key is stored, 1 when none is,
    2 when the folder is refused. The setup script asks this before it asks for the key (TODO 2.11)."""
    try:
        found = resolve_key()
        path = key_path()
    except (ValueError, OSError) as problem:
        stderr.write(f"solarchat: the key could not be looked for: {problem}\n")
        return 2
    if not found:
        stdout.write("No key is set; run solarchat --key.\n")
        return 1
    stdout.write("A key is set (from ANTHROPIC_API_KEY).\n" if os.environ.get("ANTHROPIC_API_KEY") else f"A key is stored in {path}.\n")
    return 0
