-- One review per order: keep the most recent, break ties by review_id
CREATE OR REPLACE VIEW clean_reviews AS
SELECT DISTINCT ON (order_id)
    order_id,
    review_score,
    review_creation_date
FROM order_reviews
ORDER BY order_id, review_creation_date DESC, review_id;

-- The analysable population, with all delivery gaps pre-computed
CREATE OR REPLACE VIEW delivery_analysis AS
SELECT
    o.order_id,
    o.customer_id,
    o.order_purchase_timestamp::timestamp        AS purchased_at,
    o.order_approved_at::timestamp               AS approved_at,
    o.order_delivered_carrier_date::timestamp    AS carrier_at,
    o.order_delivered_customer_date::timestamp   AS delivered_at,
    o.order_estimated_delivery_date::timestamp   AS estimated_at,

    -- Total delivery time, purchase to customer (days)
    EXTRACT(EPOCH FROM (o.order_delivered_customer_date::timestamp
                      - o.order_purchase_timestamp::timestamp)) / 86400.0 AS total_days,

    -- The four lifecycle gaps (days)
    EXTRACT(EPOCH FROM (o.order_approved_at::timestamp
                      - o.order_purchase_timestamp::timestamp)) / 86400.0 AS approval_days,
    EXTRACT(EPOCH FROM (o.order_delivered_carrier_date::timestamp
                      - o.order_approved_at::timestamp)) / 86400.0 AS handling_days,
    EXTRACT(EPOCH FROM (o.order_delivered_customer_date::timestamp
                      - o.order_delivered_carrier_date::timestamp)) / 86400.0 AS transit_days,

    -- Lateness: actual delivery vs estimate (positive = late)
    EXTRACT(EPOCH FROM (o.order_delivered_customer_date::timestamp
                      - o.order_estimated_delivery_date::timestamp)) / 86400.0 AS delay_days,

    (o.order_delivered_customer_date > o.order_estimated_delivery_date) AS is_late,

    r.review_score
FROM orders o
LEFT JOIN clean_reviews r ON o.order_id = r.order_id
WHERE o.order_status = 'delivered'
  AND o.order_approved_at            IS NOT NULL
  AND o.order_delivered_carrier_date IS NOT NULL
  AND o.order_delivered_customer_date IS NOT NULL
  AND o.order_estimated_delivery_date IS NOT NULL;