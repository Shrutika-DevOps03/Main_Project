SET LINESIZE 160
SET PAGESIZE 100
SET TIMING ON
PROMPT ===== Index quality (low clustering factor = good) =====
SELECT index_name, clustering_factor, num_rows FROM user_indexes WHERE index_name = 'IDX_ORDERS_DEMO_DATE';
PROMPT ===== PLAN A: date range, index available =====
EXPLAIN PLAN FOR
SELECT COUNT(*), SUM(total_amount) FROM orders_demo
WHERE order_date >= TIMESTAMP '2025-06-01 00:00:00'
AND order_date < TIMESTAMP '2025-06-02 00:00:00';
SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
PROMPT ===== PLAN B: same query, index hidden =====
ALTER INDEX idx_orders_demo_date INVISIBLE;
EXPLAIN PLAN FOR
SELECT COUNT(*), SUM(total_amount) FROM orders_demo
WHERE order_date >= TIMESTAMP '2025-06-01 00:00:00'
AND order_date < TIMESTAMP '2025-06-02 00:00:00';
SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
ALTER INDEX idx_orders_demo_date VISIBLE;
PROMPT ===== PLAN C: function on the column, index visible =====
EXPLAIN PLAN FOR
SELECT COUNT(*), SUM(total_amount) FROM orders_demo
WHERE TRUNC(order_date) = DATE '2025-06-01';
SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
EXIT;
