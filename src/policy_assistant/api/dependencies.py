
from pathlib import Path

from policy_assistant.infrastructure.chunking.token_chunker import TokenChunker
from policy_assistant.infrastructure.embeddings.sentence_transformer_provider import (
    SentenceTransformerEmbeddingProvider,
)
from policy_assistant.infrastructure.llm.gemini_llm_provider import GeminiLLMProvider
from policy_assistant.infrastructure.pdf.pdf_validator import PDFValidator
from policy_assistant.infrastructure.pdf.pypdf_extractor import PyPDFExtractor
from policy_assistant.infrastructure.persistence.sqlite_database import SQLiteDatabase
from policy_assistant.infrastructure.persistence.sqlite_document_repository import (
    SQLiteDocumentRepository,
)
from policy_assistant.infrastructure.persistence.sqlite_chunk_repository import (
    SQLiteChunkRepository,
)
from policy_assistant.infrastructure.vector_store.faiss_vector_store import (
    FAISSVectorStore,
)

from policy_assistant.application.use_cases.ingest_document import (
    IngestDocumentUseCase,
)
from policy_assistant.application.use_cases.query_policy import QueryPolicyUseCase
from policy_assistant.application.use_cases.delete_document import DeleteDocumentUseCase


def create_dependencies() -> dict:
    # Runtime directories
    upload_dir = Path("data/uploads")
    index_path = Path("data/indexes/policy.index")

    upload_dir.mkdir(parents=True, exist_ok=True)
    index_path.parent.mkdir(parents=True, exist_ok=True)

    # Database
    database = SQLiteDatabase()
    database.initialize()

    # Repositories
    document_repository = SQLiteDocumentRepository(database)
    chunk_repository = SQLiteChunkRepository(database)

    # Vector store: restore existing index if available
    metadata_path = index_path.with_suffix(".json")

    if index_path.exists() and metadata_path.exists():
        vector_store = FAISSVectorStore.load(str(index_path))
    else:
        vector_store = FAISSVectorStore()

    # Infrastructure providers
    pdf_validator = PDFValidator()
    pdf_extractor = PyPDFExtractor()
    chunker = TokenChunker()
    embedding_provider = SentenceTransformerEmbeddingProvider()
    llm_provider = GeminiLLMProvider()

    # Application use cases
    ingest_use_case = IngestDocumentUseCase(
        pdf_validator=pdf_validator,
        pdf_extractor=pdf_extractor,
        chunker=chunker,
        embedding_provider=embedding_provider,
        document_repository=document_repository,
        chunk_repository=chunk_repository,
        vector_store=vector_store,
    )

    query_use_case = QueryPolicyUseCase(
        embedding_provider=embedding_provider,
        vector_store=vector_store,
        document_repository=document_repository,
        llm_provider=llm_provider,
        similarity_threshold=0.65,
        top_k=5,
    )

    delete_use_case = DeleteDocumentUseCase(
        document_repository=document_repository,
        chunk_repository=chunk_repository,
        vector_store=vector_store,
    )

    return {
        "upload_dir": upload_dir,
        "index_path": index_path,
        "database": database,
        "document_repository": document_repository,
        "chunk_repository": chunk_repository,
        "vector_store": vector_store,
        "ingest_use_case": ingest_use_case,
        "query_use_case": query_use_case,
        "delete_use_case": delete_use_case,
    }
