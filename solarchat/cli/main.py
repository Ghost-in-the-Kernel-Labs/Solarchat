"""The chat command's arguments, handed to project (TODO 1.16; SC-019, amended 2026-11-21). No logic of its own (MOD-02)."""
import argparse
import sys
from typing import TextIO

from solarchat.project.chat import start_chat


def build_parser() -> argparse.ArgumentParser:
    """The command line: build_parser().parse_args(["--pack", "packs/x", "--demo"]).answerer gives "claude"."""
    parser = argparse.ArgumentParser(prog="python3 -m solarchat.cli", description="Chat with Solarchat about one pack.")
    parser.add_argument("--pack", required=True, help="the pack's folder, e.g. packs/seed-mc4-leads")
    parser.add_argument("--demo", action="store_true", help="let a demo pack answer, with the demo banner on every reply")
    parser.add_argument("--answerer", choices=("claude", "stub"), default="claude")
    return parser


def main(argv: list[str], stdin: TextIO | None = None, stdout: TextIO | None = None, stderr: TextIO | None = None) -> int:
    """Run the chat and return its exit code (0 ended, 2 cannot run): main(["--pack", "p", "--answerer", "stub"], io, out, err)
    chats on `io` and `out`; streams default to the process's own."""
    try:
        args = build_parser().parse_args(argv)
    except SystemExit as stop:
        return 0 if stop.code in (0, None) else 2
    return start_chat(args.pack, args.demo, args.answerer, stdin or sys.stdin, stdout or sys.stdout, stderr or sys.stderr)
