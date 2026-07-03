import sys

from .builtins import BUILT_IN_COMMANDS


def main():
    name = sys.argv[1]
    args = sys.argv[2:]
    BUILT_IN_COMMANDS[name](args)


if __name__ == "__main__":
    main()
