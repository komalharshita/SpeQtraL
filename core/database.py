import gzip
import os
import shutil
import sqlite3
import tempfile
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database" / "speqtral.db"
COMPRESSED_DB_PATH = DB_PATH.with_suffix(f"{DB_PATH.suffix}.gz")


def ensure_database() -> None:
    if DB_PATH.is_file() and _has_tables():
        return

    if not COMPRESSED_DB_PATH.is_file():
        raise FileNotFoundError(
            f"Database not found at {DB_PATH} and compressed database not found "
            f"at {COMPRESSED_DB_PATH}."
        )

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=DB_PATH.parent, delete=False) as temporary_file:
        temporary_path = Path(temporary_file.name)

    try:
        with gzip.open(COMPRESSED_DB_PATH, "rb") as source, temporary_path.open("wb") as target:
            shutil.copyfileobj(source, target)
        os.replace(temporary_path, DB_PATH)
    finally:
        temporary_path.unlink(missing_ok=True)


def _has_tables() -> bool:
    try:
        connection = sqlite3.connect(f"{DB_PATH.resolve().as_uri()}?mode=ro", uri=True)
        try:
            row = connection.execute(
                "SELECT 1 FROM sqlite_master WHERE type = 'table' LIMIT 1"
            ).fetchone()
            return row is not None
        finally:
            connection.close()
    except sqlite3.DatabaseError:
        return False
