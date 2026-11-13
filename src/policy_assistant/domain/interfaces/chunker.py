from typing import Protocol
from uuid import UUID

from policy_assistant.domain.entities.chunk import Chunk
from policy_assistant.domain.entities.extracted_page import ExtractedPage


class Chunker(Protocol):

    def create_chunks(
        self,
        pages: list[ExtractedPage],
        document_id: UUID,
    ) -> list[Chunk]:
        ...