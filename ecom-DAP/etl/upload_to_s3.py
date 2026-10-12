import boto3

s3 = boto3.client(
    "s3",
    endpoint_url="http://localhost:4566",
    aws_access_key_id="test",
    aws_secret_access_key="test",
    region_name="ap-south-1",
)

BUCKET = "ecom-raw-data"

try:
    s3.create_bucket(
        Bucket=BUCKET,
        CreateBucketConfiguration={"LocationConstraint": "ap-south-1"},
    )
    print("Created bucket:", BUCKET)
except s3.exceptions.BucketAlreadyOwnedByYou:
    print("Bucket already exists:", BUCKET)

s3.upload_file("data/raw_orders.csv", BUCKET, "raw/raw_orders.csv")

response = s3.list_objects_v2(Bucket=BUCKET)
for obj in response.get("Contents", []):
    print(obj["Key"], obj["Size"], "bytes")
