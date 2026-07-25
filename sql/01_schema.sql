-- Primary keys
ALTER TABLE orders     ADD PRIMARY KEY (order_id);
ALTER TABLE customers  ADD PRIMARY KEY (customer_id);
ALTER TABLE products   ADD PRIMARY KEY (product_id);
ALTER TABLE sellers    ADD PRIMARY KEY (seller_id);

-- Indexes on foreign-key / join columns
CREATE INDEX idx_orders_customer   ON orders(customer_id);
CREATE INDEX idx_items_order       ON order_items(order_id);
CREATE INDEX idx_items_product     ON order_items(product_id);
CREATE INDEX idx_items_seller      ON order_items(seller_id);
CREATE INDEX idx_reviews_order     ON order_reviews(order_id);
CREATE INDEX idx_payments_order    ON order_payments(order_id);
