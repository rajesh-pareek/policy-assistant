from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4


@dataclass
class Document:
    file_name: str
    version: str = "1.0"
    status: str = "pending"
    id: UUID = field(default_factory=uuid4)
    uploaded_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )