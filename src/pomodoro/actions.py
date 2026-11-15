from .config import AUTO_START, DURATIONS
from .state import advance, load_state, new_state, remaining, save_state, start

def apply(action, *args):
    state = load_state()
    action(state, *args)
    save_state(state)

def pause(state):
    if state["running"]:
        state.update(running=False, left=remaining(state))

def toggle(state):
    if state["running"]:
        pause(state)
    else:
        start(state)

def skip(state):
    advance(state)

def reset(state):
    # Reset only the current phase timer; keep the completed count
    state.update(running=False, left=DURATIONS[state["phase"]], end=0)

def reset_all(state):
    state.update(new_state())

def set_auto(state, value):
    state["auto"] = value

def sync_config(state):
    state["auto"] = AUTO_START
