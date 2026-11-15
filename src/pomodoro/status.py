from .alerts import beep, notify
from .config import BEEPS, LABELS
from .state import advance, load_state, remaining, save_state, start

def finish_phase_if_due(state):
    if not (state["running"] and remaining(state) == 0):
        return
    finished = LABELS[state["phase"]]
    advance(state)
    if state["auto"]:
        start(state)
    save_state(state)
    beep(BEEPS[state["phase"]])
    notify(f"{finished} finished. Next: {LABELS[state['phase']]}")

def current_status():
    state = load_state()
    finish_phase_if_due(state)
    return {
        "phase": state["phase"],
        "left": remaining(state),
        "running": state["running"],
        "done": state["done"],
        "auto": state["auto"],
    }
