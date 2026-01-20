CREATE SCHEMA IF NOT EXISTS mart;

-- =========================
-- DIM DATE (desde stg.sales)
-- =========================
DROP TABLE IF EXISTS mart.dim_date;

CREATE TABLE mart.dim_date AS
WITH bounds AS (
  SELECT MIN(fecha_orden) AS dmin, MAX(fecha_orden) AS dmax
  FROM stg.sales
),
dates AS (
  SELECT generate_series(
    (SELECT dmin FROM bounds),
    (SELECT dmax FROM bounds),
    interval '1 day'
  )::date AS date
)
SELECT
  date,
  EXTRACT(YEAR FROM date)::int AS year,
  EXTRACT(MONTH FROM date)::int AS month,
  TO_CHAR(date, 'YYYY-MM') AS year_month,
  EXTRACT(DAY FROM date)::int AS day,
  TO_CHAR(date, 'Dy') AS day_of_week
FROM dates;

-- =========================
-- DIM CUSTOMER
-- =========================
DROP TABLE IF EXISTS mart.dim_customer;

CREATE TABLE mart.dim_customer AS
SELECT
  id_cliente      AS customer_id,
  segmento        AS segment,
  region          AS region,
  nivel_actividad AS activity_level
FROM stg.customers;

-- =========================
-- DIM STORE
-- =========================
DROP TABLE IF EXISTS mart.dim_store;

CREATE TABLE mart.dim_store AS
SELECT
  id_tienda       AS store_id,
  region_tienda   AS store_region,
  tipo_tienda     AS store_type,
  pais            AS country,
  region_admin    AS state_region,
  ciudad          AS city,
  latitud         AS latitude,
  longitud        AS longitude
FROM stg.stores;

-- =========================
-- DIM PRODUCT
-- =========================
DROP TABLE IF EXISTS mart.dim_product;

CREATE TABLE mart.dim_product AS
SELECT
  id_producto     AS product_id,
  nombre_producto AS product_name,
  categoria       AS category,
  subcategoria    AS sub_category,
  marca           AS brand,
  es_top_ventas   AS is_top_seller
FROM stg.products;

-- =========================
-- FACT SALES
-- =========================
DROP TABLE IF EXISTS mart.fact_sales;

CREATE TABLE mart.fact_sales AS
SELECT
  s.id_orden                                   AS order_id,
  s.id_linea                                   AS line_id,
  s.fecha_orden                                AS order_date,
  s.id_cliente                                 AS customer_id,
  s.id_tienda                                  AS store_id,
  s.id_producto                                AS product_id,
  s.canal                                      AS channel,
  s.cantidad                                   AS quantity,
  s.precio_unitario                            AS unit_price,
  s.descuento_pct                              AS discount_pct,
  s.venta_neta                                 AS net_sales,
  s.metodo_pago                                AS payment_method,
  s.tipo_envio                                 AS shipping_type,
  s.dias_entrega                               AS delivery_days,
  s.es_devuelto                                AS is_returned,
  s.monto_devolucion                           AS return_amount,
  (s.venta_neta - s.monto_devolucion)          AS net_sales_after_returns
FROM stg.sales s;
