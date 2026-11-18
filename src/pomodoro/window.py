import math

from gi.repository import Gdk, GdkPixbuf, GLib, Gtk

from . import actions, config
from .report import ReportDialog
from .settings import SettingsDialog
from .status import current_status

from importlib.resources import files

# (icon, tooltip, action)
CONTROLS = (
    ("media-skip-backward-symbolic", "Prev", actions.prev),
    ("media-playback-start-symbolic", "Start/Pause", actions.toggle),
    ("media-skip-forward-symbolic", "Next", actions.skip),
)

PHASE_COLORS = {"work": "#e05555", "short": "#4caf7d", "long": "#4a90d9"}

RING_COLORS = ["#e05555", "#e08a3c", "#e0c030", "#4caf7d", "#4a90d9"]


class PomodoroWindow(Gtk.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app, title="Pomodoro", resizable=False)
        self.connect("key-press-event", self.on_key_press)
        self.connect("destroy", lambda _: actions.apply(actions.pause))

        css = Gtk.CssProvider()
        css.load_from_data(files("pomodoro").joinpath("style.css").read_bytes())
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(), css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        self.build_ui()
        self.refresh()
        GLib.timeout_add_seconds(1, self.on_tick)
        self.show_all()

        # focus start button by default
        Gtk.Widget.grab_focus(self.toggle_button)

    def build_ui(self):
        overlay = Gtk.Overlay()
        self.add(overlay)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10, margin=15)
        overlay.add(box)

        tools = Gtk.Box(spacing=2, halign=Gtk.Align.END, valign=Gtk.Align.START)
        for icon, tip, handler in (("dialog-information-symbolic", "Report", self.on_report),
                                   ("preferences-system-symbolic", "Settings", self.on_settings),
                                   ("help-about-symbolic", "About", self.on_about)):
            button = Gtk.Button.new_from_icon_name(icon, Gtk.IconSize.BUTTON)
            button.set_relief(Gtk.ReliefStyle.NONE)
            button.set_tooltip_text(tip)
            button.connect("clicked", handler)
            tools.pack_start(button, False, False, 0)
        overlay.add_overlay(tools)

        self.phase_label = Gtk.Label()
        self.time_label = Gtk.Label()
        self.info_label = Gtk.Label()
        box.pack_start(self.phase_label, False, False, 0)

        self.phase_label.set_halign(Gtk.Align.START)

        # Ring with the time centered over it
        self.ring = Gtk.Image()
        self.ring.set_size_request(240, 240)  # keeps the dial area even when the ring is hidden
        dial = Gtk.Overlay()
        dial.add(self.ring)

        # Reset button above the time, inside the ring
        reset = self.icon_button("view-refresh-symbolic", "Reset", actions.reset)
        reset.set_halign(Gtk.Align.CENTER)
        reset.set_valign(Gtk.Align.CENTER)
        reset.set_margin_bottom(115)
        dial.add_overlay(reset)

        self.time_label.set_halign(Gtk.Align.CENTER)
        self.time_label.set_valign(Gtk.Align.CENTER)
        dial.add_overlay(self.time_label)

        # Play/pause, prev, next below the time, inside the ring
        controls = Gtk.Box(spacing=4, halign=Gtk.Align.CENTER, valign=Gtk.Align.CENTER, margin_top=115)
        for icon, tip, action in CONTROLS:
            button = self.icon_button(icon, tip, action)
            if action is actions.toggle:
                self.toggle_button = button
            controls.pack_start(button, False, False, 0)
        dial.add_overlay(controls)

        box.pack_start(dial, True, True, 0)
        box.pack_start(self.info_label, False, False, 0)

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
        self.info_label.set_markup(f'<span foreground="{state_color}">{state_text}</span> | Completed today: {status["done"]}')

        if config.SHOW_RING:
            total = config.DURATIONS[status["phase"]]
            fraction = status["left"] / total if total else 0.0
            self.ring.set_from_pixbuf(self.ring_pixbuf(fraction, color))
        else:
            self.ring.clear()

        icon = "media-playback-pause-symbolic" if status["running"] else "media-playback-start-symbolic"
        self.toggle_button.set_image(Gtk.Image.new_from_icon_name(icon, Gtk.IconSize.BUTTON))

    def ring_pixbuf(self, fraction, color, size=240):
        # Single arc that shrinks clockwise as time runs out
        parts = []
        if fraction > 0:
            end = -math.pi / 2 + math.tau * min(fraction, 0.9999)
            x1, y1 = 50 + 46 * math.cos(end), 50 + 46 * math.sin(end)
            parts.append(
                f'<path d="M50 4 A46 46 0 {int(fraction > 0.5)} 1 {x1:.2f} {y1:.2f}" '
                f'stroke="{color}" stroke-linecap="round"/>')

        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 100 100">'
               f'<g fill="none" stroke-width="3">{"".join(parts)}</g></svg>')
        loader = GdkPixbuf.PixbufLoader.new_with_type("svg")
        loader.write(svg.encode())
        loader.close()
        return loader.get_pixbuf()

    def icon_button(self, icon, tip, action):
        button = Gtk.Button.new_from_icon_name(icon, Gtk.IconSize.BUTTON)
        button.set_relief(Gtk.ReliefStyle.NONE)
        button.get_style_context().add_class("dim")
        button.set_tooltip_text(tip)
        button.connect("clicked", self.on_click, action, None)
        return button

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

    def on_about(self, _):
        dialog = Gtk.AboutDialog(transient_for=self, modal=True)
        dialog.set_program_name("Pomodoro")
        dialog.set_version("1.0")
        dialog.set_comments("Simple Pomodoro timer built with GTK.")
        dialog.set_authors(["Guilherme Daher"])
        dialog.set_website("https://github.com/daher13/pomodoro")
        dialog.set_website_label("GitHub")
        dialog.set_license_type(Gtk.License.MIT_X11)
        dialog.run()
        dialog.destroy()

    def on_report(self, _):
        dialog = ReportDialog(self)
        dialog.run()
        dialog.destroy()

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
            # self.close()
            return True

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