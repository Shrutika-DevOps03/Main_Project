BEGIN EXECUTE IMMEDIATE 'DROP TABLE orders_demo PURGE'; EXCEPTION WHEN OTHERS THEN NULL; END;
/
CREATE TABLE orders_demo AS
SELECT 1000000 + LEVEL AS order_id,
       MOD(LEVEL, 5) + 1 AS customer_id,
       MOD(LEVEL, 5) + 1 AS product_id,
       MOD(LEVEL, 4) + 1 AS quantity,
       (MOD(LEVEL, 4) + 1) * 100 AS total_amount,
       TIMESTAMP '2025-01-01 00:00:00' + NUMTODSINTERVAL(FLOOR((LEVEL - 1) / 548), 'DAY') AS order_date,
       'DELIVERED' AS status
FROM dual
CONNECT BY LEVEL <= 200000
ORDER BY LEVEL;
CREATE INDEX idx_orders_demo_date ON orders_demo(order_date);
EXEC DBMS_STATS.GATHER_TABLE_STATS(USER, 'ORDERS_DEMO')
SELECT COUNT(*) FROM orders_demo;
EXIT;
