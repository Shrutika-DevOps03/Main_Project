DELETE FROM orders WHERE order_id > 1000000;
COMMIT;
EXEC refresh_daily_summary
SELECT COUNT(*) FROM orders;
EXIT;
