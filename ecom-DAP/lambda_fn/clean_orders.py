import csv
import io
import os

import boto3

FIELDS = ["order_id", "customer_id", "product_id", "quantity",
          "unit_price", "order_date", "status", "total_amount"]


def get_s3():
    endpoint = os.environ.get("AWS_ENDPOINT_URL")
    if not endpoint and os.environ.get("LOCALSTACK_HOSTNAME"):
        host = os.environ["LOCALSTACK_HOSTNAME"]
        port = os.environ.get("EDGE_PORT", "4566")
        endpoint = f"http://{host}:{port}"
    return boto3.client("s3", endpoint_url=endpoint)


def lambda_handler(event, context):
    s3 = get_s3()
    info = event["Records"][0]["s3"]
    bucket = info["bucket"]["name"]
    key = info["object"]["key"]

    body = s3.get_object(Bucket=bucket, Key=key)["Body"].read().decode("utf-8")
    rows = list(csv.DictReader(io.StringIO(body)))

    seen = set()
    cleaned = []
    for row in rows:
        row = {k: (v or "").strip() for k, v in row.items() if k}

        signature = tuple(row.values())
        if signature in seen:
            continue
        seen.add(signature)

        if not row["order_id"] or not row["customer_id"] or not row["product_id"]:
            continue
        try:
            quantity = int(row["quantity"])
            price = float(row["unit_price"])
        except ValueError:
            continue
        if quantity <= 0:
            continue

        row["status"] = row["status"].upper()
        row["total_amount"] = round(quantity * price, 2)
        cleaned.append(row)

    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=FIELDS, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(cleaned)

    out_key = "clean/" + os.path.basename(key)
    s3.put_object(Bucket=bucket, Key=out_key, Body=out.getvalue().encode("utf-8"))

    print(f"Cleaned {len(rows)} rows -> {len(cleaned)} rows, saved {out_key}")
    return {"rows_in": len(rows), "rows_out": len(cleaned), "output": out_key}
