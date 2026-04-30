import os
import shutil
import sys
from typing import Callable

from .history import get_history
from .jobs import list_jobs

BUILT_IN_COMMANDS: dict[str, Callable[[list[str]], None]] = {
    "exit": lambda args: sys.exit(0),
    "echo": lambda args: print(" ".join(args)),
    "type": lambda args: print(check_type(" ".join(args))),
    "pwd": lambda args: print(os.getcwd()),
    "cd": lambda args: cd(" ".join(args)),
    "jobs": lambda args: list_jobs(),
    "history": lambda args: print_history(args),
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


def print_history(args) -> None:
    history = get_history()
    k_most_recent = len(history)

    if args:
        if len(args) > 1:
            raise ValueError("history: too many arguments")
        elif isinstance(args[0], int):
            if args[0] > len(get_history()):
                raise ValueError("history: index out of range")
            else:
                k_most_recent = args[0]
        else:
            raise ValueError("history: invalid argument")

    for i, entry in enumerate(get_history()):
        if i < len(history) - k_most_recent:
            continue
        print(f"  {i + 1}  {entry}")
