from typing import Protocol
from uuid import UUID

from policy_assistant.domain.entities.chunk import Chunk


class ChunkRepository(Protocol):

    def save_many(self, chunks: list[Chunk]) -> None:
        ...

    def get_by_document_id(self, document_id: UUID) -> list[Chunk]:
        ...

    def delete_by_document_id(self, document_id: UUID) -> None:
        ...