import os
import oracledb
from dotenv import load_dotenv
from flask import Flask, jsonify

load_dotenv()
app = Flask(__name__)


def run_query(sql):
    conn = oracledb.connect(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        dsn=os.getenv("DB_DSN"),
    )
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        return cursor.fetchall()
    finally:
        conn.close()


@app.route("/api/health")
def health():
    return jsonify({"status": "healthy"})


@app.route("/api/orders/total")
def total_orders():
    rows = run_query("SELECT COUNT(*) FROM orders")
    return jsonify({"total_orders": rows[0][0]})


@app.route("/api/revenue/daily")
def daily_revenue():
    rows = run_query(
        """SELECT summary_date, total_orders, total_revenue, avg_order_value
           FROM daily_sales_summary
           ORDER BY summary_date DESC"""
    )
    data = [
        {
            "date": r[0].strftime("%Y-%m-%d"),
            "orders": r[1],
            "revenue": float(r[2]),
            "avg_order_value": float(r[3]),
        }
        for r in rows
    ]
    return jsonify(data)


@app.route("/api/products/top")
def top_products():
    rows = run_query(
        """SELECT p.product_name, SUM(o.quantity), SUM(o.total_amount)
           FROM orders o
           JOIN products p ON o.product_id = p.product_id
           GROUP BY p.product_name
           ORDER BY SUM(o.total_amount) DESC
           FETCH FIRST 5 ROWS ONLY"""
    )
    data = [
        {"product": r[0], "units_sold": int(r[1]), "revenue": float(r[2])}
        for r in rows
    ]
    return jsonify(data)


if __name__ == "__main__":
    app.run(port=5000, debug=True)
