
from policy_assistant.domain.interfaces.document_repository import DocumentRepository
from policy_assistant.domain.interfaces.embedding_provider import EmbeddingProvider
from policy_assistant.domain.interfaces.llm_provider import LLMProvider
from policy_assistant.domain.interfaces.vector_store import VectorStore

from policy_assistant.application.use_cases.query_result import (
    QueryPolicyResult,
    SourceReference,
)
from policy_assistant.application.services.output_guardrail import (
    OutputGuardrail,
)
from policy_assistant.application.services.input_guardrail import (
    InputGuardrail,
)
from policy_assistant.application.services.context_guardrail import (
    ContextGuardrail,
)


class QueryPolicyUseCase:

    def __init__(
        self,
        embedding_provider: EmbeddingProvider,
        vector_store: VectorStore,
        document_repository: DocumentRepository,
        llm_provider: LLMProvider,
        output_guardrail: OutputGuardrail,
        input_guardrail: InputGuardrail,
        context_guardrail: ContextGuardrail,
        similarity_threshold: float,
        top_k: int = 5,
    ):
        self.embedding_provider = embedding_provider
        self.vector_store = vector_store
        self.document_repository = document_repository
        self.llm_provider = llm_provider
        self.output_guardrail = output_guardrail
        self.input_guardrail = input_guardrail
        self.context_guardrail = context_guardrail
        self.similarity_threshold = similarity_threshold
        self.top_k = top_k

    def execute(self, question: str) -> QueryPolicyResult:

        # 1. Validate user input.
        guardrail_result = self.input_guardrail.validate(question)

        if not guardrail_result.is_safe:
            raise ValueError(
                "Question rejected by input security validation."
            )

        # 2. Generate query embedding.
        query_embedding = self.embedding_provider.embed_text(question)

        # 3. Retrieve relevant chunks.
        retrieved_chunks = self.vector_store.search(
            query_embedding=query_embedding,
            top_k=self.top_k,
        )

        # 4. Filter chunks using the similarity threshold.
        relevant_chunks = [
            (chunk, score)
            for chunk, score in retrieved_chunks
            if score >= self.similarity_threshold
        ]

        # Diagnostic logging: inspect threshold filtering.
        print(
            f"[DEBUG] Chunks after threshold "
            f"({self.similarity_threshold}): {len(relevant_chunks)}"
        )

        if not relevant_chunks:
            return QueryPolicyResult(
                answer="I couldn't find relevant information in the available policies.",
                sources=[],
            )

        # 5. Validate that retrieved chunks belong to active documents.
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

        # 6. Validate retrieved chunks using the context guardrail.
        context_guardrail_result = self.context_guardrail.validate(
            [chunk for chunk, document in valid_chunks]
        )

        safe_chunk_ids = {
            chunk.id
            for chunk in context_guardrail_result.safe_chunks
        }

        valid_chunks = [
            (chunk, document)
            for chunk, document in valid_chunks
            if chunk.id in safe_chunk_ids
        ]

        # Abstain if every retrieved chunk was rejected.
        if not valid_chunks:
            return QueryPolicyResult(
                answer="I couldn't find relevant information in the available policies.",
                sources=[],
            )

        # 7. Construct context and source references from safe chunks only.
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

        # 8. Generate answer using the LLM.
        answer = self.llm_provider.generate_answer(
            question=question,
            context=context,
        )

        # 9. Validate the generated answer.
        guardrail_result = self.output_guardrail.validate(answer)

        if not guardrail_result.is_safe:
            answer = (
                "I couldn't provide this response because "
                "it did not pass security validation."
            )

        return QueryPolicyResult(
            answer=answer,
            sources=sources,
        )
