
from policy_assistant.domain.entities.document import Document
from policy_assistant.domain.entities.chunk import Chunk
from policy_assistant.domain.entities.extracted_page import ExtractedPage
from policy_assistant.application.use_cases.ingest_document import (
    IngestDocumentUseCase,
)


# Fake dependencies

class FakePDFValidator:

    def validate(self, file_path):
        if not file_path.endswith(".pdf"):
            raise ValueError("Only PDF files are allowed.")


class FakePDFExtractor:

    def extract(self, file_path):
        return [
            ExtractedPage(
                page_number=1,
                content="Employees receive 20 annual leaves.",
            )
        ]


class EmptyPDFExtractor:

    def extract(self, file_path):
        return []


class FakeChunker:

    def create_chunks(self, pages, document_id):
        return [
            Chunk(
                document_id=document_id,
                content=pages[0].content,
                page_number=pages[0].page_number,
                chunk_index=0,
            )
        ]


class TwoChunker:

    def create_chunks(self, pages, document_id):
        return [
            Chunk(
                document_id=document_id,
                content="First policy section.",
                page_number=1,
                chunk_index=0,
            ),
            Chunk(
                document_id=document_id,
                content="Second policy section.",
                page_number=2,
                chunk_index=1,
            ),
        ]


class FakeEmbeddingProvider:

    def embed_texts(self, texts):
        return [[0.1, 0.2, 0.3] for _ in texts]


class InvalidEmbeddingProvider:

    def embed_texts(self, texts):
        return [[0.1, 0.2, 0.3]]


class FakeDocumentRepository:

    def __init__(self):
        self.saved_documents = []

    def save(self, document):
        self.saved_documents.append(document)


class FakeChunkRepository:

    def __init__(self):
        self.saved_chunks = []

    def save_many(self, chunks):
        self.saved_chunks.extend(chunks)


class FakeVectorStore:

    def __init__(self):
        self.saved_chunks = []
        self.saved_embeddings = []

    def add(self, chunks, embeddings):
        self.saved_chunks.extend(chunks)
        self.saved_embeddings.extend(embeddings)


# Test 1: Successful ingestion

document = Document(
    file_name="Employee_Leave_Policy.pdf",
)

document_repository = FakeDocumentRepository()
chunk_repository = FakeChunkRepository()
vector_store = FakeVectorStore()

use_case = IngestDocumentUseCase(
    pdf_validator=FakePDFValidator(),
    pdf_extractor=FakePDFExtractor(),
    chunker=FakeChunker(),
    embedding_provider=FakeEmbeddingProvider(),
    document_repository=document_repository,
    chunk_repository=chunk_repository,
    vector_store=vector_store,
)

result = use_case.execute(
    document=document,
    file_path="sample_documents/Employee_Leave_Policy.pdf",
)

print("Document status:", result.status)
print("Document ID:", result.id)
print("Saved chunks:", len(chunk_repository.saved_chunks))
print("Stored vectors:", len(vector_store.saved_embeddings))
print("Chunk page:", chunk_repository.saved_chunks[0].page_number)
print(
    "Embeddings match chunks:",
    len(vector_store.saved_chunks) == len(vector_store.saved_embeddings),
)


# Test 2: Empty PDF rejection

failed_document = Document(
    file_name="Empty_Policy.pdf",
)

failed_document_repository = FakeDocumentRepository()
failed_chunk_repository = FakeChunkRepository()
failed_vector_store = FakeVectorStore()

failed_use_case = IngestDocumentUseCase(
    pdf_validator=FakePDFValidator(),
    pdf_extractor=EmptyPDFExtractor(),
    chunker=FakeChunker(),
    embedding_provider=FakeEmbeddingProvider(),
    document_repository=failed_document_repository,
    chunk_repository=failed_chunk_repository,
    vector_store=failed_vector_store,
)

try:
    failed_use_case.execute(
        document=failed_document,
        file_path="sample_documents/Empty_Policy.pdf",
    )
except ValueError as error:
    print("Failure validation:", error)

print("Failed document status:", failed_document.status)
print("Failed document chunks:", len(failed_chunk_repository.saved_chunks))
print("Failed document vectors:", len(failed_vector_store.saved_embeddings))


# Test 3: Embedding count mismatch

mismatch_document = Document(
    file_name="Mismatch_Policy.pdf",
)

mismatch_repository = FakeDocumentRepository()
mismatch_chunk_repository = FakeChunkRepository()
mismatch_vector_store = FakeVectorStore()

mismatch_use_case = IngestDocumentUseCase(
    pdf_validator=FakePDFValidator(),
    pdf_extractor=FakePDFExtractor(),
    chunker=TwoChunker(),
    embedding_provider=InvalidEmbeddingProvider(),
    document_repository=mismatch_repository,
    chunk_repository=mismatch_chunk_repository,
    vector_store=mismatch_vector_store,
)

try:
    mismatch_use_case.execute(
        document=mismatch_document,
        file_path="sample_documents/Mismatch_Policy.pdf",
    )
except ValueError as error:
    print("Embedding validation:", error)

print("Mismatch document status:", mismatch_document.status)
print("Mismatch saved chunks:", len(mismatch_chunk_repository.saved_chunks))
print("Mismatch stored vectors:", len(mismatch_vector_store.saved_embeddings))


# Test 4: Invalid PDF rejection

invalid_document = Document(
    file_name="Invalid_Policy.txt",
)

invalid_repository = FakeDocumentRepository()
invalid_chunk_repository = FakeChunkRepository()
invalid_vector_store = FakeVectorStore()

invalid_use_case = IngestDocumentUseCase(
    pdf_validator=FakePDFValidator(),
    pdf_extractor=FakePDFExtractor(),
    chunker=FakeChunker(),
    embedding_provider=FakeEmbeddingProvider(),
    document_repository=invalid_repository,
    chunk_repository=invalid_chunk_repository,
    vector_store=invalid_vector_store,
)

try:
    invalid_use_case.execute(
        document=invalid_document,
        file_path="sample_documents/Invalid_Policy.txt",
    )
except ValueError as error:
    print("Invalid PDF validation:", error)

print("Invalid document status:", invalid_document.status)
print("Invalid document saved:", len(invalid_repository.saved_documents))
print("Invalid document chunks:", len(invalid_chunk_repository.saved_chunks))
print("Invalid document vectors:", len(invalid_vector_store.saved_embeddings))
