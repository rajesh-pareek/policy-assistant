from uuid import uuid4

from policy_assistant.domain.entities.document import Document
from policy_assistant.domain.entities.chunk import Chunk
from policy_assistant.application.use_cases.query_policy import QueryPolicyUseCase


class FakeEmbeddingProvider:
    def embed_text(self, text):
        return [0.1, 0.2, 0.3]


class FakeVectorStore:
    def __init__(self, chunk):
        self.chunk = chunk

    def search(self, query_embedding, top_k):
        return [(self.chunk, 0.40)]


class FakeDocumentRepository:
    def __init__(self, document):
        self.document = document

    def get_by_id(self, document_id):
        return self.document if document_id == self.document.id else None


class FakeLLMProvider:
    def generate_answer(self, question, context):
        return "Employees receive 20 annual leaves per year."


document = Document(
    file_name="Employee_Leave_Policy.pdf",
    status="active",
)

chunk = Chunk(
    document_id=document.id,
    content="Employees receive 20 annual leaves per year.",
    page_number=1,
    chunk_index=0,
)

use_case = QueryPolicyUseCase(
    embedding_provider=FakeEmbeddingProvider(),
    vector_store=FakeVectorStore(chunk),
    document_repository=FakeDocumentRepository(document),
    llm_provider=FakeLLMProvider(),
    similarity_threshold=0.70,
)

try:
    use_case.execute("   ")
except ValueError as error:
    print("Validation successful:", error)