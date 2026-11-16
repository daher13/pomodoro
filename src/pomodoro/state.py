import json
import os
import time
from datetime import date

from . import config

def today():
    return date.today().isoformat()

def new_state():
    return {"phase": "work", "running": False, "left": config.DURATIONS["work"],
            "end": 0, "done": 0, "day": today()}

def load_state():
    try:
        state = {**new_state(), **json.loads(config.STATE_FILE.read_text())}
    except (OSError, ValueError):
        return new_state()
    if state["day"] != today():
        state.update(done=0, day=today())  # new day: restart the daily count
    return state

def _write_json(path, data):
    # Write atomically so a reader never sees a partial file
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data))
    os.replace(tmp, path)

def save_state(state):
    _write_json(config.STATE_FILE, state)

def load_history():
    try:
        return json.loads(config.HISTORY_FILE.read_text())
    except (OSError, ValueError):
        return {}

def record_pomodoro():
    # History maps ISO date -> completed pomodoros that day
    history = load_history()
    history[today()] = history.get(today(), 0) + 1
    _write_json(config.HISTORY_FILE, history)

def remaining(state):
    if state["running"]:
        return max(0, int(state["end"] - time.time()))
    return state["left"]

def start(state):
    state.update(running=True, end=time.time() + state["left"])

def advance(state):
    if state["phase"] == "work":
        state["done"] += 1
        record_pomodoro()
        long_break = state["done"] % config.CYCLES_BEFORE_LONG_BREAK == 0
        state["phase"] = "long" if long_break else "short"
    else:
        state["phase"] = "work"
    state.update(running=False, left=config.DURATIONS[state["phase"]])