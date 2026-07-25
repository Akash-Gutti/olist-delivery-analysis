-- Q1: How late is late? Distribution of on-time vs late, and by how much.
SELECT
    CASE
        WHEN delay_days <= 0                      THEN 'On time or early'
        WHEN delay_days <= 3                      THEN 'Late 1-3 days'
        WHEN delay_days <= 7                      THEN 'Late 4-7 days'
        WHEN delay_days <= 14                     THEN 'Late 8-14 days'
        ELSE 'Late 15+ days'
    END AS delivery_band,
    COUNT(*)                                      AS orders,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct,
    ROUND(AVG(review_score)::numeric, 2)          AS avg_review
FROM delivery_analysis
GROUP BY delivery_band
ORDER BY MIN(delay_days);


-- Q2: Does late delivery cost satisfaction? Review score by on-time vs late.
SELECT
    is_late,
    COUNT(*)                             AS orders,
    ROUND(AVG(review_score)::numeric, 2) AS avg_review,
    ROUND(100.0 * COUNT(*) FILTER (WHERE review_score <= 2) / COUNT(review_score), 1) AS pct_1_2_star,
    ROUND(100.0 * COUNT(*) FILTER (WHERE review_score = 5) / COUNT(review_score), 1)  AS pct_5_star
FROM delivery_analysis
GROUP BY is_late;


-- Q3: For late orders, which stage of the lifecycle ran long?
-- Compare the three gaps for on-time vs late deliveries.
SELECT
    is_late,
    COUNT(*)                                  AS orders,
    ROUND(AVG(approval_days)::numeric, 2)     AS avg_approval_days,
    ROUND(AVG(handling_days)::numeric, 2)     AS avg_handling_days,
    ROUND(AVG(transit_days)::numeric, 2)      AS avg_transit_days,
    ROUND(AVG(total_days)::numeric, 2)        AS avg_total_days
FROM delivery_analysis
GROUP BY is_late;


-- Q4: Which product categories have the worst late-delivery rates?
-- Joins: delivery_analysis -> order_items -> products -> category_translation
SELECT
    COALESCE(t.product_category_name_english, p.product_category_name, 'unknown') AS category,
    COUNT(DISTINCT d.order_id)                                   AS orders,
    ROUND(100.0 * COUNT(DISTINCT d.order_id) FILTER (WHERE d.is_late)
                / COUNT(DISTINCT d.order_id), 1)                 AS late_pct,
    ROUND(AVG(d.review_score)::numeric, 2)                       AS avg_review,
    ROUND(AVG(d.transit_days)::numeric, 1)                       AS avg_transit_days
FROM delivery_analysis d
JOIN order_items oi        ON d.order_id = oi.order_id
JOIN products p            ON oi.product_id = p.product_id
LEFT JOIN category_translation t ON p.product_category_name = t.product_category_name
GROUP BY category
HAVING COUNT(DISTINCT d.order_id) >= 200
ORDER BY late_pct DESC
LIMIT 20;


-- Q5: Does delay track with customer region? (transit = geography test)
SELECT
    c.customer_state,
    COUNT(*)                                    AS orders,
    ROUND(100.0 * COUNT(*) FILTER (WHERE d.is_late) / COUNT(*), 1) AS late_pct,
    ROUND(AVG(d.transit_days)::numeric, 1)      AS avg_transit_days,
    ROUND(AVG(d.review_score)::numeric, 2)      AS avg_review
FROM delivery_analysis d
JOIN customers c ON d.customer_id = c.customer_id
GROUP BY c.customer_state
HAVING COUNT(*) >= 500
ORDER BY late_pct DESC;