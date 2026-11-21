"""The commands' arguments, handed to project (TODO 1.16, 2.5; SC-019, SC-022 point 6). No logic of its own (MOD-02)."""
import argparse
import sys
from typing import TextIO

from solarchat.project.chat import DEFAULT_MODEL, MODEL_CHOICES, start_chat
from solarchat.project.keys import forget_key_command, store_key_command

MENU = """solarchat: walks you through setting up and fixing your solar panels, from the manuals in a pack.

Commands:
  solarchat                 show this menu
  solarchat help            show this menu (also: solarchat --help)
  solarchat --key           store your model key, typed hidden so it stays out of shell history (the way to do it)
  solarchat --key <key>     store the key you give (it may stay in shell history)
  solarchat --forget-key    delete the stored key
  solarchat --pack <pack>   chat about one pack, e.g. solarchat --pack packs/seed-mc4-leads --demo

Chat options (with --pack):
  --demo                    let a demo pack answer, with the demo banner on every reply: solarchat --pack packs/seed-mc4-leads --demo
  --answerer claude|stub    who answers: claude (the default) or stub, which says "I do not know": solarchat --pack P --answerer stub
  --model <model>           the Claude model, claude-sonnet-5-5 (the default) or claude-haiku-5-5: solarchat --pack P --model claude-haiku-5-5

The chat uses ANTHROPIC_API_KEY when it is set, else the key stored by solarchat --key. The key is never shown or uploaded.
"""


def build_parser() -> argparse.ArgumentParser:
    """The command line: build_parser().parse_args(["--pack", "packs/x", "--demo"]).answerer gives "claude"."""
    parser = argparse.ArgumentParser(prog="solarchat", add_help=False)
    parser.add_argument("command", nargs="?", choices=("help",), help="help shows the menu")
    parser.add_argument("-h", "--help", action="store_true", help="show the menu")
    parser.add_argument("--key", nargs="?", const="", default=None, help="store the key; with no value, asked hidden")
    parser.add_argument("--forget-key", action="store_true", help="delete the stored key")
    parser.add_argument("--pack", help="the pack's folder, e.g. packs/seed-mc4-leads")
    parser.add_argument("--demo", action="store_true", help="let a demo pack answer, with the demo banner on every reply")
    parser.add_argument("--answerer", choices=("claude", "stub"), default="claude")
    parser.add_argument("--model", choices=MODEL_CHOICES, default=DEFAULT_MODEL, help="the Claude model (claude-sonnet-5-5 unless testing)")
    return parser


def main(argv: list[str], stdin: TextIO | None = None, stdout: TextIO | None = None, stderr: TextIO | None = None) -> int:
    """Run a command and return its exit code (0 done, 2 cannot run): main(["--pack", "p", "--answerer", "stub"], io, out, err)
    chats on `io` and `out`; main([]) shows the menu; streams default to the process's own."""
    out, err = stdout or sys.stdout, stderr or sys.stderr
    try:
        args = build_parser().parse_args(argv)
    except SystemExit as stop:
        return 0 if stop.code in (0, None) else 2
    if args.help or args.command == "help" or not argv:
        out.write(MENU)
        return 0
    if args.forget_key:
        return forget_key_command(out, err)
    if args.key is not None:
        return store_key_command(args.key, out, err)
    if not args.pack:
        err.write("solarchat: the chat needs --pack <pack>; `solarchat help` shows every command\n")
        return 2
    return start_chat(args.pack, args.demo, args.answerer, stdin or sys.stdin, out, err, args.model)
