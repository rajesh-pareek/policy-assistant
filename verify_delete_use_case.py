from uuid import uuid4

from policy_assistant.domain.entities.document import Document
from policy_assistant.application.use_cases.delete_document import (
    DeleteDocumentUseCase,
)


class FakeDocumentRepository:

    def __init__(self, document):
        self.document = document
        self.deleted_ids = []

    def get_by_id(self, document_id):
        if self.document and self.document.id == document_id:
            return self.document
        return None

    def delete(self, document_id):
        self.deleted_ids.append(document_id)
        self.document = None


class FakeChunkRepository:

    def __init__(self):
        self.deleted_ids = []

    def delete_by_document_id(self, document_id):
        self.deleted_ids.append(document_id)


class FakeVectorStore:

    def __init__(self):
        self.deleted_ids = []

    def delete_by_document_id(self, document_id):
        self.deleted_ids.append(document_id)


# Scenario 1: Existing document

document = Document(
    file_name="Employee_Leave_Policy.pdf",
    status="active",
)

document_repository = FakeDocumentRepository(document)
chunk_repository = FakeChunkRepository()
vector_store = FakeVectorStore()

use_case = DeleteDocumentUseCase(
    document_repository=document_repository,
    chunk_repository=chunk_repository,
    vector_store=vector_store,
)

result = use_case.execute(document.id)

print("Deletion successful:", result)
print("Document deleted:", document_repository.document is None)
print("Chunk metadata deletion:", len(chunk_repository.deleted_ids))
print("Vector deletion:", len(vector_store.deleted_ids))


# Scenario 2: Nonexistent document

unknown_id = uuid4()

missing_document_repository = FakeDocumentRepository(None)
missing_chunk_repository = FakeChunkRepository()
missing_vector_store = FakeVectorStore()

missing_use_case = DeleteDocumentUseCase(
    document_repository=missing_document_repository,
    chunk_repository=missing_chunk_repository,
    vector_store=missing_vector_store,
)

missing_result = missing_use_case.execute(unknown_id)

print("Nonexistent document result:", missing_result)
print("Unnecessary chunk deletions:", len(missing_chunk_repository.deleted_ids))
print("Unnecessary vector deletions:", len(missing_vector_store.deleted_ids))