"""Speech out for the demo (TODO 2.7): the chat reads a reply's words through the system's own voice, no new dependency.

Windows is PowerShell's System.Speech synthesizer, macOS is `say`, Linux is `espeak`. The text goes to the engine on its
standard input and never into a command line or a script string, so nothing the model writes can run as a command: the
Windows script is a constant, given by `-EncodedCommand`, and reads the words from its own input. Decision: HAD-06 (the
demo banner is spoken once, at the start); F-08's speech on the phone is not this.
"""
import base64
import shutil
import subprocess
import sys
from typing import Any, Callable, TextIO

TIMEOUT_SECONDS = 300
# The fixed script: it reads the reply from its own standard input, so the reply is never part of it.
WINDOWS_SCRIPT = (
    "[Console]::InputEncoding = [System.Text.Encoding]::UTF8; "
    "Add-Type -AssemblyName System.Speech; "
    "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
    "$s.Speak([Console]::In.ReadToEnd())"
)
WINDOWS_ENCODED = base64.b64encode(WINDOWS_SCRIPT.encode("utf-16-le")).decode("ascii")
NO_ENGINE = "solarchat: --voice found no speech engine on this system; the chat goes on in text"


def engine_command(platform: str, which: Callable[[str], str | None] = shutil.which) -> list[str] | None:
    """The argument list of the system's speech engine for this platform, or None when it has none; it holds no reply text:
    engine_command("darwin", lambda name: "/usr/bin/say") gives ["/usr/bin/say", "-f", "-"]."""
    if platform == "win32":
        shell = which("powershell") or which("powershell.exe")
        return [shell, "-NoProfile", "-NonInteractive", "-EncodedCommand", WINDOWS_ENCODED] if shell else None
    if platform == "darwin":
        engine = which("say")
        return [engine, "-f", "-"] if engine else None
    engine = which("espeak")
    return [engine, "--stdin"] if engine else None


class Speaker:
    """Speaks text through the engine, one piece at a time, waiting for each; the first trouble (no engine, a failed run)
    is one plain line on `stderr` and the speaker goes quiet, so the chat goes on in text: Speaker(err).say("Hello.")."""

    def __init__(self, stderr: TextIO, runner: Callable[..., Any] = subprocess.run, platform: str = sys.platform,
                 which: Callable[[str], str | None] = shutil.which) -> None:
        """Find the engine now; with none, say so once. `runner` has subprocess.run's shape (tests give a fake)."""
        self.stderr, self.runner = stderr, runner
        self.command = engine_command(platform, which)
        if self.command is None:
            stderr.write(NO_ENGINE + "\n")

    def say(self, text: str) -> None:
        """Speak `text` (sent on standard input, never in the arguments); nothing when it is blank or the speaker is quiet."""
        if self.command is None or not text.strip():
            return
        try:
            done = self.runner(self.command, input=text, text=True, encoding="utf-8", check=False, timeout=TIMEOUT_SECONDS)
            problem = f"the speech engine stopped with code {done.returncode}" if done.returncode else ""
        except (OSError, subprocess.SubprocessError) as error:
            problem = f"the speech engine could not run ({type(error).__name__})"
        if problem:
            self.command = None
            self.stderr.write(f"solarchat: {problem}; the chat goes on in text\n")
