import os
import subprocess
import sys
from typing import Callable

COMMANDS: dict[str, Callable[[str], None]] = {
    "exit": lambda line: sys.exit(0),
    "echo": lambda line: print(line[5:]),
    "type": lambda line: print(check_type(line[5:])),
    "pwd": lambda line: print(os.getcwd()),
    "cd": lambda line: cd(line[3:]),
}


def cd(path: str) -> None:
    try:
        os.chdir(os.path.expanduser(path))
    except FileNotFoundError:
        print(f"cd: {path}: No such file or directory")
    except Exception as e:
        print(f"{path}: {e}")


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
        args = line.split(" ")

        command = args[0]
        if command in COMMANDS:
            COMMANDS[command](line)
            continue

        try:
            subprocess.run(args)
        except FileNotFoundError:
            print(f"{command}: not found")
        except PermissionError:
            print(f"{command}: permission denied")
        except Exception as e:
            print(f"{command}: {e}")


if __name__ == "__main__":
    main()
