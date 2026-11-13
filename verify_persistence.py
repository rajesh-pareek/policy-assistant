
import sys
from uuid import UUID

from policy_assistant.domain.entities.chunk import Chunk
from policy_assistant.domain.entities.document import Document
from policy_assistant.infrastructure.persistence.sqlite_database import (
    SQLiteDatabase,
)
from policy_assistant.infrastructure.persistence.sqlite_document_repository import (
    SQLiteDocumentRepository,
)
from policy_assistant.infrastructure.persistence.sqlite_chunk_repository import (
    SQLiteChunkRepository,
)
from policy_assistant.infrastructure.vector_store.faiss_vector_store import (
    FAISSVectorStore,
)


DATABASE_PATH = "data/database/persistence_test.db"
INDEX_PATH = "data/indexes/persistence_test.faiss"

database = SQLiteDatabase(DATABASE_PATH)
database.initialize()

document_repository = SQLiteDocumentRepository(database)
chunk_repository = SQLiteChunkRepository(database)


if len(sys.argv) < 2:
    raise SystemExit("Use: python verify_persistence.py save OR load")


if sys.argv[1] == "save":
    document = Document(file_name="persistence_policy.pdf")

    chunk = Chunk(
        document_id=document.id,
        content="Employees receive 20 annual leaves.",
        page_number=1,
        chunk_index=0,
    )

    document_repository.save(document)
    chunk_repository.save_many([chunk])

    vector_store = FAISSVectorStore()
    vector_store.add(
        chunks=[chunk],
        embeddings=[[1.0] + [0.0] * 383],
    )
    vector_store.save(INDEX_PATH)

    print("Persistence test data saved.")
    print("Document ID:", document.id)


elif sys.argv[1] == "load":
    documents = document_repository.get_all()
    assert len(documents) == 1

    document = documents[0]
    chunks = chunk_repository.get_by_document_id(document.id)

    vector_store = FAISSVectorStore.load(INDEX_PATH)
    results = vector_store.search(
        [1.0] + [0.0] * 383,
        top_k=1,
    )

    assert len(chunks) == 1
    assert len(results) == 1
    assert results[0][0].document_id == document.id

    print("Document restored:", document.file_name)
    print("Chunk restored:", chunks[0].content)
    print("FAISS vectors restored:", vector_store.index.ntotal)
    print("Retrieved content:", results[0][0].content)

    print("\nPersistence across process restarts verified.")

else:
    raise SystemExit("Invalid argument. Use save or load.")
