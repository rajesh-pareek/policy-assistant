from typing import Protocol
from uuid import UUID

from policy_assistant.domain.entities.chunk import Chunk


class VectorStore(Protocol):

    def add(
        self,
        chunks: list[Chunk],
        embeddings: list[list[float]],
    ) -> None:
        ...

    def search(
        self,
        query_embedding: list[float],
        top_k: int,
    ) -> list[tuple[Chunk, float]]:
        ...

    def delete_by_document_id(self, document_id: UUID) -> None:
        ...