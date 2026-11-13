from policy_assistant.domain.entities.document import Document
from policy_assistant.domain.interfaces.chunker import Chunker
from policy_assistant.domain.interfaces.chunk_repository import ChunkRepository
from policy_assistant.domain.interfaces.document_repository import DocumentRepository
from policy_assistant.domain.interfaces.embedding_provider import EmbeddingProvider
from policy_assistant.domain.interfaces.pdf_extractor import PDFExtractor
from policy_assistant.domain.interfaces.vector_store import VectorStore
from pathlib import Path
from policy_assistant.domain.interfaces.pdf_validator import PDFValidator

class IngestDocumentUseCase:

    def __init__(
        self,
        pdf_validator: PDFValidator,
        pdf_extractor: PDFExtractor,
        chunker: Chunker,
        embedding_provider: EmbeddingProvider,
        document_repository: DocumentRepository,
        chunk_repository: ChunkRepository,
        vector_store: VectorStore,
    ):
        self.pdf_validator = pdf_validator
        self.pdf_extractor = pdf_extractor
        self.chunker = chunker
        self.embedding_provider = embedding_provider
        self.document_repository = document_repository
        self.chunk_repository = chunk_repository
        self.vector_store = vector_store

    def execute(self, document: Document, file_path: str) -> Document:
        self.pdf_validator.validate(file_path)

        self.document_repository.save(document)

        pages = self.pdf_extractor.extract(file_path)

        if not pages or not any(page.content.strip() for page in pages):
            raise ValueError("PDF contains no extractable text.")

        chunks = self.chunker.create_chunks(
            pages=pages,
            document_id=document.id,
        )

        embeddings = self.embedding_provider.embed_texts(
            [chunk.content for chunk in chunks]
        )

        if len(embeddings) != len(chunks):
            raise ValueError(
                "The number of embeddings must match the number of chunks."
            )

        if not embeddings:
            raise ValueError("No embeddings were generated.")

        self.chunk_repository.save_many(chunks)

        self.vector_store.add(
            chunks=chunks,
            embeddings=embeddings,
        )

        document.status = "active"
        self.document_repository.save(document)

        return document