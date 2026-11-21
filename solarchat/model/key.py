"""The local key: where a developer's own machine keeps the model key, and how it is found (SC-022 point 6).

The file is `key` in the user's config folder (`%APPDATA%\\solarchat` on Windows, `~/.config/solarchat` elsewhere; the
variable SOLARCHAT_CONFIG_DIR points it elsewhere, for tests). The folder may never be inside this repository, the file
is readable only by its owner where the system allows, and no function here returns the key to anything that prints it.
Decision: SC-022 (6).
"""
import os
from pathlib import Path

CONFIG_VARIABLE = "SOLARCHAT_CONFIG_DIR"
KEY_VARIABLE = "ANTHROPIC_API_KEY"
KEY_FILE = "key"
REPOSITORY = Path(__file__).resolve().parents[2]


def config_dir(environ: dict[str, str] | None = None) -> Path:
    """The config folder: config_dir({"SOLARCHAT_CONFIG_DIR": "/x"}) gives Path("/x"); a folder inside the repository
    raises ValueError in words."""
    env = os.environ if environ is None else environ
    if env.get(CONFIG_VARIABLE):
        folder = Path(env[CONFIG_VARIABLE])
    elif os.name == "nt":
        folder = Path(env.get("APPDATA") or Path.home() / "AppData" / "Roaming") / "solarchat"
    else:
        folder = Path(env.get("XDG_CONFIG_HOME") or Path.home() / ".config") / "solarchat"
    folder = folder.expanduser().resolve()
    if folder == REPOSITORY or REPOSITORY in folder.parents:
        raise ValueError("the key folder is inside the repository; point SOLARCHAT_CONFIG_DIR outside it")
    return folder


def key_path(environ: dict[str, str] | None = None) -> Path:
    """The key file's path: key_path({"SOLARCHAT_CONFIG_DIR": "/x"}) gives Path("/x/key")."""
    return config_dir(environ) / KEY_FILE


def save_key(key: str, environ: dict[str, str] | None = None) -> Path:
    """Store the key, owner-only, and return the file's path; an empty key or one with whitespace in it raises ValueError."""
    key = key.strip()
    if not key or any(c.isspace() for c in key):
        raise ValueError("the key is empty or has spaces in it")
    path = key_path(environ)
    path.parent.mkdir(parents=True, exist_ok=True)
    if os.name != "nt":
        os.chmod(path.parent, 0o700)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
        handle.write(key + "\n")
    if os.name != "nt":
        os.chmod(path, 0o600)
    return path


def forget_key(environ: dict[str, str] | None = None) -> bool:
    """Delete the stored key: True when there was one, False when not."""
    path = key_path(environ)
    if not path.is_file():
        return False
    path.unlink()
    return True


def stored_key(environ: dict[str, str] | None = None) -> str | None:
    """The stored key, or None when there is none or the folder is refused."""
    try:
        path = key_path(environ)
        return path.read_text(encoding="utf-8").strip() or None if path.is_file() else None
    except (ValueError, OSError):
        return None


def resolve_key(environ: dict[str, str] | None = None) -> str | None:
    """The key to use: ANTHROPIC_API_KEY when set, else the stored key, else None."""
    env = os.environ if environ is None else environ
    return env.get(KEY_VARIABLE) or stored_key(environ)
