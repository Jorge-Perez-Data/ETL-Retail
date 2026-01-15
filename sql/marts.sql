CREATE SCHEMA IF NOT EXISTS mart;

-- Dim Date
DROP TABLE IF EXISTS mart.dim_date;
CREATE TABLE mart.dim_date AS
SELECT DISTINCT
  order_date AS date,
  EXTRACT(YEAR FROM order_date)::int AS year,
  EXTRACT(MONTH FROM order_date)::int AS month,
  TO_CHAR(order_date, 'YYYY-MM') AS year_month,
  EXTRACT(DAY FROM order_date)::int AS day,
  EXTRACT(DOW FROM order_date)::int AS day_of_week
FROM stg.sales;

-- Dim Customer
DROP TABLE IF EXISTS mart.dim_customer;
CREATE TABLE mart.dim_customer AS
SELECT * FROM stg.customers;

-- Dim Store
DROP TABLE IF EXISTS mart.dim_store;
CREATE TABLE mart.dim_store AS
SELECT * FROM stg.stores;

-- Dim Product
DROP TABLE IF EXISTS mart.dim_product;
CREATE TABLE mart.dim_product AS
SELECT * FROM stg.products;

-- Fact Sales (línea)
DROP TABLE IF EXISTS mart.fact_sales;
CREATE TABLE mart.fact_sales AS
SELECT
  s.order_id,
  s.line_id,
  s.order_date,
  s.customer_id,
  s.store_id,
  s.product_id,
  s.channel,
  s.quantity,
  s.unit_price,
  s.discount_pct,
  s.net_sales,
  s.payment_method,
  s.shipping_type,
  s.delivery_days,
  s.is_returned,
  s.return_amount,
  (s.net_sales - s.return_amount)::numeric(14,2) AS net_sales_after_returns
FROM stg.sales s;
