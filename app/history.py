command_history: list[str] = []


def add_entry(entry: str) -> None:
    command_history.append(entry)


def get_history() -> list[str]:
    return command_history
