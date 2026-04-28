from dataclasses import dataclass
from typing import List


@dataclass
class ParsedCommand:
    name: str
    args: List[str]
    stdout_redirect_path: str | None = None
    stdout_redirect_append: bool = False
    stderr_redirect_path: str | None = None
    stderr_redirect_append: bool = False
    is_background: bool = False

    @property
    def args_with_name(self) -> List[str]:
        return [self.name, *self.args]

    @property
    def is_empty(self) -> bool:
        return self.name == ""
