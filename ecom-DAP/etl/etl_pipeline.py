import os
import oracledb
import pandas as pd
from dotenv import load_dotenv

load_dotenv()


def extract(path):
    df = pd.read_csv(path)
    print(f"Extract: read {len(df)} rows")
    return df


def transform(df, valid_customers, valid_products):
    start = len(df)
    df = df.drop_duplicates()
    df = df.dropna(subset=["order_id", "customer_id", "product_id"]).copy()
    df = df.astype({"order_id": int, "customer_id": int,
                    "product_id": int, "quantity": int})
    df["status"] = df["status"].str.strip().str.upper()
    df["order_date"] = pd.to_datetime(df["order_date"])
    df = df[df["quantity"] > 0]
    df = df[df["customer_id"].isin(valid_customers)]
    df = df[df["product_id"].isin(valid_products)]
    df["total_amount"] = df["quantity"] * df["unit_price"]
    print(f"Transform: kept {len(df)} of {start} rows")
    return df


def load(conn, df):
    cursor = conn.cursor()
    cursor.execute("SELECT order_id FROM orders")
    existing = {row[0] for row in cursor.fetchall()}
    df = df[~df["order_id"].isin(existing)]

    rows = [
        (r.order_id, r.customer_id, r.product_id, r.quantity,
         float(r.unit_price), float(r.total_amount),
         r.order_date.to_pydatetime(), r.status)
        for r in df.itertuples()
    ]
    if rows:
        cursor.executemany(
            """INSERT INTO orders
               (order_id, customer_id, product_id, quantity,
                unit_price, total_amount, order_date, status)
               VALUES (:1, :2, :3, :4, :5, :6, :7, :8)""",
            rows,
        )
    conn.commit()
    print(f"Load: inserted {len(rows)} new rows")


def main():
    conn = oracledb.connect(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        dsn=os.getenv("DB_DSN"),
    )
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT customer_id FROM customers")
        valid_customers = [r[0] for r in cursor.fetchall()]
        cursor.execute("SELECT product_id FROM products")
        valid_products = [r[0] for r in cursor.fetchall()]

        df = extract("data/raw_orders.csv")
        df = transform(df, valid_customers, valid_products)
        load(conn, df)
    except Exception as e:
        conn.rollback()
        print("ETL failed:", e)
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
