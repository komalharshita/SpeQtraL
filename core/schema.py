import sqlite3
from pathlib import Path

DB_PATH = Path("database/speqtral.db")

def get_schema_string() -> str:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]

    lines = []
    for table in tables:
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [row[1] for row in cursor.fetchall()]
        lines.append(f"Table: {table}")
        lines.append(f"  Columns: {', '.join(columns)}")

    conn.close()
    return "\n".join(lines)