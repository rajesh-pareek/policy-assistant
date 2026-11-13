
from datetime import datetime
from uuid import UUID

from policy_assistant.domain.entities.document import Document
from policy_assistant.infrastructure.persistence.sqlite_database import (
    SQLiteDatabase,
)


class SQLiteDocumentRepository:
    def __init__(self, database: SQLiteDatabase):
        self.database = database

    def save(self, document: Document) -> None:
        with self.database.connect() as connection:
           
            connection.execute(
                """
                INSERT INTO documents
                (id, file_name, version, status, uploaded_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    file_name = excluded.file_name,
                    version = excluded.version,
                    status = excluded.status,
                    uploaded_at = excluded.uploaded_at
                """,
                (
                    str(document.id),
                    document.file_name,
                    document.version,
                    document.status,
                    document.uploaded_at.isoformat(),
                ),
            )

    def get_by_id(self, document_id: UUID) -> Document | None:
        with self.database.connect() as connection:
            row = connection.execute(
                "SELECT * FROM documents WHERE id = ?",
                (str(document_id),),
            ).fetchone()

        if row is None:
            return None

        return Document(
            id=UUID(row["id"]),
            file_name=row["file_name"],
            version=row["version"],
            status=row["status"],
            uploaded_at=datetime.fromisoformat(row["uploaded_at"]),
        )

    def get_all(self) -> list[Document]:
        with self.database.connect() as connection:
            rows = connection.execute(
                "SELECT * FROM documents ORDER BY uploaded_at DESC"
            ).fetchall()

        return [
            Document(
                id=UUID(row["id"]),
                file_name=row["file_name"],
                version=row["version"],
                status=row["status"],
                uploaded_at=datetime.fromisoformat(row["uploaded_at"]),
            )
            for row in rows
        ]

    def delete(self, document_id: UUID) -> None:
        with self.database.connect() as connection:
            connection.execute(
                "DELETE FROM documents WHERE id = ?",
                (str(document_id),),
            )
