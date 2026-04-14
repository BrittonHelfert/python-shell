from dataclasses import dataclass
from typing import List


@dataclass
class ParsedCommand:
    name: str
    args: List[str]

    @property
    def args_list(self) -> List[str]:
        return [self.name, *self.args]

    @property
    def is_empty(self) -> bool:
        return self.name == ""
