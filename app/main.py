import os
import subprocess
import sys
from typing import Callable

from .parser import parse_input
from .types import ParsedCommand

COMMANDS: dict[str, Callable[[list[str]], None]] = {
    "exit": lambda args: sys.exit(0),
    "echo": lambda args: print("".join(args)),
    "type": lambda args: print(check_type(" ".join(args))),
    "pwd": lambda args: print(os.getcwd()),
    "cd": lambda args: cd(" ".join(args)),
}


def cd(path: str) -> None:
    try:
        os.chdir(os.path.expanduser(path))
    except FileNotFoundError:
        print(f"cd: {path}: No such file or directory")
    except Exception as e:
        print(f"{path}: {e}")


def get_path_of_external_command(command: str) -> str | None:
    env_path = os.getenv("PATH")
    if env_path is not None:
        for p in env_path.split(os.pathsep):
            if os.path.exists(os.path.join(p, command)):
                if os.access(os.path.join(p, command), os.X_OK):
                    return os.path.join(p, command)
    return None


def check_type(command: str) -> str:
    if command in COMMANDS:
        return f"{command} is a shell builtin"
    else:
        path = get_path_of_external_command(command)
        if path is not None:
            return f"{command} is {path}"
    return f"{command}: not found"


def run_command(command: ParsedCommand) -> None:
    # Check if it's a builtin
    if command.name in COMMANDS:
        COMMANDS[command.name](command.args)

    # Otherwise, try to run it as an external command
    else:
        try:
            subprocess.run(command.args_with_name)
        except FileNotFoundError:
            print(f"{command.name}: not found")
        except PermissionError:
            print(f"{command.name}: permission denied")
        except Exception as e:
            print(f"{command.name}: {e}")


def main():
    while True:
        sys.stdout.write("$ ")

        line = input()
        command = parse_input(line)

        run_command(command)


if __name__ == "__main__":
    main()
