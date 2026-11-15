from . import config
from .alerts import beep, notify
from .state import advance, load_state, remaining, save_state, start

# Auto start chosen in the window: lives only while the app is open
session = {"auto_start": config.AUTO_START}

def finish_phase_if_due(state):
    if not (state["running"] and remaining(state) == 0):
        return
    finished = config.LABELS[state["phase"]]
    advance(state)
    if session["auto_start"]:
        start(state)
    save_state(state)
    beep(config.BEEPS[state["phase"]])
    notify(f"{finished} finished. Next: {config.LABELS[state['phase']]}")

def current_status():
    state = load_state()
    finish_phase_if_due(state)
    return {
        "phase": state["phase"],
        "left": remaining(state),
        "running": state["running"],
        "done": state["done"],
    }
