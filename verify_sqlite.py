
from policy_assistant.infrastructure.persistence.sqlite_database import (
    SQLiteDatabase,
)

database = SQLiteDatabase()
database.initialize()

with database.connect() as connection:
    tables = connection.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()

    print("Database tables:")
    for table in tables:
        print("-", table["name"])

    table_names = {table["name"] for table in tables}

    assert "documents" in table_names
    assert "chunks" in table_names

print("\nSQLite database verification successful.")
