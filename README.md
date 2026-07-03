# pyshell

A small POSIX-style shell written in Python. Handles the usual interactive-shell surface area — quoting, pipelines, redirection (`>`, `>>`, `2>`, `2>>`), background jobs, parameter expansion (`$VAR`, `${VAR}`), shell variables via `declare`, tab completion, and persistent history — along with the common builtins (`cd`, `pwd`, `echo`, `type`, `jobs`, `history`, `complete`, `declare`, `exit`). Unix-like systems only (uses `readline`).

## Run

```sh
uv run python -m app.main
```
