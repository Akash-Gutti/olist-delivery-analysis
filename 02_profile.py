import os
import pandas as pd
from sqlalchemy import create_engine, text

PASSWORD = os.environ.get("PG_PASSWORD")
engine = create_engine(f"postgresql+psycopg2://postgres:{PASSWORD}@localhost:5432/olist")

def run(label, sql):
    print(f"\n--- {label} ---")
    print(pd.read_sql(sql, engine).to_string(index=False))

# Order status distribution — how many are actually delivered?
run("ORDER STATUS", """
    SELECT order_status, COUNT(*) AS n
    FROM orders GROUP BY order_status ORDER BY n DESC
""")

# Missing timestamps — the delivery timeline has gaps
run("MISSING TIMESTAMPS", """
    SELECT
        COUNT(*) AS total_orders,
        COUNT(*) FILTER (WHERE order_approved_at IS NULL) AS no_approval,
        COUNT(*) FILTER (WHERE order_delivered_carrier_date IS NULL) AS no_carrier,
        COUNT(*) FILTER (WHERE order_delivered_customer_date IS NULL) AS no_delivery
    FROM orders
""")

# Delivered orders with a complete timeline — our analysable population
run("ANALYSABLE POPULATION", """
    SELECT COUNT(*) AS delivered_with_full_timeline
    FROM orders
    WHERE order_status = 'delivered'
      AND order_purchase_timestamp     IS NOT NULL
      AND order_approved_at            IS NOT NULL
      AND order_delivered_carrier_date IS NOT NULL
      AND order_delivered_customer_date IS NOT NULL
      AND order_estimated_delivery_date IS NOT NULL
""")

# Review coverage and duplicates
run("REVIEWS PER ORDER", """
    SELECT reviews_per_order, COUNT(*) AS n_orders FROM (
        SELECT order_id, COUNT(*) AS reviews_per_order
        FROM order_reviews GROUP BY order_id
    ) t GROUP BY reviews_per_order ORDER BY reviews_per_order
""")

# Review score distribution
run("REVIEW SCORES", """
    SELECT review_score, COUNT(*) AS n
    FROM order_reviews GROUP BY review_score ORDER BY review_score
""")

# Sanity check: any deliveries logged before purchase? (impossible = dirty)
run("IMPOSSIBLE DATES", """
    SELECT COUNT(*) AS delivered_before_purchase
    FROM orders
    WHERE order_delivered_customer_date < order_purchase_timestamp
""")