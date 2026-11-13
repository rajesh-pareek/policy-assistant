from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass
class Chunk:
    document_id: UUID
    content: str
    page_number: int
    chunk_index: int
    id: UUID = field(default_factory=uuid4)