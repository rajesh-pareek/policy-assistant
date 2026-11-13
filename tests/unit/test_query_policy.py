from uuid import uuid4

import pytest

from policy_assistant.application.use_cases.query_policy import (
    QueryPolicyUseCase,
)
from policy_assistant.domain.entities.chunk import Chunk
from policy_assistant.domain.entities.document import Document


class FakeEmbeddingProvider:
    def embed_text(self, text):
        return [0.1, 0.2, 0.3]


class FakeVectorStore:
    def __init__(self, results):
        self.results = results

    def search(self, query_embedding, top_k):
        return self.results


class FakeDocumentRepository:
    def __init__(self, documents):
        self.documents = documents

    def get_by_id(self, document_id):
        return self.documents.get(document_id)


class FakeLLMProvider:
    def generate_answer(self, question, context):
        return "Employees receive 20 annual leaves."


def create_use_case(results, documents):
    return QueryPolicyUseCase(
        embedding_provider=FakeEmbeddingProvider(),
        vector_store=FakeVectorStore(results),
        document_repository=FakeDocumentRepository(documents),
        llm_provider=FakeLLMProvider(),
        similarity_threshold=0.65,
        top_k=5,
    )


def test_active_document_returns_answer_and_source():
    document = Document(
        file_name="leave_policy.pdf",
        status="active",
    )
    chunk = Chunk(
        document_id=document.id,
        content="Employees receive 20 annual leaves.",
        page_number=1,
        chunk_index=0,
    )

    use_case = create_use_case(
        results=[(chunk, 0.85)],
        documents={document.id: document},
    )

    result = use_case.execute("How many annual leaves?")

    assert result.answer == "Employees receive 20 annual leaves."
    assert len(result.sources) == 1
    assert result.sources[0].file_name == "leave_policy.pdf"
    assert result.sources[0].page_number == 1


def test_inactive_document_is_excluded():
    document = Document(
        file_name="old_policy.pdf",
        status="inactive",
    )
    chunk = Chunk(
        document_id=document.id,
        content="Employees receive 15 annual leaves.",
        page_number=1,
        chunk_index=0,
    )

    use_case = create_use_case(
        results=[(chunk, 0.85)],
        documents={document.id: document},
    )

    result = use_case.execute("How many annual leaves?")

    assert result.sources == []
    assert "couldn't find relevant information" in result.answer


def test_low_similarity_score_causes_abstention():
    document = Document(
        file_name="leave_policy.pdf",
        status="active",
    )
    chunk = Chunk(
        document_id=document.id,
        content="Employees receive 20 annual leaves.",
        page_number=1,
        chunk_index=0,
    )

    use_case = create_use_case(
        results=[(chunk, 0.40)],
        documents={document.id: document},
    )

    result = use_case.execute("What is the maternity leave policy?")

    assert result.sources == []
    assert "couldn't find relevant information" in result.answer


def test_empty_question_is_rejected():
    use_case = create_use_case(
        results=[],
        documents={},
    )

    with pytest.raises(ValueError, match="Question cannot be empty"):
        use_case.execute("   ")