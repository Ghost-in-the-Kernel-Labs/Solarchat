"""Run the chat: `python3 -m solarchat.cli --pack packs/seed-mc4-leads --demo [--answerer claude|stub]`."""
import sys

from solarchat.cli.main import main

sys.exit(main(sys.argv[1:]))
