import subprocess
from contextlib import ExitStack, redirect_stderr, redirect_stdout

from .builtins import BUILT_IN_COMMANDS
from .jobs import add_job
from .types import ParsedCommand, Pipeline


def run_command(command: ParsedCommand) -> None:
    if command.is_empty:
        return

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


def run_pipeline(pipe: Pipeline) -> None:
    procs = []
    prev_out = None

    with ExitStack() as stack:
        for i, command in enumerate(pipe.commands):
            if i == 0:
                stdin = None
            else:
                stdin = prev_out if prev_out is not None else subprocess.DEVNULL

            if i == len(pipe.commands) - 1:
                stdout = None
            else:
                stdout = subprocess.PIPE

            stderr = None

            if command.stdout_redirect_path is not None:
                mode = "a" if command.stdout_redirect_append else "w"
                stdout = stack.enter_context(open(command.stdout_redirect_path, mode))

            if command.stderr_redirect_path is not None:
                mode = "a" if command.stderr_redirect_append else "w"
                stderr = stack.enter_context(open(command.stderr_redirect_path, mode))

            p = subprocess.Popen(
                command.args_with_name, stdin=stdin, stdout=stdout, stderr=stderr
            )
            procs.append(p)

            if prev_out is not None:
                prev_out.close()

            prev_out = p.stdout if stdout == subprocess.PIPE else None

        if pipe.is_background:
            add_job(pipe.commands[-1], procs[-1])
        else:
            for p in procs:
                p.wait()


def _run_with_output(command: ParsedCommand, stdout_target, stderr_target) -> None:
    # Check if it's a builtin
    if command.name in BUILT_IN_COMMANDS:
        BUILT_IN_COMMANDS[command.name](command.args)

    # Otherwise, try to run it as an external command
    else:
        try:
            if command.is_background:
                proc = subprocess.Popen(
                    command.args_with_name, stdout=stdout_target, stderr=stderr_target
                )
                add_job(command, proc)
            else:
                subprocess.run(
                    command.args_with_name, stdout=stdout_target, stderr=stderr_target
                )
        except FileNotFoundError:
            print(f"{command.name}: not found")
        except PermissionError:
            print(f"{command.name}: permission denied")
