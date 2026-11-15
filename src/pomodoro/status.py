from . import config
from .alerts import beep, notify
from .state import advance, load_state, remaining, save_state, start

def _finish_phase_if_due(state):
    if not (state["running"] and remaining(state) == 0):
        return
    finished = config.LABELS[state["phase"]]
    advance(state)
    if config.AUTO_START:
        start(state)
    save_state(state)
    beep(config.BEEPS[state["phase"]])
    notify(f"{finished} finished. Next: {config.LABELS[state['phase']]}")

def current_status():
    state = load_state()
    _finish_phase_if_due(state)
    return {**state, "left": remaining(state)}