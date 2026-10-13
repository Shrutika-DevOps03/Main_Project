import boto3

ENDPOINT = "http://localhost:4566"
REGION = "ap-south-1"
BUCKET = "ecom-raw-data"
NAME = "clean-orders"
ROLE = "arn:aws:iam::000000000000:role/lambda-role"
ZIP_PATH = "lambda_fn/function.zip"

settings = dict(
    endpoint_url=ENDPOINT,
    aws_access_key_id="test",
    aws_secret_access_key="test",
    region_name=REGION,
)
lam = boto3.client("lambda", **settings)
s3 = boto3.client("s3", **settings)

with open(ZIP_PATH, "rb") as f:
    zip_bytes = f.read()

try:
    lam.create_function(
        FunctionName=NAME,
        Runtime="python3.12",
        Role=ROLE,
        Handler="clean_orders.lambda_handler",
        Code={"ZipFile": zip_bytes},
        Timeout=30,
    )
    print("Created function:", NAME)
except lam.exceptions.ResourceConflictException:
    lam.update_function_code(FunctionName=NAME, ZipFile=zip_bytes)
    print("Updated function:", NAME)

lam.get_waiter("function_active_v2").wait(FunctionName=NAME)
lam.get_waiter("function_updated_v2").wait(FunctionName=NAME)

arn = lam.get_function(FunctionName=NAME)["Configuration"]["FunctionArn"]

try:
    lam.add_permission(
        FunctionName=NAME,
        StatementId="s3-invoke",
        Action="lambda:InvokeFunction",
        Principal="s3.amazonaws.com",
        SourceArn=f"arn:aws:s3:::{BUCKET}",
    )
except lam.exceptions.ResourceConflictException:
    pass

s3.put_bucket_notification_configuration(
    Bucket=BUCKET,
    NotificationConfiguration={
        "LambdaFunctionConfigurations": [
            {
                "LambdaFunctionArn": arn,
                "Events": ["s3:ObjectCreated:*"],
                "Filter": {
                    "Key": {
                        "FilterRules": [
                            {"Name": "prefix", "Value": "raw/"},
                            {"Name": "suffix", "Value": ".csv"},
                        ]
                    }
                },
            }
        ]
    },
)
print("Bucket", BUCKET, "now triggers", NAME, "for raw/*.csv")
