import os
import readline
from operator import add

from .builtins import BUILT_IN_COMMANDS
from .executor import run_command, run_pipeline
from .history import add_entry
from .jobs import remove_completed_jobs
from .parser import parse_input
from .types import Pipeline

EXECUTABLES_CACHE: list[str] = []


def completer(text, state):
    token_start = readline.get_begidx()
    completing_command_name = token_start == 0

    dir_part = text.rsplit("/", 1)[0] + "/" if "/" in text else None
    prefix = text.rsplit("/", 1)[1] if "/" in text else text
    options = []
    if dir_part is not None:
        if not os.path.isdir(dir_part):
            return None
        options.extend([entry.name for entry in os.scandir(dir_part)])
    else:
        options.extend([entry.name for entry in os.scandir(".")])

    # if text is empty, only show dirs and files
    if completing_command_name and dir_part is None:
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
