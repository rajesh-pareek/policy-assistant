
from pathlib import Path
from uuid import uuid4

from policy_assistant.domain.entities.chunk import Chunk
from policy_assistant.infrastructure.vector_store.faiss_vector_store import (
    FAISSVectorStore,
)

store = FAISSVectorStore(dimension=384)

document_a = uuid4()
document_b = uuid4()

vector_a = [1.0] + [0.0] * 383
vector_b = [0.0, 1.0] + [0.0] * 382

chunk_a = Chunk(
    document_id=document_a,
    content="Employees receive 20 annual leaves.",
    page_number=1,
    chunk_index=0,
)

chunk_b = Chunk(
    document_id=document_b,
    content="Employees receive 10 sick leaves.",
    page_number=2,
    chunk_index=0,
)

# 1. Add vectors
store.add(
    chunks=[chunk_a, chunk_b],
    embeddings=[vector_a, vector_b],
)

print("Vectors stored:", store.index.ntotal)
assert store.index.ntotal == 2

# 2. Search
results = store.search(vector_a, top_k=2)

print("Best match:", results[0][0].content)
print("Best similarity:", results[0][1])

assert results[0][0].document_id == document_a
assert results[0][1] > 0.99

# 3. Delete one document
store.delete_by_document_id(document_a)

print("Vectors after deletion:", store.index.ntotal)
assert store.index.ntotal == 1
assert store.chunks[0].document_id == document_b

# 4. Save index and metadata
index_path = "data/indexes/verification.faiss"
store.save(index_path)

assert Path(index_path).exists()
assert Path(index_path).with_suffix(".json").exists()

print("Index and metadata saved successfully.")

# 5. Reload index
loaded_store = FAISSVectorStore.load(index_path)

print("Vectors after reload:", loaded_store.index.ntotal)
assert loaded_store.index.ntotal == 1

loaded_results = loaded_store.search(vector_b, top_k=1)

print("Reloaded content:", loaded_results[0][0].content)
assert loaded_results[0][0].document_id == document_b

print("\nAll FAISS verification checks passed.")
