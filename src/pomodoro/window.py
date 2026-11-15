import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gdk, GLib, Gtk

from . import actions
from .config import LABELS
from .status import current_status

BUTTONS = (
    ("Start/Pause", actions.toggle),
    ("Reset", actions.reset),
    ("Skip", actions.skip),
    ("Reset All", actions.reset_all),
)

class PomodoroWindow(Gtk.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app, title="Pomodoro", resizable=False)
        self.set_default_size(380, 220)
        self.connect("key-press-event", self.on_key_press)
        self.connect("destroy", lambda _: actions.apply(actions.pause))

        actions.apply(actions.sync_config)
        self.build_ui()
        self.refresh()
        GLib.timeout_add_seconds(1, self.on_tick)
        self.show_all()

    def build_ui(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10, margin=15)
        self.add(box)

        self.phase_label = Gtk.Label()
        self.time_label = Gtk.Label()
        self.info_label = Gtk.Label()
        box.pack_start(self.phase_label, False, False, 0)
        box.pack_start(self.time_label, True, True, 0)
        box.pack_start(self.info_label, False, False, 0)

        row = Gtk.Box(spacing=6, halign=Gtk.Align.CENTER)
        box.pack_start(row, False, False, 0)
        for label, action in BUTTONS:
            button = Gtk.Button(label=label)
            button.connect("clicked", self.on_click, action)
            row.pack_start(button, False, False, 0)

        self.auto_check = Gtk.CheckButton(label="Auto start next phase", halign=Gtk.Align.CENTER)
        self.auto_check.connect("toggled", self.on_auto_toggled)
        box.pack_start(self.auto_check, False, False, 0)

    def refresh(self):
        # The UI always mirrors the saved state
        status = current_status()
        minutes, seconds = divmod(status["left"], 60)
        state_text = "Running" if status["running"] else "Paused"
        self.phase_label.set_markup(f'<span size="large" weight="bold">{LABELS[status["phase"]]}</span>')
        self.time_label.set_markup(f'<span font="monospace 40">{minutes:02d}:{seconds:02d}</span>')
        self.info_label.set_text(f'{state_text} | Completed: {status["done"]}')
        self.auto_check.set_active(status["auto"])

    def confirm(self, text):
        dialog = Gtk.MessageDialog(
            transient_for=self,
            modal=True,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text=text,
        )
        answer = dialog.run()
        dialog.destroy()
        return answer == Gtk.ResponseType.YES

    def on_click(self, _, action):
        if action is actions.reset_all and not self.confirm("Reset everything, including the completed count?"):
            return
        actions.apply(action)
        self.refresh()

    def on_auto_toggled(self, check):
        actions.apply(actions.set_auto, check.get_active())

    def on_key_press(self, _, event):
        if event.keyval == Gdk.KEY_Escape:
            self.close()

    def on_tick(self):
        self.refresh()
        return True

class PomodoroApp(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="local.pomodoro")

    def do_activate(self):
        # A second launch lands here too: just bring the existing window forward
        windows = self.get_windows()
        window = windows[0] if windows else PomodoroWindow(self)
        window.present()
