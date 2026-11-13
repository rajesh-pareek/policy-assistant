from typing import Protocol
from uuid import UUID

from policy_assistant.domain.entities.document import Document


class DocumentRepository(Protocol):

    def save(self, document: Document) -> None:
        ...

    def get_by_id(self, document_id: UUID) -> Document | None:
        ...

    def get_all(self) -> list[Document]:
        ...

    def delete(self, document_id: UUID) -> None:
        ...