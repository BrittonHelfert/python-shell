import os
import shutil
import sys
from typing import Callable

from .history import add_entries, get_history
from .jobs import list_jobs

BUILT_IN_COMMANDS: dict[str, Callable[[list[str]], None]] = {
    "exit": lambda args: sys.exit(0),
    "echo": lambda args: print(" ".join(args)),
    "type": lambda args: print(check_type(" ".join(args))),
    "pwd": lambda args: print(os.getcwd()),
    "cd": lambda args: cd(" ".join(args)),
    "jobs": lambda args: list_jobs(),
    "history": lambda args: history(args),
}


def cd(path: str) -> None:
    try:
        os.chdir(os.path.expanduser(path))
    except FileNotFoundError:
        print(f"cd: {path}: No such file or directory")


def check_type(command: str) -> str:
    if command in BUILT_IN_COMMANDS:
        return f"{command} is a shell builtin"
    else:
        path = shutil.which(command, mode=os.X_OK)
        if path is not None:
            return f"{command} is {path}"
    return f"{command}: not found"


def history(args) -> None:
    entries = get_history()

    k_most_recent = 0
    overwrite_path = None

    if args:
        if len(args) > 1:
            raise ValueError("history: too many arguments")
        else:
            if args[0] == "-r":
                try:
                    overwrite_path = args[1]
                except IndexError:
                    raise ValueError("history: too few arguments")
            else:
                try:
                    k_most_recent = int(args[0])
                except ValueError:
                    raise ValueError("history: invalid argument")

    if overwrite_path:
        # split file by newline, print as history, append to history
        with open(overwrite_path, "r") as f:
            entries = f.read().splitlines()
            add_entries(entries)

    _print_history(entries, k_most_recent)


def _print_history(entries: list[str], k_most_recent: int) -> None:
    for i, entry in enumerate(entries):
        if i < len(entries) - k_most_recent:
            continue
        print(f"  {i + 1}  {entry}")
