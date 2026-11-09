import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database" / "speqtral.db"


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

    lines.extend([
        "",
        "Relationships:",
        "  orders.customer_id -> customers.customer_id",
        "  order_items.order_id -> orders.order_id",
        "  order_items.product_id -> products.product_id",
        "  order_items.seller_id -> sellers.seller_id",
        "  order_reviews.order_id -> orders.order_id",
        "  order_payments.order_id -> orders.order_id",
        "  products.product_category_name -> category_translation.product_category_name",
    ])

    conn.close()
    return "\n".join(lines)