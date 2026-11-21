"""Make a worker clone's `.venv/` a real directory of symlinks to this checkout's own `.venv/` entries (C-036).

Run: python3 -I scripts/worker_venv.py /path/to/clone
     python3 -I scripts/worker_venv.py --help     prints this and does nothing else

The clone gets `.venv/` as a real directory holding one symlink per entry of this checkout's `.venv/` (the repository
root of this script). Never a symlink to `.venv` itself: the gitignore rule `/.venv/` does not match a symlink, so the
gate would record it and `scripts/commit.sh` would refuse. It refuses, changing nothing, when this checkout's `.venv/`
is missing, when the clone is this checkout, when the clone is not a folder, and when the clone's `.venv` already exists
and is not already such a directory of the same links (one that is, is left as it is and the exit code is 0).
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def wanted_links(source: Path) -> dict[str, str]:
    """The link each entry of the source venv should have: a source holding `bin` gives {"bin": "<source>/bin"}."""
    return {entry.name: str(entry) for entry in sorted(source.iterdir())}


def current_links(target: Path) -> dict[str, str] | None:
    """The links of a real directory by name, or None when it is a symlink, a file, or holds anything that is not a link:
    an empty real folder gives {}."""
    if target.is_symlink() or not target.is_dir():
        return None
    entries = sorted(target.iterdir())
    if not all(entry.is_symlink() for entry in entries):
        return None
    return {entry.name: str(entry.readlink()) for entry in entries}


def refusal(clone: Path, source: Path, root: Path) -> str | None:
    """Why the clone cannot be given a `.venv`, or None when it can: a clone that is the root gives a refusal."""
    if not source.is_dir() or source.is_symlink():
        return f"{source} is not a real directory; build the shared venv first (docs/when/coordinate.md)"
    if clone.resolve() == root.resolve():
        return f"{clone} is this checkout itself; run it on a worker's clone"
    if not clone.is_dir():
        return f"{clone} is not a folder"
    target = clone / ".venv"
    if (target.exists() or target.is_symlink()) and current_links(target) != wanted_links(source):
        return f"{target} exists and is not a directory of links to {source}; remove it yourself first"
    return None


def make_venv(clone: Path, source: Path) -> bool:
    """Make clone/.venv a real directory with one link per source entry; True when it made it, False when it was there:
    make_venv(Path("/work/clone"), Path("/main/.venv")) links /work/clone/.venv/bin to /main/.venv/bin."""
    target = clone / ".venv"
    if target.exists():
        return False
    target.mkdir()
    for name, destination in wanted_links(source).items():
        (target / name).symlink_to(destination)
    return True


def main(argv: list[str], root: Path = ROOT) -> int:
    """The command: main(["/work/clone"]) links the clone; a refusal is one line on stderr and exit code 1."""
    if "-h" in argv or "--help" in argv:
        print(__doc__.strip())
        return 0
    if len(argv) != 1:
        print("usage: worker_venv.py <clone>   (--help says more)", file=sys.stderr)
        return 2
    clone, source = Path(argv[0]), root / ".venv"
    problem = refusal(clone, source, root)
    if problem:
        print(f"worker_venv: {problem}", file=sys.stderr)
        return 1
    print(f"{clone / '.venv'}: {'made' if make_venv(clone, source) else 'already in place'}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
