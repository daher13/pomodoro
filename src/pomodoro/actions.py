import time

from .config import DURATIONS
from .state import advance, load_state, new_state, remaining, save_state

def pause(state):
    if state["running"]:
        state.update(running=False, left=remaining(state))

def toggle(state):
    if state["running"]:
        pause(state)
    else:
        state.update(running=True, end=time.time() + state["left"])


def skip(state):
    advance(state)

def reset(state):
    # Reset only the current phase timer; keep the completed count
    state.update(running=False, left=DURATIONS[state["phase"]], end=0)


def reset_all(state):
    state.update(new_state())

ACTIONS = {"toggle": toggle, "pause": pause, "skip": skip, "reset": reset, "reset-all": reset_all}

def apply_action(name):
    state = load_state()
    ACTIONS[name](state)
    save_state(state)
