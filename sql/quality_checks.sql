-- Ventas sin match en dimensiones (integridad referencial)
SELECT COUNT(*) AS ventas_sin_producto
FROM mart.fact_sales f
LEFT JOIN mart.dim_product p ON f.product_id = p.product_id
WHERE p.product_id IS NULL;

SELECT COUNT(*) AS ventas_sin_cliente
FROM mart.fact_sales f
LEFT JOIN mart.dim_customer c ON f.customer_id = c.customer_id
WHERE c.customer_id IS NULL;

SELECT COUNT(*) AS ventas_sin_tienda
FROM mart.fact_sales f
LEFT JOIN mart.dim_store s ON f.store_id = s.store_id
WHERE s.store_id IS NULL;

-- Reglas de calidad de campos
SELECT COUNT(*) AS descuento_invalido
FROM mart.fact_sales
WHERE discount_pct < 0 OR discount_pct > 1;

SELECT COUNT(*) AS cantidad_invalida
FROM mart.fact_sales
WHERE quantity <= 0;

SELECT COUNT(*) AS devolucion_invalida
FROM mart.fact_sales
WHERE return_amount > net_sales;

-- (Opcional) ventas negativas
SELECT COUNT(*) AS venta_neta_negativa
FROM mart.fact_sales
WHERE net_sales < 0;
