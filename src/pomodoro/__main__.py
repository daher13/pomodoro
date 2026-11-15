import os

os.environ.setdefault("GTK_USE_PORTAL", "1")  # use the xdg file chooser portal

from gi.repository import GLib

from .window import PomodoroApp

def main():
    GLib.set_prgname("pomodoro")  # app-id on Wayland
    PomodoroApp().run(None)

if __name__ == "__main__":
    main()
