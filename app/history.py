command_history: list[str] = []
unstaged: list[str] = []


def add_entry(entry: str) -> None:
    command_history.append(entry)
    unstaged.append(entry)


def add_entries(entries: list[str]) -> None:
    command_history.extend(entries)


def history(args) -> None:

    first_arg = args[0] if args else None

    if first_arg == "-r":
        try:
            _read_history(args[1])
        except IndexError:
            raise ValueError("history: too few arguments")
        return
    elif first_arg == "-w":
        try:
            _write_history(args[1])
        except IndexError:
            raise ValueError("history: too few arguments")
        return
    elif first_arg == "-a":
        try:
            _append_history(args[1])
        except IndexError:
            raise ValueError("history: too few arguments")
        return
    else:
        if args:
            try:
                k_most_recent = int(args[0])
            except ValueError:
                raise ValueError("history: invalid argument")
        else:
            k_most_recent = len(command_history)
        _print_history(command_history, k_most_recent)


def _read_history(path: str) -> None:
    with open(path, "r") as f:
        history = f.read().splitlines()
        add_entries(history)
    return


def _write_history(path: str) -> None:
    with open(path, "w") as f:
        for entry in command_history:
            f.write(entry + "\n")


def _append_history(path: str) -> None:
    with open(path, "a") as f:
        for entry in unstaged:
            f.write(entry + "\n")
    unstaged.clear()


def _print_history(entries: list[str], k_most_recent: int) -> None:
    for i, entry in enumerate(entries):
        if i < len(entries) - k_most_recent:
            continue
        print(f"  {i + 1}  {entry}")
