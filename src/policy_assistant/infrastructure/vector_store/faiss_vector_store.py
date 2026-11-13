
import json
from pathlib import Path
from uuid import UUID

import faiss
import numpy as np

from policy_assistant.domain.entities.chunk import Chunk


class FAISSVectorStore:
    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        self.index = faiss.IndexFlatIP(dimension)
        self.chunks: list[Chunk] = []

    def add(
        self,
        chunks: list[Chunk],
        embeddings: list[list[float]],
    ) -> None:
        if len(chunks) != len(embeddings):
            raise ValueError("Chunks and embeddings must have matching lengths.")

        if not chunks:
            return

        vectors = np.asarray(embeddings, dtype=np.float32)

        if vectors.ndim != 2 or vectors.shape[1] != self.dimension:
            raise ValueError(
                f"Expected embeddings with {self.dimension} dimensions."
            )

        if not np.isfinite(vectors).all():
            raise ValueError("Embeddings must contain finite values.")

        self.index.add(vectors)
        self.chunks.extend(chunks)

    def search(
        self,
        query_embedding: list[float],
        top_k: int,
    ) -> list[tuple[Chunk, float]]:
        if top_k <= 0:
            raise ValueError("top_k must be greater than zero.")

        if self.index.ntotal == 0:
            return []

        query = np.asarray([query_embedding], dtype=np.float32)

        if query.shape[1] != self.dimension:
            raise ValueError(
                f"Expected query embedding with {self.dimension} dimensions."
            )

        if not np.isfinite(query).all():
            raise ValueError("Query embedding must contain finite values.")

        scores, indices = self.index.search(
            query,
            min(top_k, self.index.ntotal),
        )

        results = []

        for score, index in zip(scores[0], indices[0]):
            if index < 0:
                continue

            results.append((self.chunks[index], float(score)))

        return results

    def delete_by_document_id(self, document_id: UUID) -> None:
        remaining = [
            (chunk, vector)
            for chunk, vector in zip(
                self.chunks,
                self.index.reconstruct_n(0, self.index.ntotal)
                if self.index.ntotal else [],
            )
            if chunk.document_id != document_id
        ]

        self.index = faiss.IndexFlatIP(self.dimension)
        self.chunks = []

        if remaining:
            chunks, vectors = zip(*remaining)
            self.add(list(chunks), np.asarray(vectors).tolist())

    def save(self, index_path: str) -> None:
        path = Path(index_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        faiss.write_index(self.index, str(path))

        metadata = [
            {
                "document_id": str(chunk.document_id),
                "content": chunk.content,
                "page_number": chunk.page_number,
                "chunk_index": chunk.chunk_index,
                "id": str(chunk.id),
            }
            for chunk in self.chunks
        ]

        metadata_path = path.with_suffix(".json")
        metadata_path.write_text(
            json.dumps(metadata, indent=2),
            encoding="utf-8",
        )

    @classmethod
    def load(cls, index_path: str) -> "FAISSVectorStore":
        path = Path(index_path)
        metadata_path = path.with_suffix(".json")

        if not path.exists() or not metadata_path.exists():
            raise FileNotFoundError("FAISS index or metadata file not found.")

        store = cls()
        store.index = faiss.read_index(str(path))

        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))

        store.chunks = [
            Chunk(
                document_id=UUID(item["document_id"]),
                content=item["content"],
                page_number=item["page_number"],
                chunk_index=item["chunk_index"],
                id=UUID(item["id"]),
            )
            for item in metadata
        ]

        if store.index.ntotal != len(store.chunks):
            raise ValueError("FAISS index and chunk metadata are inconsistent.")

        return store
