"""Speech out for the demo (TODO 2.7): the chat reads a reply's words through the system's own voice, no new dependency.

Windows is PowerShell's System.Speech synthesizer, macOS is `say`, Linux is `espeak`. The text goes to the engine on its
standard input and never into a command line or a script string, so nothing the model writes can run as a command: the
Windows script is a constant, given by `-EncodedCommand`, and reads the words from its own input. Decision: HAD-06 (the
demo banner is spoken once, at the start); F-08's speech on the phone is not this.
"""
import base64
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable, TextIO

from solarchat.model.key import key_path

TIMEOUT_SECONDS = 300
# The fixed script: it reads the reply from its own standard input, so the reply is never part of it.
WINDOWS_SCRIPT = (
    "[Console]::InputEncoding = [System.Text.Encoding]::UTF8; "
    "Add-Type -AssemblyName System.Speech; "
    "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
    "if ($env:SOLARCHAT_VOICE_NAME) { try { $s.SelectVoice($env:SOLARCHAT_VOICE_NAME) } catch { } }; "
    "$s.Speak([Console]::In.ReadToEnd())"
)
WINDOWS_ENCODED = base64.b64encode(WINDOWS_SCRIPT.encode("utf-16-le")).decode("ascii")
# The fixed listing script (TODO 2.13): the enabled voices, one per line as name, culture and gender split by tabs.
WINDOWS_LIST_SCRIPT = (
    "[Console]::OutputEncoding = [System.Text.Encoding]::UTF8; "
    "Add-Type -AssemblyName System.Speech; "
    "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
    "$s.GetInstalledVoices() | Where-Object { $_.Enabled } | ForEach-Object { "
    "$i = $_.VoiceInfo; $i.Name + [char]9 + $i.Culture.Name + [char]9 + $i.Gender }"
)
WINDOWS_LIST_ENCODED = base64.b64encode(WINDOWS_LIST_SCRIPT.encode("utf-16-le")).decode("ascii")
VOICE_VARIABLE = "SOLARCHAT_VOICE_NAME"
VOICE_FILE = "voice"
MAX_VOICE_NAME = 100
NO_ENGINE = "solarchat: --voice found no speech engine on this system; the chat goes on in text"


def engine_command(platform: str, which: Callable[[str], str | None] = shutil.which, voice: str | None = None) -> list[str] | None:
    """The argument list of the system's speech engine for this platform, or None when it has none; it holds no reply text,
    and on Windows no voice name either (that goes in an environment variable): engine_command("darwin", lambda name:
    "/usr/bin/say") gives ["/usr/bin/say", "-f", "-"], and with voice "Samantha" ["/usr/bin/say", "-v", "Samantha", "-f", "-"]."""
    if platform == "win32":
        shell = which("powershell") or which("powershell.exe")
        return [shell, "-NoProfile", "-NonInteractive", "-EncodedCommand", WINDOWS_ENCODED] if shell else None
    if platform == "darwin":
        engine = which("say")
        return [engine, *(["-v", voice] if voice else []), "-f", "-"] if engine else None
    engine = which("espeak")
    return [engine, *(["-v", voice] if voice else []), "--stdin"] if engine else None


def list_command(platform: str, which: Callable[[str], str | None] = shutil.which) -> list[str] | None:
    """The argument list that prints the installed voices, or None with no engine: list_command("linux", lambda name:
    "/bin/espeak") gives ["/bin/espeak", "--voices"]."""
    if platform == "win32":
        shell = which("powershell") or which("powershell.exe")
        return [shell, "-NoProfile", "-NonInteractive", "-EncodedCommand", WINDOWS_LIST_ENCODED] if shell else None
    if platform == "darwin":
        engine = which("say")
        return [engine, "-v", "?"] if engine else None
    engine = which("espeak")
    return [engine, "--voices"] if engine else None


def voice_path(environ: dict[str, str] | None = None) -> Path:
    """The chosen voice's file, beside the key: voice_path({"SOLARCHAT_CONFIG_DIR": "/x"}) gives Path("/x/voice"); a folder
    inside the repository raises ValueError, as for the key."""
    return key_path(environ).parent / VOICE_FILE


def check_voice_name(name: str) -> str:
    """The name without surrounding spaces, or ValueError in words when it is empty, over 100 characters, holds a control
    character or starts with a dash: check_voice_name(" Zira ") gives "Zira"."""
    name = name.strip()
    if not name:
        raise ValueError("the voice name is empty")
    if len(name) > MAX_VOICE_NAME:
        raise ValueError(f"the voice name is longer than {MAX_VOICE_NAME} characters")
    if any(ord(c) < 32 or ord(c) == 127 for c in name):
        raise ValueError("the voice name holds a control character")
    if name.startswith("-"):  # say and espeak take it as an argument, where a leading dash would be read as an option
        raise ValueError("the voice name starts with a dash")
    return name


def save_voice(name: str, environ: dict[str, str] | None = None) -> Path:
    """Store the chosen voice's name (not a secret) and return the file's path; a refused name or folder raises ValueError."""
    name = check_voice_name(name)
    path = voice_path(environ)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(name + "\n", encoding="utf-8")
    return path


def forget_voice(environ: dict[str, str] | None = None) -> bool:
    """Delete the chosen voice: True when there was one, False when not."""
    path = voice_path(environ)
    if not path.is_file():
        return False
    path.unlink()
    return True


