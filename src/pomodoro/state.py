import json
import os
import time

from .config import AUTO_START, CYCLES_BEFORE_LONG_BREAK, DURATIONS, STATE_FILE

def new_state():
    return {"phase": "work", "running": False, "left": DURATIONS["work"],
            "end": 0, "done": 0, "auto": AUTO_START}

def load_state():
    try:
        return {**new_state(), **json.loads(STATE_FILE.read_text())}
    except (OSError, ValueError):
        return new_state()

def save_state(state):
    # Write atomically so a reader never sees a partial file
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = STATE_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(state))
    os.replace(tmp, STATE_FILE)

def remaining(state):
    if state["running"]:
        return max(0, int(state["end"] - time.time()))
    return state["left"]

def start(state):
    state.update(running=True, end=time.time() + state["left"])

def advance(state):
    if state["phase"] == "work":
        state["done"] += 1
        long_break = state["done"] % CYCLES_BEFORE_LONG_BREAK == 0
        state["phase"] = "long" if long_break else "short"
    else:
        state["phase"] = "work"
    state.update(running=False, left=DURATIONS[state["phase"]])
