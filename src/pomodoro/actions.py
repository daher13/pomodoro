from . import config
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
    state.update(running=False, left=config.DURATIONS[state["phase"]], end=0)

def reset_all(state):
    state.update(new_state())

def apply_durations(state, old_durations):
    # A stopped phase that was never started picks up its new duration right away
    phase = state["phase"]
    if not state["running"] and state["left"] == old_durations[phase]:
        state["left"] = config.DURATIONS[phase]
