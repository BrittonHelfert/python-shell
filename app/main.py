import os
import readline
import subprocess

from .builtins import BUILT_IN_COMMANDS, COMPLETION_SCRIPT_REGISTRY
from .executor import run_command, run_pipeline
from .history import add_entry, read_history
from .jobs import remove_completed_jobs
from .parser import parse_input
from .types import Pipeline

EXECUTABLES_CACHE: list[str] = []

COMPLETIONS_CACHE: dict[str, list[str]] = {}

"""When the user types a command name followed by a space and presses TAB,
your shell should first check whether a completer is registered for that command.
If one is registered:

1) Run the script as a separate process
2) Read its stdout
3) Use each line of output as a completion candidate"""


def run_completion_script(script: str) -> list[str]:
    result = subprocess.run(script, capture_output=True, text=True)
    res = result.stdout.splitlines() if result.returncode == 0 else []
    return res


def completer(text, state):
    line_buffer = readline.get_line_buffer()
    token_start = readline.get_begidx()
    completing_command_name = token_start == 0
    command_name = line_buffer.split(" ")[0] if line_buffer else ""
    use_command_completer = (
        not completing_command_name and command_name in COMPLETION_SCRIPT_REGISTRY
    )

    dir_part = text.rsplit("/", 1)[0] + "/" if "/" in text else None
    prefix = text.rsplit("/", 1)[1] if "/" in text else text
    options = []

    if use_command_completer:
        if command_name not in COMPLETIONS_CACHE:
            COMPLETIONS_CACHE[command_name] = run_completion_script(
                COMPLETION_SCRIPT_REGISTRY[command_name]
            )
        options.extend(COMPLETIONS_CACHE[command_name])

    if not use_command_completer:
        if dir_part is not None:
            if not os.path.isdir(dir_part):
                return None
            options.extend([entry.name for entry in os.scandir(dir_part)])
        else:
            options.extend([entry.name for entry in os.scandir(".")])

    # if text is empty, only show dirs and files
    if completing_command_name and dir_part is None and not use_command_completer:
        # builtins
        options.extend(BUILT_IN_COMMANDS.keys())
        # path executables
        options.extend(EXECUTABLES_CACHE)
    matches = sorted(s for s in options if s.startswith(prefix))
    if state < len(matches):
        match = matches[state]
        output = dir_part + match if dir_part is not None else match
        if os.path.isdir(output):
            return output + "/"
        else:
            return output + " "

    return None


def refresh_executables_cache():
    path = os.environ.get("PATH")
    if path is not None:
        dirs = path.split(os.pathsep)
        for d in dirs:
            if os.path.exists(d):
                for f in os.listdir(d):
                    if os.path.isfile(os.path.join(d, f)) and os.access(
                        os.path.join(d, f), os.X_OK
                    ):
                        EXECUTABLES_CACHE.append(f)


def main():
    refresh_executables_cache()

    readline.set_completer(completer)
    readline.set_completer_delims(" \n")
    readline.parse_and_bind("tab: complete")

    read_history()

    while True:
        line = input("$ ")
        add_entry(line)
        command = parse_input(line)

        if isinstance(command, Pipeline):
            run_pipeline(command)
        else:
            run_command(command)

        remove_completed_jobs(print_each=True)


if __name__ == "__main__":
    main()
