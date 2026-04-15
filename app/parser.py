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
    inside_double_quotes = False
    escape_next = False
    for i, char in enumerate(line):
        if escape_next:
            curr_token += char
            escape_next = False
        elif char == '"':
            if inside_single_quotes:
                curr_token += char
            else:
                inside_double_quotes = not inside_double_quotes
        elif char == "'":
            if inside_double_quotes:
                curr_token += char
            else:
                inside_single_quotes = not inside_single_quotes
        elif char == "\\":
            if inside_single_quotes:
                curr_token += char
            elif inside_double_quotes:
                if i < len(line) - 1 and line[i + 1] in {'"', "\\", "$", "`", "\n"}:
                    escape_next = True
                else:
                    curr_token += char
            else:
                escape_next = True
        elif char == " ":
            if inside_single_quotes or inside_double_quotes:
                curr_token += char
            else:
                if curr_token:
                    res.append(curr_token)
                    curr_token = ""
        else:
            curr_token += char
    if curr_token:
        res.append(curr_token)
    if inside_single_quotes or inside_double_quotes:
        raise ParseSyntaxError("unterminated quote")
    return res
