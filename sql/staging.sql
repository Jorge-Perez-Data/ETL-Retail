CREATE SCHEMA IF NOT EXISTS stg;

-- Customers
DROP TABLE IF EXISTS stg.customers;
CREATE TABLE stg.customers AS
SELECT
  customer_id::int,
  segment::text,
  region::text,
  activity_level::text
FROM raw.customers;

-- Stores
DROP TABLE IF EXISTS stg.stores;
CREATE TABLE stg.stores AS
SELECT
  store_id::int,
  store_region::text,
  store_type::text
FROM raw.stores;

-- Products
DROP TABLE IF EXISTS stg.products;
CREATE TABLE stg.products AS
SELECT
  product_id::int,
  product_name::text,
  category::text,
  sub_category::text,
  brand::text,
  is_top_seller::boolean
FROM raw.products;

-- Sales (dedupe + types + basic rules)
DROP TABLE IF EXISTS stg.sales;
CREATE TABLE stg.sales AS
WITH dedup AS (
  SELECT
    *,
    ROW_NUMBER() OVER (PARTITION BY order_id, line_id ORDER BY order_date) AS rn
  FROM raw.sales
)
SELECT
  order_id::bigint,
  line_id::int,
  order_date::date,
  customer_id::int,
  store_id::int,
  product_id::int,
  channel::text,
  quantity::int,
  unit_price::numeric(12,2),
  discount_pct::numeric(6,3),
  net_sales::numeric(14,2),
  payment_method::text,
  COALESCE(shipping_type, 'Unknown')::text AS shipping_type,
  delivery_days::int,
  is_returned::int,
  return_amount::numeric(14,2)
FROM dedup
WHERE rn = 1
  AND quantity > 0
  AND unit_price >= 0
  AND discount_pct BETWEEN 0 AND 1;
