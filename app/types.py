from dataclasses import dataclass
from typing import List


@dataclass
class ParsedCommand:
    name: str
    args: List[str]
    stdout_redirect_path: str | None = None
    stderr_redirect_path: str | None = None

    @property
    def args_with_name(self) -> List[str]:
        return [self.name, *self.args]

    @property
    def is_empty(self) -> bool:
        return self.name == ""
