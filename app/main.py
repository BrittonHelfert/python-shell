import os
import readline
import subprocess
import sys
from contextlib import ExitStack, redirect_stderr, redirect_stdout
from pathlib import Path
from typing import Callable

from .parser import parse_input
from .types import ParsedCommand

BUILT_IN_COMMANDS: dict[str, Callable[[list[str]], None]] = {
    "exit": lambda args: sys.exit(0),
    "echo": lambda args: print(" ".join(args)),
    "type": lambda args: print(check_type(" ".join(args))),
    "pwd": lambda args: print(os.getcwd()),
    "cd": lambda args: cd(" ".join(args)),
    "jobs": lambda args: list_jobs(),
}

path = os.environ.get("PATH")
background_jobs = []


def cd(path: str) -> None:
    try:
        os.chdir(os.path.expanduser(path))
    except FileNotFoundError:
        print(f"cd: {path}: No such file or directory")
    except Exception as e:
        print(f"{path}: {e}")


def list_jobs() -> None:
    for i, job_and_command in enumerate(background_jobs):
        status = (
            "Running" + " " * 17
            if job_and_command[0].poll() is None
            else "Done" + " " * 20
        )
        marker = ""
        if i == len(background_jobs) - 1:
            marker = "+"
        if i == len(background_jobs) - 2:
            marker = "-"
        print(f"[{i + 1}]{marker}  {status}  {job_and_command[1]}")


def get_path_of_external_command(command: str) -> str | None:
    if path is not None:
        for p in path.split(os.pathsep):
            if os.path.exists(os.path.join(p, command)):
                if os.access(os.path.join(p, command), os.X_OK):
                    return os.path.join(p, command)
    return None


def check_type(command: str) -> str:
    if command in BUILT_IN_COMMANDS:
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
    if command.name in BUILT_IN_COMMANDS:
        BUILT_IN_COMMANDS[command.name](command.args)

    # Otherwise, try to run it as an external command
    else:
        try:
            if command.is_background:
                global background_job_num
                proc = subprocess.Popen(
                    command.args_with_name, stdout=stdout_target, stderr=stderr_target
                )
                background_jobs.append([proc, command.raw_command])
                print(f"[{len(background_jobs)}] {proc.pid}")
            else:
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
    options = []
    options.extend([str(entry) for entry in Path(".").rglob("*")])
    # if text is empty, only show dirs and files
    if text:
        # builtins
        options.extend(BUILT_IN_COMMANDS.keys())
        # path executables
        if path is not None:
            dirs = path.split(os.pathsep)
            for d in dirs:
                if os.path.exists(d):
                    for f in os.listdir(d):
                        if os.path.isfile(os.path.join(d, f)) and os.access(
                            os.path.join(d, f), os.X_OK
                        ):
                            options.append(f)
    matches = sorted(s for s in options if s.startswith(text))
    if state < len(matches):
        match = matches[state]
        if os.path.isdir(match):
            return match + "/"
        else:
            return match + " "

    return None


def main():

    readline.set_completer(completer)
    readline.set_completer_delims(" \n")
    readline.parse_and_bind("tab: complete")

    while True:
        line = input("$ ")
        command = parse_input(line)

        run_command(command)


if __name__ == "__main__":
    main()
