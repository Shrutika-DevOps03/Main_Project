import os

import oracledb
from dotenv import load_dotenv
from flask import Flask, jsonify, request

load_dotenv()
app = Flask(__name__)

MAX_LIMIT = 100


class BadRequest(Exception):
    pass


def run_query(sql, params=None):
    conn = oracledb.connect(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        dsn=os.getenv("DB_DSN"),
    )
    try:
        cursor = conn.cursor()
        cursor.execute(sql, params or {})
        return cursor.fetchall()
    finally:
        conn.close()


def get_paging():
    try:
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 10))
    except ValueError:
        raise BadRequest("page and limit must be whole numbers")
    if page < 1:
        raise BadRequest("page must be 1 or more")
    if limit < 1 or limit > MAX_LIMIT:
        raise BadRequest(f"limit must be between 1 and {MAX_LIMIT}")
    return page, limit


@app.errorhandler(BadRequest)
def handle_bad_request(error):
    return jsonify({"error": str(error)}), 400


@app.errorhandler(404)
def handle_not_found(error):
    return jsonify({"error": "not found"}), 404


@app.errorhandler(oracledb.Error)
def handle_database_error(error):
    app.logger.error("Database error: %s", error)
    return jsonify({"error": "database unavailable"}), 503


@app.route("/api/health")
def health():
    return jsonify({"status": "healthy"})


@app.route("/api/orders/total")
def total_orders():
    rows = run_query("SELECT COUNT(*) FROM orders")
    return jsonify({"total_orders": rows[0][0]})


@app.route("/api/orders")
def list_orders():
    page, limit = get_paging()
    offset = (page - 1) * limit
    rows = run_query(
        """SELECT order_id, customer_id, product_id, quantity,
                  total_amount, order_date, status
           FROM orders
           ORDER BY order_id
           OFFSET :offset ROWS FETCH NEXT :limit ROWS ONLY""",
        {"offset": offset, "limit": limit},
    )
    total = run_query("SELECT COUNT(*) FROM orders")[0][0]
    data = [
        {
            "order_id": r[0],
            "customer_id": r[1],
            "product_id": r[2],
            "quantity": r[3],
            "total_amount": float(r[4]),
            "order_date": r[5].strftime("%Y-%m-%d"),
            "status": r[6],
        }
        for r in rows
    ]
    return jsonify({"page": page, "limit": limit, "total": total, "data": data})


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
