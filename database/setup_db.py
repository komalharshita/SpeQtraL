import sqlite3
import pandas as pd
from pathlib import Path

DB_PATH = Path("database/speqtral.db")
DATA_PATH = Path("data/olist")

# Map: table name → CSV filename
TABLES = {
    "orders": "olist_orders_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "products": "olist_products_dataset.csv",
    "customers": "olist_customers_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "order_reviews": "olist_order_reviews_dataset.csv",
    "order_payments": "olist_order_payments_dataset.csv",
    "geolocation": "olist_geolocation_dataset.csv",
    "category_translation": "product_category_name_translation.csv",
}

def load_all():
    conn = sqlite3.connect(DB_PATH)
    for table_name, filename in TABLES.items():
        path = DATA_PATH / filename
        df = pd.read_csv(path)
        df.to_sql(table_name, conn, if_exists="replace", index=False)
        print(f"Loaded {table_name}: {len(df)} rows")
    conn.close()
    print("Done — speqtral.db created")

if __name__ == "__main__":
    load_all()