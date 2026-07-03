import os
import readline
import subprocess
import sys

from .builtins import BUILT_IN_COMMANDS, COMPLETION_SCRIPT_REGISTRY
from .executor import run_command, run_pipeline
from .history import add_entry, read_history
from .jobs import remove_completed_jobs
from .parser import parse_input
from .types import Pipeline

EXECUTABLES_CACHE: list[str] = []

COMPLETIONS_CACHE: dict[str, list[str]] = {}


def run_completion_script(
    script: str, command_name: str, prefix: str, previous_word: str
) -> list[str]:
    result = subprocess.run(
        [script, command_name, prefix, previous_word],
        capture_output=True,
        text=True,
    )
    return result.stdout.splitlines() if result.returncode == 0 else []


def display_matches(substitution, matches, longest_match_length, line_buffer):
    candidates = sorted(m.rstrip() for m in matches)
    sys.stdout.write("\n" + "  ".join(candidates) + "\n")
    sys.stdout.write("$ " + line_buffer)
    sys.stdout.flush()


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
        readline.set_completion_display_matches_hook(
            lambda substitution, matches, longest_match_length: display_matches(
                substitution, matches, longest_match_length, line_buffer
            )
        )
    else:
        readline.set_completion_display_matches_hook(None)

    if use_command_completer:
        os.environ["COMP_LINE"] = line_buffer
        os.environ["COMP_POINT"] = str(readline.get_endidx())
        previous_word = (
            line_buffer.split(" ")[-2] if len(line_buffer.split(" ")) > 1 else ""
        )
        COMPLETIONS_CACHE[command_name] = run_completion_script(
            COMPLETION_SCRIPT_REGISTRY[command_name],
            command_name,
            prefix,
            previous_word,
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
