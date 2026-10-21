INSERT INTO orders (order_id, customer_id, product_id, quantity, unit_price, total_amount, order_date, status)
SELECT 1000000 + LEVEL,
       MOD(LEVEL, 5) + 1,
       MOD(LEVEL, 5) + 1,
       MOD(LEVEL, 4) + 1,
       100,
       (MOD(LEVEL, 4) + 1) * 100,
       TIMESTAMP '2025-01-01 00:00:00' + NUMTODSINTERVAL(MOD(LEVEL, 365), 'DAY'),
       'DELIVERED'
FROM dual
CONNECT BY LEVEL <= 200000;
COMMIT;
EXEC DBMS_STATS.GATHER_TABLE_STATS(USER, 'ORDERS')
EXIT;
