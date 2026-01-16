# Diccionario de Datos — Retail Synthetic Pipeline (2024–2025)

Este documento describe las tablas y columnas del pipeline de datos, organizado por capas:
- **raw**: carga directa desde CSV (sin transformación)
- **stg**: staging (tipado, dedupe, limpieza)
- **mart**: modelo estrella para BI/Analytics (dimensiones + hechos)

> Base de datos: `retail`  
> Schemas: `raw`, `stg`, `mart`

---

## Convenciones generales

- **ID**: claves numéricas (customer_id, product_id, store_id).
- **order_id + line_id**: identifican de forma única una línea de venta.
- **channel**: canal de venta (p.ej. `Online`, `Store`).
- **net_sales**: venta neta de la línea (ya considerando descuento).
- **return_amount**: monto devuelto (0 si no hubo devolución).
- **net_sales_after_returns**: `net_sales - return_amount`.

---

# 1) RAW (raw.*)

## raw.customers
**Descripción:** clientes sintéticos.

| Columna | Tipo (raw) | Descripción |
|---|---|---|
| customer_id | int/text | Identificador único del cliente. |
| segment | text | Segmento (ej. Consumer/Corporate/Home Office u otro set). |
| region | text | Región/ubicación del cliente. |
| activity_level | text | Nivel de actividad (ej. Low/Medium/High). |

**Notas:**
- Puede contener valores categóricos usados para segmentación.

---

## raw.stores
**Descripción:** tiendas/sucursales sintéticas.

| Columna | Tipo (raw) | Descripción |
|---|---|---|
| store_id | int/text | Identificador único de la tienda. |
| store_region | text | Región de la tienda. |
| store_type | text | Tipo de tienda (ej. Mall, Street, Outlet, etc.). |

---

## raw.products
**Descripción:** catálogo de productos sintéticos.

| Columna | Tipo (raw) | Descripción |
|---|---|---|
| product_id | int/text | Identificador único del producto. |
| product_name | text | Nombre del producto. |
| category | text | Categoría (ej. Apparel, Footwear, Accessories, etc.). |
| sub_category | text | Subcategoría. |
| brand | text | Marca. |
| is_top_seller | bool/int | Flag que indica si es de alta rotación. |

---

## raw.sales
**Descripción:** líneas de venta (tabla más grande), cruda desde CSV.

| Columna | Tipo (raw) | Descripción |
|---|---|---|
| order_id | int/text | ID del pedido/boleta. |
| line_id | int/text | ID de línea dentro de la orden. |
| order_date | text/date | Fecha de la venta (YYYY-MM-DD). |
| customer_id | int/text | FK a customers. |
| store_id | int/text | FK a stores. |
| product_id | int/text | FK a products. |
| channel | text | Canal de venta (`Online` / `Store`). |
| quantity | int/text | Unidades vendidas (esperado > 0). |
| unit_price | numeric/text | Precio unitario. |
| discount_pct | numeric/text | Descuento (0 a 1). |
| net_sales | numeric/text | Venta neta de la línea (post-descuento). |
| payment_method | text | Medio de pago (ej. Credit Card, Debit, Transfer, etc.). |
| shipping_type | text | Tipo de envío (para online). Puede ser NULL. |
| delivery_days | int/text | Días estimados/reales de entrega. |
| is_returned | int/bool | 1 si hubo devolución, 0 si no. |
| return_amount | numeric/text | Monto devuelto (0 si no hubo devolución). |

**Notas:**
- `shipping_type` puede ser nulo en ventas no online.
- Se considera una “línea” por producto por orden.

---

# 2) STAGING (stg.*)

## stg.customers
**Descripción:** customers con tipos normalizados.

| Columna | Tipo (stg) | Descripción |
|---|---|---|
| customer_id | int | ID cliente. |
| segment | text | Segmento. |
| region | text | Región. |
| activity_level | text | Nivel actividad. |

---

## stg.stores
**Descripción:** stores con tipos normalizados.

| Columna | Tipo (stg) | Descripción |
|---|---|---|
| store_id | int | ID tienda. |
| store_region | text | Región tienda. |
| store_type | text | Tipo tienda. |

---

## stg.products
**Descripción:** products con tipos normalizados.

| Columna | Tipo (stg) | Descripción |
|---|---|---|
| product_id | int | ID producto. |
| product_name | text | Nombre. |
| category | text | Categoría. |
| sub_category | text | Subcategoría. |
| brand | text | Marca. |
| is_top_seller | boolean | Indicador de alta rotación. |

---

## stg.sales
**Descripción:** ventas con deduplicación, tipado y reglas de calidad.

