from .types import ParsedCommand


class ParseSyntaxError(Exception):
    pass


def parse_input(line: str) -> ParsedCommand:
    if line.strip() == "":
        return ParsedCommand(name="", args=[])
    parts = split_tokens(line)
    return ParsedCommand(name=parts[0], args=parts[1:])


def split_tokens(line: str) -> list[str]:
    # Treat quoted strings as one token, otherwise split on spaces
    res = []
    curr_token = ""
    inside_single_quotes = False
    for char in line:
        if char == "'":
            inside_single_quotes = not inside_single_quotes
        elif char == " ":
            if inside_single_quotes:
                curr_token += char
            else:
                if curr_token:
                    res.append(curr_token)
                    curr_token = ""
        else:
            curr_token += char
    if curr_token:
        res.append(curr_token)
    if inside_single_quotes:
        raise ParseSyntaxError("unterminated single quote")
    return res
