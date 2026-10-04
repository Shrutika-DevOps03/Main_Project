CREATE OR REPLACE PROCEDURE refresh_daily_summary AS
BEGIN
    DELETE FROM daily_sales_summary;

    INSERT INTO daily_sales_summary
        (summary_date, total_orders, total_revenue,
         total_customers, avg_order_value)
    SELECT TRUNC(order_date),
           COUNT(*),
           SUM(total_amount),
           COUNT(DISTINCT customer_id),
           ROUND(AVG(total_amount), 2)
    FROM orders
    GROUP BY TRUNC(order_date);

    COMMIT;
END;
/

SHOW ERRORS
EXIT;
