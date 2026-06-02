from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class VectorPoint:
    id: str
    vector: list[float]
    payload: dict


@dataclass
class SearchResult:
    id: str
    score: float
    payload: dict


class VectorStoreAdapter(ABC):
    @abstractmethod
    def upsert(self, points: list[VectorPoint]) -> None:
        """Insert or update vector points."""
        ...

    @abstractmethod
    def search(self, query_vector: list[float], document_id: str, top_k: int) -> list[SearchResult]:
        """Similarity search filtered by document_id."""
        ...

    @abstractmethod
    def delete_document(self, document_id: str) -> int:
        """Delete all points for a document. Returns deleted count."""
        ...

    @abstractmethod
    def health_check(self) -> bool:
        """Return True if the store is reachable."""
        ...
