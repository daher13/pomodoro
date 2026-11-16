from gi.repository import Gdk, GLib, Gtk

from . import actions, config
from .settings import SettingsDialog
from .status import current_status

# (label, action, confirmation question or None)
BUTTONS = (
    ("Start/Pause", actions.toggle, None),
    ("Reset", actions.reset, None),
    ("Skip", actions.skip, None),
    ("Reset All", actions.reset_all, "Reset everything, including the completed count?"),
)

PHASE_COLORS = {"work": "#e05555", "short": "#4caf7d", "long": "#4a90d9"}

class PomodoroWindow(Gtk.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app, title="Pomodoro", resizable=False)
        self.connect("key-press-event", self.on_key_press)
        self.connect("destroy", lambda _: actions.apply(actions.pause))

        self.build_ui()
        self.refresh()
        GLib.timeout_add_seconds(1, self.on_tick)
        self.show_all()

    def build_ui(self):
        overlay = Gtk.Overlay()
        self.add(overlay)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10, margin=15)
        overlay.add(box)

        settings = Gtk.Button.new_from_icon_name("preferences-system-symbolic", Gtk.IconSize.BUTTON)
        settings.set_relief(Gtk.ReliefStyle.NONE)
        settings.set_tooltip_text("Settings")
        settings.set_halign(Gtk.Align.END)
        settings.set_valign(Gtk.Align.START)
        settings.connect("clicked", self.on_settings)
        overlay.add_overlay(settings)

        self.phase_label = Gtk.Label()
        self.time_label = Gtk.Label()
        self.info_label = Gtk.Label()
        box.pack_start(self.phase_label, False, False, 0)
        box.pack_start(self.time_label, True, True, 0)
        box.pack_start(self.info_label, False, False, 0)

        row = Gtk.Box(spacing=6, halign=Gtk.Align.CENTER)
        box.pack_start(row, False, False, 0)
        for label, action, question in BUTTONS:
            button = Gtk.Button(label=label)
            button.connect("clicked", self.on_click, action, question)
            row.pack_start(button, False, False, 0)

    def refresh(self):
        # The UI always mirrors the saved state
        status = current_status()
        minutes, seconds = divmod(status["left"], 60)
        color = PHASE_COLORS[status["phase"]]
        alpha = "100%" if status["running"] else "55%"
        state_text = "Running" if status["running"] else "Paused"
        state_color = "#4caf7d" if status["running"] else "#e0a030"
        self.phase_label.set_markup(f'<span size="large" weight="bold" foreground="{color}">{config.LABELS[status["phase"]]}</span>')
        self.time_label.set_markup(f'<span font="monospace 40" foreground="{color}" alpha="{alpha}">{minutes:02d}:{seconds:02d}</span>')
        self.info_label.set_markup(f'<span foreground="{state_color}">{state_text}</span> | Completed: {status["done"]}')

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

    def on_click(self, _, action, question):
        if question and not self.confirm(question):
            return
        actions.apply(action)
        self.refresh()

    def on_settings(self, _):
        old_durations = dict(config.DURATIONS)  # taken before the dialog reloads the config file
        dialog = SettingsDialog(self)
        if dialog.run() == Gtk.ResponseType.OK:
            config.save_config(dialog.values())
            actions.apply(actions.apply_durations, old_durations)
            self.refresh()
        dialog.destroy()

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