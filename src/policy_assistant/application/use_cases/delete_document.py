from uuid import UUID

from policy_assistant.domain.interfaces.document_repository import DocumentRepository
from policy_assistant.domain.interfaces.chunk_repository import ChunkRepository
from policy_assistant.domain.interfaces.vector_store import VectorStore


class DeleteDocumentUseCase:

    def __init__(
        self,
        document_repository: DocumentRepository,
        chunk_repository: ChunkRepository,
        vector_store: VectorStore,
    ):
        self.document_repository = document_repository
        self.chunk_repository = chunk_repository
        self.vector_store = vector_store

    def execute(self, document_id: UUID) -> bool:

        document = self.document_repository.get_by_id(document_id)

        if document is None:
            return False

        self.vector_store.delete_by_document_id(document_id)

        self.chunk_repository.delete_by_document_id(document_id)

        self.document_repository.delete(document_id)

        return True