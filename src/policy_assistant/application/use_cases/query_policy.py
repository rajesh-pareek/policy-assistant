from policy_assistant.domain.interfaces.document_repository import DocumentRepository
from policy_assistant.domain.interfaces.embedding_provider import EmbeddingProvider
from policy_assistant.domain.interfaces.llm_provider import LLMProvider
from policy_assistant.domain.interfaces.vector_store import VectorStore

from policy_assistant.application.use_cases.query_result import (
    QueryPolicyResult,
    SourceReference,
)


class QueryPolicyUseCase:

    def __init__(
        self,
        embedding_provider: EmbeddingProvider,
        vector_store: VectorStore,
        document_repository: DocumentRepository,
        llm_provider: LLMProvider,
        similarity_threshold: float,
        top_k: int = 5,
    ):
        self.embedding_provider = embedding_provider
        self.vector_store = vector_store
        self.document_repository = document_repository
        self.llm_provider = llm_provider
        self.similarity_threshold = similarity_threshold
        self.top_k = top_k

    def execute(self, question: str) -> QueryPolicyResult:

        if not question or not question.strip():
            raise ValueError("Question cannot be empty.")

        query_embedding = self.embedding_provider.embed_text(question)

        retrieved_chunks = self.vector_store.search(
            query_embedding=query_embedding,
            top_k=self.top_k,
        )

        relevant_chunks = [
            (chunk, score)
            for chunk, score in retrieved_chunks
            if score >= self.similarity_threshold
        ]

        if not relevant_chunks:
            return QueryPolicyResult(
                answer="I couldn't find relevant information in the available policies.",
                sources=[],
            )

        documents = {}
        valid_chunks = []

        for chunk, score in relevant_chunks:

            document_id = chunk.document_id

            if document_id not in documents:
                documents[document_id] = (
                    self.document_repository.get_by_id(document_id)
                )

            document = documents[document_id]

            if document is None or document.status != "active":
                continue

            valid_chunks.append((chunk, document))

        if not valid_chunks:
            return QueryPolicyResult(
                answer="I couldn't find relevant information in the available policies.",
                sources=[],
            )

        context_parts = []
        sources = []

        seen_sources = set()

        for chunk, document in valid_chunks:

            context_parts.append(
                f"Source: {document.file_name}, "
                f"Version: {document.version}, "
                f"Page: {chunk.page_number}\n"
                f"Content: {chunk.content}"
            )

            source_key = (document.id, chunk.page_number)

            if source_key not in seen_sources:
                sources.append(
                    SourceReference(
                        document_id=document.id,
                        file_name=document.file_name,
                        document_version=document.version,
                        page_number=chunk.page_number,
                    )
                )
                seen_sources.add(source_key)

        context = "\n\n".join(context_parts)

        answer = self.llm_provider.generate_answer(
            question=question,
            context=context,
        )

        return QueryPolicyResult(
            answer=answer,
            sources=sources,
        )