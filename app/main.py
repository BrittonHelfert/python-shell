import os
import readline
import subprocess
import sys
from contextlib import ExitStack, redirect_stderr, redirect_stdout
from pathlib import Path
from typing import Callable

from .parser import parse_input
from .types import BackgroundJob, ParsedCommand

BUILT_IN_COMMANDS: dict[str, Callable[[list[str]], None]] = {
    "exit": lambda args: sys.exit(0),
    "echo": lambda args: print(" ".join(args)),
    "type": lambda args: print(check_type(" ".join(args))),
    "pwd": lambda args: print(os.getcwd()),
    "cd": lambda args: cd(" ".join(args)),
    "jobs": lambda args: list_jobs(),
}

path = os.environ.get("PATH")
curr_background_num = 1
background_jobs: list[BackgroundJob] = []


def cd(path: str) -> None:
    try:
        os.chdir(os.path.expanduser(path))
    except FileNotFoundError:
        print(f"cd: {path}: No such file or directory")
    except Exception as e:
        print(f"{path}: {e}")


def list_jobs() -> None:
    for job in background_jobs:
        status = "Running" + " " * 17 if job.proc.poll() is None else "Done" + " " * 20
        print(f"[{job.num}]{job.marker}  {status}  {job.command}")
    # remove completed jobs
    remove_completed_jobs()


def assign_markers() -> None:
    for i, job in enumerate(background_jobs):
        if i == len(background_jobs) - 1:
            job.marker = "+"
        elif i == len(background_jobs) - 2:
            job.marker = "-"
        else:
            job.marker = " "


def remove_completed_jobs(print_each: bool = False) -> None:
    assign_markers()
    for job in background_jobs:
        if job.proc.poll() is not None:
            if print_each:
                print(f"[{job.num}]{job.marker}  Done{' ' * 20}{job.command}")
            background_jobs.remove(job)


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
                global curr_background_num
                proc = subprocess.Popen(
                    command.args_with_name, stdout=stdout_target, stderr=stderr_target
                )
                background_jobs.append(
                    BackgroundJob(
                        proc=proc, num=curr_background_num, command=command.raw_command
                    )
                )
                print(f"[{curr_background_num}] {proc.pid}")
                curr_background_num += 1
                assign_markers()
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
        remove_completed_jobs(print_each=True)


if __name__ == "__main__":
    main()
