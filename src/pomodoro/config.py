import configparser
import os
from pathlib import Path

CONFIG_FILE = Path.home() / ".config" / "pomodoro" / "pomodoro.conf"
STATE_FILE = Path("/tmp/pomodoro.json")

_parser = configparser.ConfigParser()
_parser.read(CONFIG_FILE)

def _get(section, key, default, cast=str):
    try:
        return cast(_parser.get(section, key))
    except (configparser.Error, ValueError):
        return default


DURATIONS = {
    phase: int(_get("durations", phase, default, float) * 60)
    for phase, default in (("work", 25), ("short", 5), ("long", 15))
}

BEEPS = {
    phase: _get("beeps", phase, default, int)
    for phase, default in (("work", 1), ("short", 2), ("long", 3))
}

CYCLES_BEFORE_LONG_BREAK = _get("timer", "cycles", 4, int)

SOUND_FILE = _get("sound", "file", "/usr/share/sounds/freedesktop/stereo/message.oga")

LABELS = {
    phase: _get("labels", phase, default, str)
    for phase, default in (("work", "Focus"), ("short", "Short break"), ("long", "Long break"))
}

DEFAULT_STATE_FILE = Path(os.environ.get("XDG_RUNTIME_DIR", "/tmp")) / "pomodoro.json"
STATE_FILE = _get("state", "file", DEFAULT_STATE_FILE, lambda v: Path(v).expanduser())
