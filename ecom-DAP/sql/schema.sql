CREATE TABLE customers (
    customer_id   NUMBER PRIMARY KEY,
    customer_name VARCHAR2(100) NOT NULL,
    email         VARCHAR2(100) UNIQUE,
    country       VARCHAR2(50),
    created_date  TIMESTAMP DEFAULT SYSTIMESTAMP
);

CREATE TABLE products (
    product_id     NUMBER PRIMARY KEY,
    product_name   VARCHAR2(150) NOT NULL,
    category       VARCHAR2(50),
    price          NUMBER(10,2),
    stock_quantity NUMBER,
    created_date   TIMESTAMP DEFAULT SYSTIMESTAMP
);

CREATE TABLE orders (
    order_id     NUMBER PRIMARY KEY,
    customer_id  NUMBER NOT NULL,
    product_id   NUMBER NOT NULL,
    quantity     NUMBER NOT NULL,
    unit_price   NUMBER(10,2),
    total_amount NUMBER(12,2),
    order_date   TIMESTAMP DEFAULT SYSTIMESTAMP,
    status       VARCHAR2(20) DEFAULT 'PENDING',
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (product_id)  REFERENCES products(product_id)
);

CREATE INDEX idx_orders_date     ON orders(order_date);
CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_orders_product  ON orders(product_id);

CREATE TABLE daily_sales_summary (
    summary_date    DATE PRIMARY KEY,
    total_orders    NUMBER,
    total_revenue   NUMBER(12,2),
    total_customers NUMBER,
    avg_order_value NUMBER(10,2),
    created_at      TIMESTAMP DEFAULT SYSTIMESTAMP
);

EXIT;
