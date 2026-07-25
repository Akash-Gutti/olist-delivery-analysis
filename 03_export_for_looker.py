import os
import pandas as pd
from sqlalchemy import create_engine

PASSWORD = os.environ.get("PG_PASSWORD")
if not PASSWORD:
    raise SystemExit("Set PG_PASSWORD first:  $env:PG_PASSWORD=\"your_password\"")

engine = create_engine(f"postgresql+psycopg2://postgres:{PASSWORD}@localhost:5432/olist")
os.makedirs("data/looker", exist_ok=True)

queries = {}

queries['delivery_bands'] = """
SELECT
    CASE
        WHEN delay_days <= 0  THEN '1. On time or early'
        WHEN delay_days <= 3  THEN '2. Late 1-3 days'
        WHEN delay_days <= 7  THEN '3. Late 4-7 days'
        WHEN delay_days <= 14 THEN '4. Late 8-14 days'
        ELSE '5. Late 15+ days'
    END AS delivery_band,
    COUNT(*) AS orders,
    ROUND(AVG(review_score)::numeric, 2) AS avg_review
FROM delivery_analysis
GROUP BY delivery_band
ORDER BY delivery_band
"""

queries['late_vs_satisfaction'] = """
SELECT
    CASE WHEN is_late THEN 'Late' ELSE 'On time' END AS delivery_status,
    COUNT(*) AS orders,
    ROUND(AVG(review_score)::numeric, 2) AS avg_review,
    ROUND(100.0 * COUNT(*) FILTER (WHERE review_score <= 2) / COUNT(review_score), 1) AS pct_negative,
    ROUND(100.0 * COUNT(*) FILTER (WHERE review_score = 5) / COUNT(review_score), 1)  AS pct_5_star
FROM delivery_analysis
GROUP BY is_late
"""

queries['lifecycle_gaps'] = """
SELECT
    CASE WHEN is_late THEN 'Late' ELSE 'On time' END AS delivery_status,
    ROUND(AVG(approval_days)::numeric, 2) AS approval_days,
    ROUND(AVG(handling_days)::numeric, 2) AS handling_days,
    ROUND(AVG(transit_days)::numeric, 2)  AS transit_days
FROM delivery_analysis
GROUP BY is_late
"""

queries['by_state'] = """
SELECT
    c.customer_state,
    COUNT(*) AS orders,
    ROUND(100.0 * COUNT(*) FILTER (WHERE d.is_late) / COUNT(*), 1) AS late_pct,
    ROUND(AVG(d.transit_days)::numeric, 1) AS avg_transit_days,
    ROUND(AVG(d.review_score)::numeric, 2) AS avg_review
FROM delivery_analysis d
JOIN customers c ON d.customer_id = c.customer_id
GROUP BY c.customer_state
HAVING COUNT(*) >= 500
ORDER BY late_pct DESC
"""

queries['by_category'] = """
SELECT
    COALESCE(t.product_category_name_english, p.product_category_name, 'unknown') AS category,
    COUNT(DISTINCT d.order_id) AS orders,
    ROUND(100.0 * COUNT(DISTINCT d.order_id) FILTER (WHERE d.is_late)
                / COUNT(DISTINCT d.order_id), 1) AS late_pct,
    ROUND(AVG(d.review_score)::numeric, 2) AS avg_review
FROM delivery_analysis d
JOIN order_items oi ON d.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id
LEFT JOIN category_translation t ON p.product_category_name = t.product_category_name
GROUP BY category
HAVING COUNT(DISTINCT d.order_id) >= 200
ORDER BY late_pct DESC
LIMIT 20
"""

for name, sql in queries.items():
    df = pd.read_sql(sql, engine)
    df.to_csv(f"data/looker/{name}.csv", index=False)
    print(f"{name:22} {len(df):>4} rows  ->  data/looker/{name}.csv")