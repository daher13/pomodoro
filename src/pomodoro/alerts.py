import subprocess

from .config import SOUND_FILE


def beep(count):
    cmd = f"for i in $(seq {count}); do paplay {SOUND_FILE}; done"
    subprocess.Popen(["sh", "-c", cmd], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def notify(message):
    subprocess.Popen(["notify-send", "Pomodoro", message])
