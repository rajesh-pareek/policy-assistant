from dataclasses import dataclass
from uuid import UUID


@dataclass
class SourceReference:
    document_id: UUID
    file_name: str
    document_version: str
    page_number: int


@dataclass
class QueryPolicyResult:
    answer: str
    sources: list[SourceReference]