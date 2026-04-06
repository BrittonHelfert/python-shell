import sys

COMMANDS = {
    "exit": lambda line: sys.exit(0),
    "echo": lambda line: print(line[5:]),
    "type": lambda line: (
        print(f"{line[5:]} is a shell builtin")
        if line[5:] in COMMANDS
        else print(f"{line[5:]}: not found")
    ),
}


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
