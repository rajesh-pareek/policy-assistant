
from uuid import UUID

from policy_assistant.domain.entities.chunk import Chunk
from policy_assistant.infrastructure.persistence.sqlite_database import (
    SQLiteDatabase,
)


class SQLiteChunkRepository:
    def __init__(self, database: SQLiteDatabase):
        self.database = database

    def save_many(self, chunks: list[Chunk]) -> None:
        if not chunks:
            return

        with self.database.connect() as connection:
            connection.executemany(
                """
                INSERT OR REPLACE INTO chunks
                (id, document_id, content, page_number, chunk_index)
                VALUES (?, ?, ?, ?, ?)
                """,
                [
                    (
                        str(chunk.id),
                        str(chunk.document_id),
                        chunk.content,
                        chunk.page_number,
                        chunk.chunk_index,
                    )
                    for chunk in chunks
                ],
            )

    def get_by_document_id(self, document_id: UUID) -> list[Chunk]:
        with self.database.connect() as connection:
            rows = connection.execute(
                """
                SELECT * FROM chunks
                WHERE document_id = ?
                ORDER BY chunk_index
                """,
                (str(document_id),),
            ).fetchall()

        return [
            Chunk(
                id=UUID(row["id"]),
                document_id=UUID(row["document_id"]),
                content=row["content"],
                page_number=row["page_number"],
                chunk_index=row["chunk_index"],
            )
            for row in rows
        ]

    def delete_by_document_id(self, document_id: UUID) -> None:
        with self.database.connect() as connection:
            connection.execute(
                "DELETE FROM chunks WHERE document_id = ?",
                (str(document_id),),
            )
