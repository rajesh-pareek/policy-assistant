
import tiktoken
from uuid import UUID

from policy_assistant.domain.entities.chunk import Chunk
from policy_assistant.domain.entities.extracted_page import ExtractedPage


class TokenChunker:
    CHUNK_SIZE = 500
    CHUNK_OVERLAP = 50
    STEP_SIZE = CHUNK_SIZE - CHUNK_OVERLAP

    def __init__(self):
        self.encoding = tiktoken.get_encoding("cl100k_base")

    def create_chunks(
        self,
        pages: list[ExtractedPage],
        document_id: UUID,
    ) -> list[Chunk]:

        chunks = []
        chunk_index = 0

        for page in pages:
            if not page.content.strip():
                continue

            tokens = self.encoding.encode(page.content)

            start = 0

            while start < len(tokens):
                end = min(start + self.CHUNK_SIZE, len(tokens))

                chunk_tokens = tokens[start:end]
                chunk_content = self.encoding.decode(chunk_tokens)

                if chunk_content.strip():
                    chunks.append(
                        Chunk(
                            document_id=document_id,
                            content=chunk_content,
                            page_number=page.page_number,
                            chunk_index=chunk_index,
                        )
                    )
                    chunk_index += 1

                if end == len(tokens):
                    break

                start += self.STEP_SIZE

        return chunks
