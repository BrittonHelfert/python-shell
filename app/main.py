import os
import sys

COMMANDS = {
    "exit": lambda line: sys.exit(0),
    "echo": lambda line: print(line[5:]),
    "type": lambda line: print(check_type(line[5:])),
}


def get_path(command: str) -> str | None:
    if os.getenv("PATH") is not None:
        for path in os.getenv("PATH").split(os.pathsep):
            if os.path.exists(os.path.join(path, command)):
                if os.access(os.path.join(path, command), os.X_OK):
                    return os.path.join(path, command)
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
        command = input()
        if command.split(" ")[0] in COMMANDS:
            COMMANDS[command.split(" ")[0]](command)
        else:
            print(f"{command}: command not found")


if __name__ == "__main__":
    main()
