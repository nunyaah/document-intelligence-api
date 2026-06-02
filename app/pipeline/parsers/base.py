from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class PageText:
    page_number: int
    text: str


class BaseParser(ABC):
    @abstractmethod
    def parse(self, file_path: str) -> list[PageText]:
        """Parse a file and return list of page texts with metadata."""
        ...
