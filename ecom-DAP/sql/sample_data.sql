INSERT INTO customers (customer_id, customer_name, email, country) VALUES (1, 'Amit Sharma', 'amit@example.com', 'India');
INSERT INTO customers (customer_id, customer_name, email, country) VALUES (2, 'Priya Patel', 'priya@example.com', 'India');
INSERT INTO customers (customer_id, customer_name, email, country) VALUES (3, 'John Smith', 'john@example.com', 'USA');
INSERT INTO customers (customer_id, customer_name, email, country) VALUES (4, 'Emma Brown', 'emma@example.com', 'UK');
INSERT INTO customers (customer_id, customer_name, email, country) VALUES (5, 'Li Wei', 'li@example.com', 'China');

INSERT INTO products (product_id, product_name, category, price, stock_quantity) VALUES (1, 'Laptop', 'Electronics', 55000, 20);
INSERT INTO products (product_id, product_name, category, price, stock_quantity) VALUES (2, 'Mouse', 'Electronics', 500, 200);
INSERT INTO products (product_id, product_name, category, price, stock_quantity) VALUES (3, 'Notebook', 'Stationery', 60, 500);
INSERT INTO products (product_id, product_name, category, price, stock_quantity) VALUES (4, 'Headphones', 'Electronics', 2500, 80);
INSERT INTO products (product_id, product_name, category, price, stock_quantity) VALUES (5, 'Water Bottle', 'Home', 350, 150);

INSERT INTO orders (order_id, customer_id, product_id, quantity, unit_price, total_amount, order_date, status) VALUES (1, 1, 1, 1, 55000, 55000, TO_DATE('2026-09-28','YYYY-MM-DD'), 'DELIVERED');
INSERT INTO orders (order_id, customer_id, product_id, quantity, unit_price, total_amount, order_date, status) VALUES (2, 2, 2, 2, 500, 1000, TO_DATE('2026-09-28','YYYY-MM-DD'), 'DELIVERED');
INSERT INTO orders (order_id, customer_id, product_id, quantity, unit_price, total_amount, order_date, status) VALUES (3, 3, 4, 1, 2500, 2500, TO_DATE('2026-09-29','YYYY-MM-DD'), 'SHIPPED');
INSERT INTO orders (order_id, customer_id, product_id, quantity, unit_price, total_amount, order_date, status) VALUES (4, 4, 3, 10, 60, 600, TO_DATE('2026-09-29','YYYY-MM-DD'), 'DELIVERED');
INSERT INTO orders (order_id, customer_id, product_id, quantity, unit_price, total_amount, order_date, status) VALUES (5, 5, 5, 3, 350, 1050, TO_DATE('2026-09-30','YYYY-MM-DD'), 'PENDING');
INSERT INTO orders (order_id, customer_id, product_id, quantity, unit_price, total_amount, order_date, status) VALUES (6, 1, 2, 1, 500, 500, TO_DATE('2026-09-30','YYYY-MM-DD'), 'SHIPPED');
INSERT INTO orders (order_id, customer_id, product_id, quantity, unit_price, total_amount, order_date, status) VALUES (7, 2, 4, 2, 2500, 5000, TO_DATE('2026-10-01','YYYY-MM-DD'), 'DELIVERED');
INSERT INTO orders (order_id, customer_id, product_id, quantity, unit_price, total_amount, order_date, status) VALUES (8, 3, 1, 1, 55000, 55000, TO_DATE('2026-10-02','YYYY-MM-DD'), 'PENDING');

COMMIT;
EXIT;
