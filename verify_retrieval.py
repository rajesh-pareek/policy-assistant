from tempfile import TemporaryDirectory

from policy_assistant.domain.entities.document import Document
from policy_assistant.infrastructure.pdf.pypdf_extractor import PyPDFExtractor
from policy_assistant.infrastructure.chunking.token_chunker import TokenChunker
from policy_assistant.infrastructure.embeddings.sentence_transformer_provider import (
    SentenceTransformerEmbeddingProvider,
)
from policy_assistant.infrastructure.vector_store.faiss_vector_store import (
    FAISSVectorStore,
)
from policy_assistant.infrastructure.persistence.sqlite_database import (
    SQLiteDatabase,
)
from policy_assistant.infrastructure.persistence.sqlite_document_repository import (
    SQLiteDocumentRepository,
)
from policy_assistant.infrastructure.persistence.sqlite_chunk_repository import (
    SQLiteChunkRepository,
)
from policy_assistant.infrastructure.llm.gemini_llm_provider import (
    GeminiLLMProvider,
)
from policy_assistant.application.use_cases.query_policy import QueryPolicyUseCase


with TemporaryDirectory() as temp_dir:

    # 1. Initialize temporary SQLite database
    database = SQLiteDatabase(f"{temp_dir}/test.db")
    database.initialize()

    document_repository = SQLiteDocumentRepository(database)
    chunk_repository = SQLiteChunkRepository(database)

    # 2. Initialize RAG components
    extractor = PyPDFExtractor()
    chunker = TokenChunker()
    embedding_provider = SentenceTransformerEmbeddingProvider()
    vector_store = FAISSVectorStore()
    llm_provider = GeminiLLMProvider()

    # 3. Extract PDF
    pages = extractor.extract("sample_documents/test_policy.pdf")

    # 4. Save document metadata
    document = Document(
        file_name="test_policy.pdf",
        status="active",
    )
    document_repository.save(document)

    # 5. Create and persist chunks
    chunks = chunker.create_chunks(pages, document.id)
    chunk_repository.save_many(chunks)

    # 6. Generate embeddings and index them
    embeddings = embedding_provider.embed_texts(
        [chunk.content for chunk in chunks]
    )
    vector_store.add(chunks, embeddings)

    print("Indexed chunks:", len(chunks))
    print("Stored vectors:", vector_store.index.ntotal)

    # 7. Initialize query use case
    query_use_case = QueryPolicyUseCase(
        embedding_provider=embedding_provider,
        vector_store=vector_store,
        document_repository=document_repository,
        llm_provider=llm_provider,
        similarity_threshold=0.65,
        top_k=5,
    )

    # 8. Test supported question
    question = "How many annual leaves do employees receive?"

    supported_embedding = embedding_provider.embed_text(question)

    supported_matches = vector_store.search(
        query_embedding=supported_embedding,
        top_k=5,
    )

    print("\nSupported question similarity scores:")

    for chunk, score in supported_matches:
        print(
            f"Score: {score:.4f} | "
            f"Page: {chunk.page_number} | "
            f"Content: {chunk.content}"
        )

    result = query_use_case.execute(question)

    print("\nQuestion:", question)
    print("Answer:", result.answer)

    print("\nSources:")
    for source in result.sources:
        print(
            f"File: {source.file_name} | "
            f"Version: {source.document_version} | "
            f"Page: {source.page_number}"
        )

    assert result.sources, "No sources were returned."
    assert any(
        source.page_number == 1 for source in result.sources
    ), "Annual leave source was not retrieved."

    assert "20" in result.answer, (
        "Expected annual leave answer was not found."
    )

    # 9. Test unsupported question
    unsupported_question = (
        "What is the company's maternity leave policy?"
    )

    unsupported_embedding = embedding_provider.embed_text(
        unsupported_question
    )

    unsupported_matches = vector_store.search(
        query_embedding=unsupported_embedding,
        top_k=5,
    )

    print("\nUnsupported question similarity scores:")

    for chunk, score in unsupported_matches:
        print(
            f"Score: {score:.4f} | "
            f"Page: {chunk.page_number} | "
            f"Content: {chunk.content}"
        )

    unsupported_result = query_use_case.execute(
        unsupported_question
    )

    print("\nUnsupported question:", unsupported_question)
    print("Answer:", unsupported_result.answer)
    print("Sources:", len(unsupported_result.sources))

    assert "couldn't find relevant information" in (
        unsupported_result.answer.lower()
    ), "Expected abstention response was not returned."

    print("\nLLM/retrieval abstention response verified.")

    print("\nEnd-to-end RAG + Gemini verification passed.")