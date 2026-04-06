import sys


def main():
    while True:
        sys.stdout.write("$ ")
        command = input()
        if command == "exit":
            break
        if command.split(" ")[0] == "echo"
            print(command[5:])
        print(f"{command}: command not found")


if __name__ == "__main__":
    main()
