SET LINESIZE 160
SET PAGESIZE 100
SET TIMING ON
PROMPT ===== Rows in table =====
SELECT COUNT(*) FROM orders;
PROMPT ===== PLAN A: date range, index available =====
EXPLAIN PLAN FOR
SELECT COUNT(*), SUM(total_amount) FROM orders
WHERE order_date >= TIMESTAMP '2025-06-01 00:00:00'
AND order_date < TIMESTAMP '2025-06-02 00:00:00';
SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
SELECT COUNT(*), SUM(total_amount) FROM orders
WHERE order_date >= TIMESTAMP '2025-06-01 00:00:00'
AND order_date < TIMESTAMP '2025-06-02 00:00:00';
PROMPT ===== PLAN B: same query, index hidden =====
ALTER INDEX idx_orders_date INVISIBLE;
EXPLAIN PLAN FOR
SELECT COUNT(*), SUM(total_amount) FROM orders
WHERE order_date >= TIMESTAMP '2025-06-01 00:00:00'
AND order_date < TIMESTAMP '2025-06-02 00:00:00';
SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
SELECT COUNT(*), SUM(total_amount) FROM orders
WHERE order_date >= TIMESTAMP '2025-06-01 00:00:00'
AND order_date < TIMESTAMP '2025-06-02 00:00:00';
ALTER INDEX idx_orders_date VISIBLE;
PROMPT ===== PLAN C: function on the column, index visible =====
EXPLAIN PLAN FOR
SELECT COUNT(*), SUM(total_amount) FROM orders
WHERE TRUNC(order_date) = DATE '2025-06-01';
SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
EXIT;
