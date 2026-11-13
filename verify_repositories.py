
from tempfile import TemporaryDirectory
from uuid import uuid4

from policy_assistant.domain.entities.chunk import Chunk
from policy_assistant.domain.entities.document import Document
from policy_assistant.infrastructure.persistence.sqlite_database import (
    SQLiteDatabase,
)
from policy_assistant.infrastructure.persistence.sqlite_document_repository import (
    SQLiteDocumentRepository,
)
from policy_assistant.infrastructure.persistence.sqlite_chunk_repository import (
    SQLiteChunkRepository,
)


with TemporaryDirectory() as temp_dir:
    database = SQLiteDatabase(f"{temp_dir}/test.db")
    database.initialize()

    document_repository = SQLiteDocumentRepository(database)
    chunk_repository = SQLiteChunkRepository(database)

    document = Document(file_name="leave_policy.pdf")

    chunks = [
        Chunk(
            document_id=document.id,
            content="Employees receive 20 annual leaves.",
            page_number=1,
            chunk_index=0,
        ),
        Chunk(
            document_id=document.id,
            content="Employees receive 10 sick leaves.",
            page_number=2,
            chunk_index=1,
        ),
    ]

    # Save document and chunks
    document_repository.save(document)
    chunk_repository.save_many(chunks)

    print("Saved document:", document.file_name)
    print("Saved chunks:", len(chunk_repository.get_by_document_id(document.id)))

    # Update document status without deleting its chunks
    document.status = "active"
    document_repository.save(document)

    retrieved_document = document_repository.get_by_id(document.id)
    retrieved_chunks = chunk_repository.get_by_document_id(document.id)

    assert retrieved_document.status == "active"
    assert len(retrieved_chunks) == 2

    print("Updated status:", retrieved_document.status)
    print("Chunks after document update:", len(retrieved_chunks))

    # Verify document listing
    all_documents = document_repository.get_all()
    assert len(all_documents) == 1

    print("Documents retrieved:", len(all_documents))

    # Delete document and verify cascade deletion
    document_repository.delete(document.id)

    assert document_repository.get_by_id(document.id) is None
    assert chunk_repository.get_by_document_id(document.id) == []

    print("Documents after deletion:", len(document_repository.get_all()))
    print("Chunks after deletion:", len(chunk_repository.get_by_document_id(document.id)))

    print("\nAll SQLite repository verification checks passed.")
