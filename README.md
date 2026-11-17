# Pomodoro

Pomodoro timer with a GTK3 window. Single instance, configurable through a settings dialog or a plain `.conf` file.

![alt text](assets/screenshot.png)

## Features

- Three phases: focus, short break and long break (long break every N focus sessions)
- Segmented ring with one segment per minute of the phase (can be hidden)
- Window with Start/Pause, Prev, Next and Reset
- Beep and desktop notification when a phase ends
- Optional sound at the end of every minute, with its own sound file
- Report dialog with the completed pomodoros per day
- Settings dialog (durations, cycles, auto start, beeps, ring, sounds, data folder)
- Closing the window pauses the timer
- Opening it again focuses the existing window instead of creating a new one
- State and history persist across reboots

## Requirements

- Python 3.10+
- GTK 3 and PyGObject
- `paplay` (PulseAudio/PipeWire) and `notify-send`
- An xdg desktop portal (used by the file chooser in Settings)

Arch Linux:

```sh
sudo pacman -S gtk3 python-gobject libpulse libnotify
```

## Install

From the project root (the folder that contains `src/`):

```sh
mkdir -p ~/.local/bin
python3 -m zipapp src -m "pomodoro.__main__:main" -p "/usr/bin/env python3" -o ~/.local/bin/pomodoro
chmod +x ~/.local/bin/pomodoro
```

Make sure `~/.local/bin` is in your `PATH`. Run the `zipapp` command again after changing the code.

## Usage

```sh
pomodoro
```

| Button      | Action                                                          |
|-------------|-----------------------------------------------------------------|
| Start/Pause | Starts or pauses the current phase                              |
| Prev        | Goes back to the previous phase (paused)                        |
| Next        | Moves to the next phase (paused); leaving a focus phase counts it |
| Reset       | Resets the current phase timer, keeps the completed count       |

The top-right icons open the **Report** (pomodoros per day) and the **Settings** dialog. `Esc` closes the window.

## Configuration

Everything in the Settings dialog is saved to `~/.config/pomodoro/pomodoro.conf`. You can also edit the file by hand. Missing or invalid values fall back to the defaults below. Changes made in the dialog apply immediately.

```ini
[durations]
work = 25
short = 5
long = 15

[timer]
cycles = 4
auto_start = false

[beeps]
work = 1
short = 2
long = 3

[labels]
work = Focus
short = Short break
long = Long break

[sound]
file = /usr/share/sounds/freedesktop/stereo/message.oga
minute_enabled = false
minute_file = /usr/share/sounds/freedesktop/stereo/bell.oga

[ui]
show_ring = true

[data]
dir = ~/.local/share/pomodoro
```

- `[labels]` is only editable in the file (not in the Settings dialog).
- `[sound] file` plays when a phase ends, repeated according to `[beeps]`.
- `minute_enabled` plays `minute_file` at every minute boundary while the timer is running. It does not play at the end of a phase.
- `[data] dir` defaults to `$XDG_DATA_HOME/pomodoro` (`~/.local/share/pomodoro` when the variable is not set). It holds `state.json` and `history.json`, and is created automatically.

A stopped phase that was never started picks up a new duration right away. A phase already in progress keeps its old duration until you press Reset.

## Project structure

```
src/pomodoro/
├── __init__.py   # pins the GTK versions
├── __main__.py   # entry point (python -m pomodoro)
├── config.py     # defaults and .conf loading/saving
├── state.py      # state and history files, remaining time, phase changes
├── actions.py    # toggle, pause, next, prev, reset, reset-all
├── status.py     # phase end detection and status data
├── alerts.py     # beeps and notifications
├── window.py     # main GTK window and ring
├── settings.py   # settings dialog
└── report.py     # report dialog
```

## How it works

The state (phase, end timestamp, completed count) lives in `state.json`, and the completed pomodoros per day live in `history.json`, both inside the data folder. While running, the remaining time is computed from the end timestamp, so it stays correct even if the window is busy. The window refreshes every second and, when the timer reaches zero, advances to the next phase, plays the beep and sends a notification. The daily count restarts on a new day. There is no background process: the timer only counts while the window is open.

# Developers

## Testing light/dark themes

From the project root:

```sh
GTK_THEME=Adwaita:light PYTHONPATH=src python -m pomodoro
GTK_THEME=Adwaita:dark PYTHONPATH=src python -m pomodoro
```