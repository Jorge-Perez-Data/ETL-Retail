SELECT COUNT(*) AS orphan_products
FROM mart.fact_sales f
LEFT JOIN mart.dim_product p ON f.product_id = p.product_id
WHERE p.product_id IS NULL;

SELECT COUNT(*) AS orphan_customers
FROM mart.fact_sales f
LEFT JOIN mart.dim_customer c ON f.customer_id = c.customer_id
WHERE c.customer_id IS NULL;

SELECT COUNT(*) AS bad_discount
FROM mart.fact_sales
WHERE discount_pct < 0 OR discount_pct > 1;

SELECT COUNT(*) AS bad_qty
FROM mart.fact_sales
WHERE quantity <= 0;

SELECT COUNT(*) AS bad_returns
FROM mart.fact_sales
WHERE return_amount > net_sales;
