import sqlite3
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database" / "speqtral.db"


def run_query(sql: str) -> tuple[pd.DataFrame | None, str | None]:
    """Returns (dataframe, None) on success, (None, error_message) on failure."""
    # Strip markdown code fences the LLM sometimes adds
    sql = sql.strip().removeprefix("```sql").removeprefix("```").removesuffix("```").strip()

    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query(sql, conn)
        conn.close()
        return df, None
    except Exception as e:
        return None, str(e)