**Reglas aplicadas:**
- Deduplicación: se conserva `ROW_NUMBER() = 1` por (`order_id`, `line_id`)
- Filtros:
  - `quantity > 0`
  - `unit_price >= 0`
  - `discount_pct BETWEEN 0 AND 1`
- Nulos:
  - `shipping_type` se reemplaza por `'Unknown'` si viene NULL

| Columna | Tipo (stg) | Descripción |
|---|---|---|
| order_id | bigint | ID orden. |
| line_id | int | ID línea. |
| order_date | date | Fecha. |
| customer_id | int | FK a customers. |
| store_id | int | FK a stores. |
| product_id | int | FK a products. |
| channel | text | Canal. |
| quantity | int | Cantidad. |
| unit_price | numeric(12,2) | Precio unitario. |
| discount_pct | numeric(6,3) | Descuento (0–1). |
| net_sales | numeric(14,2) | Venta neta. |
| payment_method | text | Medio de pago. |
| shipping_type | text | Tipo envío (Unknown si NULL). |
| delivery_days | int | Días de entrega. |
| is_returned | int | 0/1 devolución. |
| return_amount | numeric(14,2) | Monto devuelto. |

---

# 3) MART (mart.*)

## mart.dim_date
**Descripción:** dimensión de fechas derivada desde `stg.sales.order_date`.

| Columna | Tipo | Descripción |
|---|---|---|
| date | date | Fecha. |
| year | int | Año. |
| month | int | Mes (1–12). |
| year_month | text | Formato `YYYY-MM`. |
| day | int | Día del mes. |
| day_of_week | int | Día de semana (0=Domingo, 1=Lunes, ... según PostgreSQL). |

---

## mart.dim_customer
**Descripción:** dimensión de clientes (copia de `stg.customers`).

| Columna | Tipo | Descripción |
|---|---|---|
| customer_id | int | PK cliente. |
| segment | text | Segmento. |
| region | text | Región. |
| activity_level | text | Nivel actividad. |

---

## mart.dim_store
**Descripción:** dimensión de tiendas (copia de `stg.stores`).

| Columna | Tipo | Descripción |
|---|---|---|
| store_id | int | PK tienda. |
| store_region | text | Región tienda. |
| store_type | text | Tipo tienda. |

---

## mart.dim_product
**Descripción:** dimensión de productos (copia de `stg.products`).

| Columna | Tipo | Descripción |
|---|---|---|
| product_id | int | PK producto. |
| product_name | text | Nombre. |
| category | text | Categoría. |
| sub_category | text | Subcategoría. |
| brand | text | Marca. |
| is_top_seller | boolean | Flag alta rotación. |

---

## mart.fact_sales
**Descripción:** tabla de hechos a nivel de línea de venta. Es la tabla principal para BI.

| Columna | Tipo | Descripción |
|---|---|---|
| order_id | bigint | ID orden. |
| line_id | int | ID línea. |
| order_date | date | FK a dim_date(date). |
| customer_id | int | FK a dim_customer. |
| store_id | int | FK a dim_store. |
| product_id | int | FK a dim_product. |
| channel | text | Canal. |
| quantity | int | Cantidad. |
| unit_price | numeric(12,2) | Precio unitario. |
| discount_pct | numeric(6,3) | Descuento (0–1). |
| net_sales | numeric(14,2) | Venta neta. |
| payment_method | text | Medio de pago. |
| shipping_type | text | Tipo envío. |
| delivery_days | int | Días entrega. |
| is_returned | int | 0/1 devolución. |
| return_amount | numeric(14,2) | Monto devuelto. |
| net_sales_after_returns | numeric(14,2) | `net_sales - return_amount`. |

**Métricas típicas:**
- GMV/ventas netas: `SUM(net_sales)`
- Ventas netas post devoluciones: `SUM(net_sales_after_returns)`
- Unidades: `SUM(quantity)`
- Tasa de devoluciones:
  - por órdenes: `AVG(is_returned)`
  - por monto: `SUM(return_amount) / NULLIF(SUM(net_sales),0)`

---

# Relaciones recomendadas para (Power BI)

- `mart.fact_sales[order_date]` → `mart.dim_date[date]`
- `mart.fact_sales[customer_id]` → `mart.dim_customer[customer_id]`
- `mart.fact_sales[product_id]` → `mart.dim_product[product_id]`
- `mart.fact_sales[store_id]` → `mart.dim_store[store_id]`

Cardinalidad esperada: **muchos a uno** desde fact a dims.

---

# Checks de calidad (quality_checks.sql)

- Orphans: fact sin dimensión (product/customer) → esperado **0**
- `discount_pct` fuera de rango → esperado **0**
- `quantity <= 0` → esperado **0**
- `return_amount > net_sales` → esperado **0**

---