def stored_voice(environ: dict[str, str] | None = None) -> str | None:
    """The chosen voice's name, or None when there is none, the file is not a good name, or the folder is refused."""
    try:
        path = voice_path(environ)
        return check_voice_name(path.read_text(encoding="utf-8")) if path.is_file() else None
    except (ValueError, OSError):
        return None


def installed_voices(platform: str, runner: Callable[..., Any] = subprocess.run, which: Callable[[str], str | None] = shutil.which) -> list[str] | None:
    """The lines the listing command prints, or None with no engine or a listing that failed."""
    command = list_command(platform, which)
    if command is None:
        return None
    try:
        done = runner(command, capture_output=True, text=True, encoding="utf-8", check=False, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return None
    return None if done.returncode else [line for line in str(done.stdout).splitlines() if line.strip()]


def voice_name_of(platform: str, line: str) -> str:
    """The voice name a listing line starts a voice with, to compare with the chosen one: Windows lines are tab-split, macOS
    names end at the first run of two spaces, espeak's name is its fourth column."""
    if platform == "win32":
        return line.split("\t")[0].strip()
    if platform == "darwin":
        return re.split(r"\s{2,}", line.strip())[0]
    columns = line.split()
    return columns[3] if len(columns) > 3 else ""


def voices_command(stdout: TextIO, stderr: TextIO, platform: str = sys.platform, runner: Callable[..., Any] = subprocess.run,
                   which: Callable[[str], str | None] = shutil.which) -> int:
    """List the installed voices, the chosen one marked, and say how to choose: 0 listed, 1 no engine or a failed listing.
    Windows lines are shown as `Name (culture, gender)`; macOS and Linux lines as the engine gives them."""
    if list_command(platform, which) is None:
        stderr.write(NO_ENGINE + "\n")
        return 1
    lines = installed_voices(platform, runner, which)
    if lines is None:
        stderr.write("solarchat: the voices could not be listed; the speech engine failed\n")
        return 1
    chosen = stored_voice()
    for line in lines:
        name = voice_name_of(platform, line)
        shown = line
        if platform == "win32":
            parts = line.split("\t")
            shown = f"{parts[0]} ({', '.join(p for p in parts[1:] if p)})" if len(parts) > 1 else parts[0]
        mark = " (chosen)" if chosen and name.lower() == chosen.lower() else ""
        stdout.write(shown + mark + "\n")
    stdout.write('Choose one with: solarchat --voice-name "<name>"\n')
    return 0


def voice_name_command(name: str, stdout: TextIO, stderr: TextIO, platform: str = sys.platform, runner: Callable[..., Any] = subprocess.run,
                       which: Callable[[str], str | None] = shutil.which) -> int:
    """Remember the voice `name` (or forget it, for "default") and return the exit code (0 done, 2 refused). On Windows a
    name the listing does not show gets a warning (best effort: no warning when the listing fails)."""
    try:
        if name.strip().lower() == "default":
            gone = forget_voice()
            stdout.write("Voice forgotten; the system's default voice is used.\n" if gone else "No voice was chosen; the system's default voice is used.\n")
            return 0
        name = check_voice_name(name)
        voice_path()
        lines = installed_voices(platform, runner, which) if platform == "win32" else None
        save_voice(name)
    except (ValueError, OSError) as problem:
        stderr.write(f"solarchat: the voice was not saved: {problem}\n")
        return 2
    if lines is not None and name.lower() not in (voice_name_of(platform, line).lower() for line in lines):
        stderr.write(f'solarchat: warning: "{name}" is not in the installed voices; the default voice is used until it is. `solarchat --voices` lists them\n')
    stdout.write(f"Voice set to {name}. It is used whenever the voice is on.\n")
    return 0


class Speaker:
    """Speaks text through the engine, one piece at a time, waiting for each; the first trouble (no engine, a failed run)
    is one plain line on `stderr` and the speaker goes quiet, so the chat goes on in text: Speaker(err).say("Hello.")."""

    def __init__(self, stderr: TextIO, runner: Callable[..., Any] = subprocess.run, platform: str = sys.platform,
                 which: Callable[[str], str | None] = shutil.which, voice: str | None = None) -> None:
        """Find the engine and the chosen voice now (`voice` given, else the stored one); with no engine, say so once.
        `runner` has subprocess.run's shape (tests give a fake)."""
        self.stderr, self.runner = stderr, runner
        self.voice = voice or stored_voice()
        self.command = engine_command(platform, which, self.voice)
        # On Windows the name travels in an environment variable, never in the script or the arguments.
        self.environment = {**os.environ, VOICE_VARIABLE: self.voice} if self.voice and platform == "win32" else None
        if self.command is None:
            stderr.write(NO_ENGINE + "\n")

    def say(self, text: str) -> None:
        """Speak `text` (sent on standard input, never in the arguments); nothing when it is blank or the speaker is quiet."""
        if self.command is None or not text.strip():
            return
        try:
            extra = {"env": self.environment} if self.environment else {}
            done = self.runner(self.command, input=text, text=True, encoding="utf-8", check=False, timeout=TIMEOUT_SECONDS, **extra)
            problem = f"the speech engine stopped with code {done.returncode}" if done.returncode else ""
        except (OSError, subprocess.SubprocessError) as error:
            problem = f"the speech engine could not run ({type(error).__name__})"
        if problem:
            self.command = None
            self.stderr.write(f"solarchat: {problem}; the chat goes on in text\n")
