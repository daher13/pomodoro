import argparse
import json

from .actions import ACTIONS, apply_action
from .status import current_status


def main():
    parser = argparse.ArgumentParser(prog="pomodoro")
    parser.add_argument("command", nargs="?", default="status",
                        choices=["status", "window", *ACTIONS])
    args = parser.parse_args()

    if args.command == "status":
        print(json.dumps(current_status()))
    elif args.command == "window":
        from .window import show_window  # lazy: GTK is slow to import
        show_window()
    else:
        apply_action(args.command)
