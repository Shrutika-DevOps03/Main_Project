import pandas as pd
from etl.etl_pipeline import transform

CUSTOMERS = [1, 2, 3]
PRODUCTS = [1, 2, 3]
COLUMNS = ["order_id", "customer_id", "product_id", "quantity",
           "unit_price", "order_date", "status"]


def make_df(rows):
    return pd.DataFrame(rows, columns=COLUMNS)


def test_valid_row_is_kept():
    df = make_df([[1, 1, 1, 2, 100, "2026-10-01", "shipped"]])
    result = transform(df, CUSTOMERS, PRODUCTS)
    assert len(result) == 1


def test_removes_duplicate_rows():
    row = [1, 1, 1, 2, 100, "2026-10-01", "shipped"]
    df = make_df([row, row])
    result = transform(df, CUSTOMERS, PRODUCTS)
    assert len(result) == 1


def test_removes_missing_order_id():
    df = make_df([[None, 1, 1, 2, 100, "2026-10-01", "shipped"]])
    result = transform(df, CUSTOMERS, PRODUCTS)
    assert len(result) == 0


def test_removes_negative_quantity():
    df = make_df([[1, 1, 1, -3, 100, "2026-10-01", "shipped"]])
    result = transform(df, CUSTOMERS, PRODUCTS)
    assert len(result) == 0


def test_removes_unknown_customer():
    df = make_df([[1, 99, 1, 2, 100, "2026-10-01", "shipped"]])
    result = transform(df, CUSTOMERS, PRODUCTS)
    assert len(result) == 0


def test_status_is_cleaned():
    df = make_df([[1, 1, 1, 2, 100, "2026-10-01", " Delivered "]])
    result = transform(df, CUSTOMERS, PRODUCTS)
    assert result.iloc[0]["status"] == "DELIVERED"


def test_total_amount_is_calculated():
    df = make_df([[1, 1, 1, 3, 50, "2026-10-01", "pending"]])
    result = transform(df, CUSTOMERS, PRODUCTS)
    assert result.iloc[0]["total_amount"] == 150
