import os
import pandas as pd
from sqlalchemy import create_engine, text

PASSWORD = os.environ.get("PG_PASSWORD")
if not PASSWORD:
    raise SystemExit("Set PG_PASSWORD first:  $env:PG_PASSWORD=\"your_password\"")

engine = create_engine(
    f"postgresql+psycopg2://postgres:{PASSWORD}@localhost:5432/olist"
)

# CSV filename -> table name
FILES = {
    "olist_orders_dataset.csv":              "orders",
    "olist_order_items_dataset.csv":         "order_items",
    "olist_order_reviews_dataset.csv":       "order_reviews",
    "olist_order_payments_dataset.csv":      "order_payments",
    "olist_customers_dataset.csv":           "customers",
    "olist_sellers_dataset.csv":             "sellers",
    "olist_products_dataset.csv":            "products",
    "olist_geolocation_dataset.csv":         "geolocation",
    "product_category_name_translation.csv": "category_translation",
}

for filename, table in FILES.items():
    path = f"data/raw/{filename}"
    print(f"Loading {table} from {filename}...")
    df = pd.read_csv(path)
    df.to_sql(table, engine, if_exists="replace", index=False,
              chunksize=10000, method="multi")
    print(f"  {len(df):,} rows")

print("\nAll tables loaded. Verifying counts:")
with engine.connect() as conn:
    for table in FILES.values():
        n = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
        print(f"  {table:22} {n:>10,}")