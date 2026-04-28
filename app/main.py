import os
import readline
import subprocess
import sys
from contextlib import ExitStack, redirect_stderr, redirect_stdout
from typing import Callable

from .parser import parse_input
from .types import ParsedCommand

COMMANDS: dict[str, Callable[[list[str]], None]] = {
    "exit": lambda args: sys.exit(0),
    "echo": lambda args: print(" ".join(args)),
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
    with ExitStack() as stack:
        stdout_target = None
        stderr_target = None

        if command.stdout_redirect_path is not None:
            mode = "a" if command.stdout_redirect_append else "w"
            stdout_target = open(command.stdout_redirect_path, mode)
            stack.enter_context(redirect_stdout(stdout_target))

        if command.stderr_redirect_path is not None:
            mode = "a" if command.stderr_redirect_append else "w"
            stderr_target = open(command.stderr_redirect_path, mode)
            stack.enter_context(redirect_stderr(stderr_target))

        _run_with_output(command, stdout_target, stderr_target)


def _run_with_output(command: ParsedCommand, stdout_target, stderr_target) -> None:
    # Check if it's a builtin
    if command.name in COMMANDS:
        COMMANDS[command.name](command.args)

    # Otherwise, try to run it as an external command
    else:
        try:
            subprocess.run(
                command.args_with_name, stdout=stdout_target, stderr=stderr_target
            )
        except FileNotFoundError:
            print(f"{command.name}: not found")
        except PermissionError:
            print(f"{command.name}: permission denied")
        except Exception as e:
            print(f"{command.name}: {e}")


def completer(text, state):
    options = ["echo ", "exit "]
    matches = [s for s in options if s.startswith(text)]
    return matches[state] if state < len(matches) else None


def main():

    readline.set_completer(completer)
    readline.parse_and_bind("tab: complete")

    while True:
        line = input("$ ")
        command = parse_input(line)

        run_command(command)


if __name__ == "__main__":
    main()
