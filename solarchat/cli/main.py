"""The commands' arguments, handed to project (TODO 1.16, 2.5; SC-019, SC-022 point 6). No logic of its own (MOD-02)."""
import argparse
import sys
from typing import TextIO

from solarchat.project.chat import DEFAULT_MODEL, DEMO_PACK, MODEL_CHOICES, parse_signed_off, start_chat
from solarchat.project.keys import forget_key_command, has_key_command, store_key_command

MENU = """solarchat: walks you through setting up and fixing your solar panels, from the manuals in a pack.

Commands:
  solarchat                 show this menu
  solarchat help            show this menu (also: solarchat --help)
  solarchat --key           store your model key, typed or pasted at the prompt (it stays out of shell history; the way to do it)
  solarchat --key <key>     store the key you give (it may stay in shell history)
  solarchat --forget-key    delete the stored key
  solarchat --demo          the demo: the seed pack, spoken aloud; type your question, quit to end (--no-voice for text only)
  solarchat --pack <pack>   chat about one pack, e.g. solarchat --pack packs/seed-mc4-leads --demo
  solarchat --has-key       say whether a key is set (exit 0) or not (exit 1), without showing it

Chat options (with --pack or --demo):
  --demo                    let a demo pack answer, with the demo banner on every reply; alone it uses the seed pack, with the voice on: solarchat --demo
  --voice                   speak each reply aloud through the system's own voice (the citations are shown, not spoken): solarchat --pack P --demo --voice
  --no-voice                keep the demo silent, text only: solarchat --demo --no-voice
  --answerer claude|stub    who answers: claude (the default) or stub, which says "I do not know": solarchat --pack P --answerer stub
  --model <model>           the Claude model, claude-sonnet-5-5 (the default) or claude-haiku-5-5: solarchat --pack P --model claude-haiku-5-5
  --role new|crew|qualified   your role, so the bot does not ask: solarchat --pack P --demo --role qualified
  --signed-off <list>       what you are signed off for, from meter,connector,battery,height (or none); skips the question.
                            Both given skip both questions: solarchat --demo --role qualified --signed-off battery
  --equipment <ids>         the equipment you have, by id from the list the chat shows (or none); skips the question:
                            solarchat --demo --equipment victron-smartsolar-mppt

The chat uses ANTHROPIC_API_KEY when it is set, else the key stored by solarchat --key; with neither it asks for the key and stores it. The key is never shown or uploaded.
"""


def signed_off_value(text: str) -> frozenset[str]:
    """The --signed-off value as a set, or an argparse error in words: signed_off_value("meter,battery") has both."""
    try:
        return parse_signed_off(text)
    except ValueError as problem:
        raise argparse.ArgumentTypeError(str(problem)) from None


def build_parser() -> argparse.ArgumentParser:
    """The command line: build_parser().parse_args(["--pack", "packs/x", "--demo"]).answerer gives "claude"."""
    parser = argparse.ArgumentParser(prog="solarchat", add_help=False)
    parser.add_argument("command", nargs="?", choices=("help",), help="help shows the menu")
    parser.add_argument("-h", "--help", action="store_true", help="show the menu")
    parser.add_argument("--key", nargs="?", const="", default=None, help="store the key; with no value, asked at a prompt")
    parser.add_argument("--has-key", action="store_true", help="say whether a key is set; exit 0 yes, 1 no")
    parser.add_argument("--forget-key", action="store_true", help="delete the stored key")
    parser.add_argument("--pack", help="the pack's folder, e.g. packs/seed-mc4-leads")
    parser.add_argument("--demo", action="store_true", help="let a demo pack answer, with the demo banner on every reply")
    parser.add_argument("--voice", action="store_true", help="speak each reply aloud through the system's own voice")
    parser.add_argument("--no-voice", action="store_true", help="no speech, even with --demo")
    parser.add_argument("--answerer", choices=("claude", "stub"), default="claude")
    parser.add_argument("--role", choices=("new", "crew", "qualified"), help="your role; skips the first question")
    parser.add_argument("--signed-off", type=signed_off_value, help="meter,connector,battery,height or none; skips the second question")
    parser.add_argument("--equipment", help="equipment ids from the packs' lists, or none; skips the make-and-model question")
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
    if args.has_key:
        return has_key_command(out, err)
    if args.forget_key:
        return forget_key_command(out, err)
    if args.key is not None:
        return store_key_command(args.key, out, err, stdin)
    if not args.pack and not args.demo:
        err.write("solarchat: the chat needs --pack <pack>; `solarchat help` shows every command\n")
        return 2
    pack = args.pack or str(DEMO_PACK)
    voice = (args.voice or args.demo) and not args.no_voice
    return start_chat(pack, args.demo, args.answerer, stdin or sys.stdin, out, err, args.model, voice, args.role, args.signed_off, args.equipment)
