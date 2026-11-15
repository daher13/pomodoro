import configparser
import os
from pathlib import Path

CONFIG_FILE = Path.home() / ".config" / "pomodoro" / "pomodoro.conf"

_DEFAULT_MINUTES = {"work": 25, "short": 5, "long": 15}
_DEFAULT_BEEPS = {"work": 1, "short": 2, "long": 3}
_DEFAULT_LABELS = {"work": "Focus", "short": "Short break", "long": "Long break"}
_DEFAULT_STATE_FILE = Path(os.environ.get("XDG_RUNTIME_DIR", "/tmp")) / "pomodoro.json"
_DEFAULT_SOUND = "/usr/share/sounds/freedesktop/stereo/message.oga"

_parser = configparser.ConfigParser()

def _get(section, key, default, cast=str):
    try:
        return cast(_parser.get(section, key))
    except (configparser.Error, ValueError):
        return default

def _as_bool(value):
    return value.strip().lower() in ("1", "true", "yes", "on")

def _as_path(value):
    return Path(value).expanduser()

def load():
    # Other modules read these as config.X at call time, so reloading takes effect immediately
    global _parser, DURATIONS, BEEPS, LABELS
    global CYCLES_BEFORE_LONG_BREAK, AUTO_START, SOUND_FILE, STATE_FILE

    _parser = configparser.ConfigParser(strict=False, interpolation=None)
    try:
        _parser.read(CONFIG_FILE)
    except configparser.Error:
        pass  # malformed file: keep the defaults

    DURATIONS = {p: int(_get("durations", p, m, float) * 60) for p, m in _DEFAULT_MINUTES.items()}
    BEEPS = {p: _get("beeps", p, n, int) for p, n in _DEFAULT_BEEPS.items()}
    LABELS = {p: _get("labels", p, text) for p, text in _DEFAULT_LABELS.items()}
    CYCLES_BEFORE_LONG_BREAK = _get("timer", "cycles", 4, int)
    AUTO_START = _get("timer", "auto_start", False, _as_bool)
    SOUND_FILE = _get("sound", "file", _DEFAULT_SOUND)
    STATE_FILE = _get("state", "file", _DEFAULT_STATE_FILE, _as_path)

def save_config(values):
    # values: {(section, key): text}; an empty text removes the key (back to the default)
    for (section, key), value in values.items():
        if not _parser.has_section(section):
            _parser.add_section(section)
        if value:
            _parser.set(section, key, value)
        else:
            _parser.remove_option(section, key)
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with CONFIG_FILE.open("w") as f:
        _parser.write(f)
    load()

load()
