import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gdk, GLib, Gtk

from .actions import apply_action
from .status import current_status
from .config import LABELS

BUTTONS = (
    ("Start/Pause", "toggle"),
    ("Reset", "reset"),
    ("Skip", "skip"),
    ("Reset All", "reset-all"),
)

def confirm(parent, text):
    dialog = Gtk.MessageDialog(
        transient_for=parent,
        modal=True,
        message_type=Gtk.MessageType.QUESTION,
        buttons=Gtk.ButtonsType.YES_NO,
        text=text,
    )
    answer = dialog.run()
    dialog.destroy()
    return answer == Gtk.ResponseType.YES

def build_window(app):
    win = Gtk.ApplicationWindow(application=app, title="Pomodoro", resizable=False)
    win.set_default_size(380, 170)
    win.connect(
        "key-press-event",
        lambda w, event: w.close() if event.keyval == Gdk.KEY_Escape else None,
    )

    win.connect("destroy", lambda _: apply_action("pause"))

    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10, margin=15)
    win.add(box)

    phase_label = Gtk.Label()
    time_label = Gtk.Label()
    info_label = Gtk.Label()
    box.pack_start(phase_label, False, False, 0)
    box.pack_start(time_label, True, True, 0)
    box.pack_start(info_label, False, False, 0)

    def refresh():
        status = current_status()
        minutes, seconds = divmod(status["left"], 60)
        phase_label.set_markup(f'<span size="large" weight="bold">{LABELS[status["phase"]]}</span>')
        time_label.set_markup(f'<span font="monospace 40">{minutes:02d}:{seconds:02d}</span>')
        info_label.set_text(f'{"Running" if status["running"] else "Paused"} | Completed: {status["done"]}')

    def on_click(_, action):
        if action == "reset-all" and not confirm(win, "Reset everything, including the completed count?"):
            return
        apply_action(action)
        refresh()

    row = Gtk.Box(spacing=6, halign=Gtk.Align.CENTER)
    box.pack_start(row, False, False, 0)
    for label, action in BUTTONS:
        button = Gtk.Button(label=label)
        button.connect("clicked", on_click, action)
        row.pack_start(button, False, False, 0)

    def tick():
        refresh()
        return True

    refresh()
    GLib.timeout_add_seconds(1, tick)
    win.show_all()


def on_activate(app):
    # A second launch lands here too: just bring the existing window forward
    windows = app.get_windows()
    if windows:
        windows[0].present()
    else:
        build_window(app)


def show_window():
    GLib.set_prgname("pomodoro")  # app-id on Wayland
    app = Gtk.Application(application_id="local.pomodoro")
    app.connect("activate", on_activate)
    app.run(None)
