from .types import ParsedCommand


class ParseSyntaxError(Exception):
    pass


def parse_input(line: str) -> ParsedCommand:
    parts = split_input(line)
    return ParsedCommand(name=parts[0], args=parts[1:])


def split_input(line: str) -> list[str]:
    return extract_quotes(line)


def extract_quotes(line: str) -> list[str]:
    if line.count("'") % 2 == 0:
        # Split on spaces until we reach a single quote, then add until the next single quote
        res = []
        start = 0
        inside_single_quotes = False
        for i, char in enumerate(line):
            if char == "'":
                res.append(line[start:i])
                start = i + 1
                inside_single_quotes = not inside_single_quotes
            # Collapse spaces outside single quotes
            elif char == " " and not inside_single_quotes:
                while line[i + 1] == " ":
                    line = line[: i + 1] + line[i + 2 :]
        if start < len(line):
            res.append(line[start:])
        return res
    else:
        raise ParseSyntaxError("unterminated single quote")
