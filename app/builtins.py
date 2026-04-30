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

    first_arg = args[0] if args else None

    if first_arg == "-r":
        try:
            _read_history(args[1])
        except IndexError:
            raise ValueError("history: too few arguments")
        return
    elif first_arg == "-w" or first_arg == "-a":
        try:
            _write_history(first_arg[1], args[1])
        except IndexError:
            raise ValueError("history: too few arguments")
        return
    else:
        history = get_history()
        if args:
            try:
                k_most_recent = int(args[0])
            except ValueError:
                raise ValueError("history: invalid argument")
        else:
            k_most_recent = len(history)
        _print_history(history, k_most_recent)


def _read_history(path: str) -> None:
    with open(path, "r") as f:
        history = f.read().splitlines()
        add_entries(history)
    return


def _write_history(mode: str, path: str) -> None:
    with open(path, mode) as f:
        for entry in get_history():
            f.write(entry + "\n")


def _print_history(entries: list[str], k_most_recent: int) -> None:
    for i, entry in enumerate(entries):
        if i < len(entries) - k_most_recent:
            continue
        print(f"  {i + 1}  {entry}")
