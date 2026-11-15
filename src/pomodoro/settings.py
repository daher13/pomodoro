from pathlib import Path

from gi.repository import Gtk

from . import config

def _number(widget):
    return f"{widget.get_value():g}"

def _checked(widget):
    return "true" if widget.get_active() else "false"

def _text(widget):
    return widget.get_text().strip()

class FileField(Gtk.Box):
    # Text entry plus a button that opens the file chooser (xdg portal when available)
    def __init__(self, owner, text, action, title):
        super().__init__(spacing=6)
        self.owner = owner
        self.chooser_action = action
        self.chooser_title = title

        self.entry = Gtk.Entry(text=text, width_chars=36, hexpand=True)
        button = Gtk.Button.new_from_icon_name("document-open-symbolic", Gtk.IconSize.BUTTON)
        button.set_tooltip_text("Browse")
        button.connect("clicked", self.on_browse)
        self.pack_start(self.entry, True, True, 0)
        self.pack_start(button, False, False, 0)

    def get_text(self):
        return self.entry.get_text()

    def on_browse(self, _):
        chooser = Gtk.FileChooserNative.new(
            self.chooser_title, self.owner, self.chooser_action, "Select", "Cancel")
        saving = self.chooser_action == Gtk.FileChooserAction.SAVE
        chooser.set_do_overwrite_confirmation(False)

        path = Path(self.entry.get_text().strip() or "~").expanduser()
        if path.is_file():
            chooser.set_filename(str(path))
        elif path.parent.is_dir():
            chooser.set_current_folder(str(path.parent))
            if saving:
                chooser.set_current_name(path.name)

        if chooser.run() == Gtk.ResponseType.ACCEPT:
            self.entry.set_text(chooser.get_filename())

class SettingsDialog(Gtk.Dialog):
    def __init__(self, parent):
        super().__init__(title="Settings", transient_for=parent, modal=True)
        self.add_button("Cancel", Gtk.ResponseType.CANCEL)
        self.add_button("Save", Gtk.ResponseType.OK)
        self.set_default_response(Gtk.ResponseType.OK)

        self.fields = {}
        self.row = 0
        self.grid = Gtk.Grid(column_spacing=12, row_spacing=8, margin=15)
        self.get_content_area().add(self.grid)
        self.build_form()
        self.show_all()

    def build_form(self):
        self.add_heading("Durations (minutes)")
        for phase, seconds in config.DURATIONS.items():
            spin = Gtk.SpinButton.new_with_range(1, 240, 1)
            spin.set_value(round(seconds / 60))
            self.add_field(config.LABELS[phase], spin, "durations", phase, _number)

        self.add_heading("Timer")
        cycles = Gtk.SpinButton.new_with_range(1, 12, 1)
        cycles.set_value(config.CYCLES_BEFORE_LONG_BREAK)
        self.add_field("Focus sessions before long break", cycles, "timer", "cycles", _number)
        auto = Gtk.CheckButton(active=config.AUTO_START)
        self.add_field("Auto start next phase", auto, "timer", "auto_start", _checked)

        self.add_heading("Beeps per phase")
        for phase, count in config.BEEPS.items():
            spin = Gtk.SpinButton.new_with_range(0, 10, 1)
            spin.set_value(count)
            self.add_field(config.LABELS[phase], spin, "beeps", phase, _number)

        self.add_heading("Labels")
        for phase, text in config.LABELS.items():
            self.add_field(phase.capitalize(), Gtk.Entry(text=text), "labels", phase, _text)

        self.add_heading("Files")
        sound = FileField(self, config.SOUND_FILE, Gtk.FileChooserAction.OPEN, "Select sound")
        self.add_field("Sound", sound, "sound", "file", _text)
        state = FileField(self, str(config.STATE_FILE), Gtk.FileChooserAction.SAVE, "Select state file")
        self.add_field("State", state, "state", "file", _text)

        note = Gtk.Label(label="Changes apply the next time Pomodoro opens.")
        note.get_style_context().add_class("dim-label")
        self.grid.attach(note, 0, self.row, 2, 1)

    def add_heading(self, text):
        label = Gtk.Label(halign=Gtk.Align.START, margin_top=6)
        label.set_markup(f"<b>{text}</b>")
        self.grid.attach(label, 0, self.row, 2, 1)
        self.row += 1

    def add_field(self, text, widget, section, key, getter):
        self.grid.attach(Gtk.Label(label=text, halign=Gtk.Align.START), 0, self.row, 1, 1)
        fixed_size = isinstance(widget, (Gtk.SpinButton, Gtk.CheckButton))
        widget.set_halign(Gtk.Align.START if fixed_size else Gtk.Align.FILL)
        self.grid.attach(widget, 1, self.row, 1, 1)
        self.fields[(section, key)] = (widget, getter)
        self.row += 1

    def values(self):
        return {key: getter(widget) for key, (widget, getter) in self.fields.items()}
