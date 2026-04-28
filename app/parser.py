from .types import ParsedCommand


class ParseSyntaxError(Exception):
    pass


def parse_input(line: str) -> ParsedCommand:
    parts = split_tokens(line)

    stdout_redirect_path = None
    stderr_redirect_path = None
    stdout_redirect_append = False
    stderr_redirect_append = False

    command_parts: list[str] = []

    i = 0
    while i < len(parts):
        tok = parts[i]
        if tok in {">", "1>", ">>", "1>>"}:
            if i + 1 >= len(parts):
                raise ParseSyntaxError("missing redirect file")
            stdout_redirect_path = parts[i + 1]
            stdout_redirect_append = tok in {"1>>", ">>"}
            i += 2
            continue
        elif tok in {"2>", "2>>"}:
            if i + 1 >= len(parts):
                raise ParseSyntaxError("missing redirect file")
            stderr_redirect_path = parts[i + 1]
            stderr_redirect_append = tok == "2>>"
            i += 2
            continue

        command_parts.append(tok)
        i += 1

    is_background = False
    if command_parts and command_parts[-1] == "&":
        command_parts.pop()
        is_background = True

    return ParsedCommand(
        name=command_parts[0] if command_parts else "",
        args=command_parts[1:] if command_parts else [],
        stdout_redirect_path=stdout_redirect_path,
        stdout_redirect_append=stdout_redirect_append,
        stderr_redirect_path=stderr_redirect_path,
        stderr_redirect_append=stderr_redirect_append,
        is_background=is_background,
    )


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
