import configparser
import os
from pathlib import Path

CONFIG_FILE = Path.home() / ".config" / "pomodoro" / "pomodoro.conf"

_parser = configparser.ConfigParser(strict=False, interpolation=None)
try:
    _parser.read(CONFIG_FILE)
except configparser.Error:
    pass  # malformed file: keep the defaults

def _get(section, key, default, cast=str):
    try:
        return cast(_parser.get(section, key))
    except (configparser.Error, ValueError):
        return default

def _as_bool(value):
    return value.strip().lower() in ("1", "true", "yes", "on")

def _as_path(value):
    return Path(value).expanduser()

_DEFAULT_MINUTES = {"work": 25, "short": 5, "long": 15}
_DEFAULT_BEEPS = {"work": 1, "short": 2, "long": 3}
_DEFAULT_LABELS = {"work": "Focus", "short": "Short break", "long": "Long break"}
_DEFAULT_STATE_FILE = Path(os.environ.get("XDG_RUNTIME_DIR", "/tmp")) / "pomodoro.json"
_DEFAULT_SOUND = "/usr/share/sounds/freedesktop/stereo/message.oga"

DURATIONS = {p: int(_get("durations", p, m, float) * 60) for p, m in _DEFAULT_MINUTES.items()}
BEEPS = {p: _get("beeps", p, n, int) for p, n in _DEFAULT_BEEPS.items()}
LABELS = {p: _get("labels", p, text) for p, text in _DEFAULT_LABELS.items()}

CYCLES_BEFORE_LONG_BREAK = _get("timer", "cycles", 4, int)
AUTO_START = _get("timer", "auto_start", False, _as_bool)
SOUND_FILE = _get("sound", "file", _DEFAULT_SOUND)
STATE_FILE = _get("state", "file", _DEFAULT_STATE_FILE, _as_path)
