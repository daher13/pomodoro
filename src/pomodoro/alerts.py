import subprocess

from .config import SOUND_FILE

BEEP_SCRIPT = 'for i in $(seq "$1"); do paplay "$2"; done'

def _spawn(cmd):
    try:
        subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except FileNotFoundError:
        pass  # optional tool not installed

def beep(count):
    _spawn(["sh", "-c", BEEP_SCRIPT, "sh", str(count), SOUND_FILE])

def notify(message):
    _spawn(["notify-send", "Pomodoro", message])
