import os
import sys
from typing import Callable

COMMANDS: dict[str, Callable[[str], None]] = {
    "exit": lambda line: sys.exit(0),
    "echo": lambda line: print(line[5:]),
    "type": lambda line: print(check_type(line[5:])),
}


def get_path(command: str) -> str | None:
    path = os.getenv("PATH")
    if path is not None:
        for p in path.split(os.pathsep):
            if os.path.exists(os.path.join(p, command)):
                if os.access(os.path.join(p, command), os.X_OK):
                    return os.path.join(p, command)
    return None


def check_type(command: str) -> str:
    if command in COMMANDS:
        return f"{command} is a shell builtin"
    else:
        path = get_path(command)
        if path is not None:
            return f"{command} is {path}"
    return f"{command}: not found"


def main():
    while True:
        sys.stdout.write("$ ")
        line = input()

        command = line.split(" ")[0]
        if command in COMMANDS:
            COMMANDS[command](line)
        else:
            path = get_path(command)
            if path is not None:
                os.execv(path, line.split(" ")[1:])
            else:
                print(f"{command}: command not found")


if __name__ == "__main__":
    main()
