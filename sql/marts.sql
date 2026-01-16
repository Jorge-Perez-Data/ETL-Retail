CREATE SCHEMA IF NOT EXISTS stg;

DROP TABLE IF EXISTS stg.customers;
CREATE TABLE stg.customers AS
SELECT
  id_cliente::int,
  segmento::text,
  region::text,
  nivel_actividad::text
FROM raw.customers;

DROP TABLE IF EXISTS stg.stores;
CREATE TABLE stg.stores AS
SELECT
  id_tienda::int,
  region_tienda::text,
  tipo_tienda::text
FROM raw.stores;

DROP TABLE IF EXISTS stg.products;
CREATE TABLE stg.products AS
SELECT
  id_producto::int,
  nombre_producto::text,
  categoria::text,
  subcategoria::text,
  marca::text,
  es_top_ventas::boolean
FROM raw.products;

DROP TABLE IF EXISTS stg.sales;
CREATE TABLE stg.sales AS
WITH dedup AS (
  SELECT
    *,
    ROW_NUMBER() OVER (PARTITION BY id_orden, id_linea ORDER BY fecha_orden) AS rn
  FROM raw.sales
)
SELECT
  id_orden::bigint,
  id_linea::int,
  fecha_orden::date,
  id_cliente::int,
  id_tienda::int,
  id_producto::int,
  canal::text,
  cantidad::int,
  precio_unitario::numeric(12,2),
  descuento_pct::numeric(6,3),
  venta_neta::numeric(14,2),
  metodo_pago::text,
  COALESCE(tipo_envio, 'Unknown')::text AS tipo_envio,
  dias_entrega::int,
  es_devuelto::int,
  monto_devolucion::numeric(14,2)
FROM dedup
WHERE rn = 1
  AND cantidad > 0
  AND precio_unitario >= 0
  AND descuento_pct BETWEEN 0 AND 1;
