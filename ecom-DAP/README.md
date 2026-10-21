![Tests](https://github.com/Shrutika-DevOps03/Main_Project/ecom-DAP/actions/workflows/tests.yml/badge.svg)
# E-Commerce Data Pipeline

A small end-to-end data engineering project. It cleans messy order
data from a CSV file, loads it into an Oracle database, builds a
daily sales summary, and serves the results through a REST API.

## Status

Working locally. The AWS part runs on LocalStack (a local AWS
simulator). Deployment to real AWS is planned.

## How it works

```
raw/*.csv in S3 -> Lambda (quick cleaning) -> clean/*.csv in S3
                                                   |
                       Python ETL (validate against database, load)
                                                   |
                                             Oracle: orders
                                                   |
                          stored procedure -> daily_sales_summary
                                                   |
                                      Flask REST API (JSON)
```
`scripts/run_etl.sh` runs the ETL and writes a daily log file.
Cron runs it every day at 2 AM.

## What is built
- Oracle XE 21c in Docker, 4 tables with primary keys, foreign keys
  and indexes
- ETL in Python (pandas, oracledb). It removes duplicates, rows with
  missing IDs, invalid quantities and unknown customers, standardizes
  the status text, and calculates totals
- Safe to re-run: orders already in the database are skipped
- PL/SQL stored procedure `refresh_daily_summary`
- Flask API with 4 endpoints
- Shell script and cron job, with one log file per day
- 7 pytest unit tests for the cleaning logic
- S3 bucket and a Python Lambda function on LocalStack: uploading a
  CSV under raw/ triggers the cleaning step automatically
- Deploy script (boto3) for the Lambda and the S3 trigger
- Startup script that restarts the Docker services after a reboot
- 16 pytest unit tests (data cleaning and API), run automatically by
  GitHub Actions on every push
- API returns clean JSON errors: 400 for bad input, 404 for unknown
  URLs, 503 when the database is down
- Docker Compose: Oracle, LocalStack and the API start with one
  command; Dockerfile for the API (gunicorn), custom healthcheck

## Sample run
- S3 bucket and a Python Lambda function on LocalStack: uploading a
  CSV under raw/ triggers the cleaning step automatically
- Deploy script (boto3) for the Lambda and the S3 trigger
- Startup script that restarts the Docker services after a rebootThe sample file has 9 rows. The ETL loads 5 and rejects 4
(1 duplicate, 1 missing order ID, 1 negative quantity,
1 unknown customer).

## Tech stack
Oracle SQL and PL/SQL, Python, pandas, Flask, Docker, Bash, cron,
pytest, Git

## API endpoints

| Endpoint | Returns |
|----------|---------|
| GET /api/health | API status |
| GET /api/orders/total | Number of orders |
| GET /api/revenue/daily | Orders and revenue per day |
| GET /api/products/top | Top 5 products by revenue |
| GET /api/orders?page=1&limit=10 | Orders, paginated (limit up to 100) |

## How to run

```bash
# 1. Start Oracle
docker run -d --name oracle-xe -p 1521:1521 \
| GET /api/orders?page=1&limit=10 | Orders, paginated (limit up to 100) |  -e ORACLE_PASSWORD=<admin-password> gvenzl/oracle-xe:21-slim

# 2. In sqlplus (system/<admin-password>@//localhost:1521/XEPDB1)
CREATE USER ecom IDENTIFIED BY <password>;
GRANT CONNECT, RESOURCE, UNLIMITED TABLESPACE TO ecom;

# 3. Create tables, sample data and the procedure
docker cp sql oracle-xe:/tmp/sql
docker exec -it oracle-xe sqlplus ecom/<password>@//localhost:1521/XEPDB1 @/tmp/sql/schema.sql
docker exec -it oracle-xe sqlplus ecom/<password>@//localhost:1521/XEPDB1 @/tmp/sql/sample_data.sql
docker exec -it oracle-xe sqlplus ecom/<password>@//localhost:1521/XEPDB1 @/tmp/sql/procedures.sql

# 4. Python setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 5. Create a .env file
DB_USER=ecom
DB_PASSWORD=<password>
DB_DSN=localhost:1521/XEPDB1

# 6. Run
python3 etl/etl_pipeline.py
python3 api/app.py
python3 -m pytest -v
```

## Quick start (Docker Compose)
Needs Docker and a free LocalStack auth token.

```bash
cp .env.example .env     # then fill in passwords and your token
docker compose up -d --build
curl http://localhost:5000/api/orders/total
```
This starts Oracle (tables created automatically), LocalStack and the
API (gunicorn). Oracle data lives in a Docker volume;
`docker compose down -v` deletes it.

## Run the AWS part locally (LocalStack)
Needs a free LocalStack auth token saved in ~/.localstack_token
(never commit it). Add these to your .env:
```
AWS_ENDPOINT_URL=http://localhost:4566
AWS_ACCESS_KEY_ID=test
AWS_SECRET_ACCESS_KEY=test
AWS_DEFAULT_REGION=ap-south-1
S3_BUCKET=ecom-raw-data
S3_KEY=clean/raw_orders.csv
```
Then:
```bash
python3 etl/upload_to_s3.py
cd lambda_fn && python3 -m zipfile -c function.zip clean_orders.py && cd ..
python3 scripts/deploy_lambda.py
python3 etl/upload_to_s3.py data/raw_orders_2.csv
python3 etl/show_s3.py
S3_KEY=clean/raw_orders_2.csv python3 etl/etl_pipeline.py
```

## Backup and restore (Oracle Data Pump)
Backed up the ECOM schema with `expdp`, deleted 9 orders on purpose,
restored the ORDERS table with `impdp`, and checked the row counts
(17 -> 8 -> 17).

```bash
docker compose exec oracle bash -c 'expdp ecom/$APP_USER_PASSWORD@//localhost:1521/XEPDB1 schemas=ECOM directory=DATA_PUMP_DIR dumpfile=ecom_backup.dmp logfile=ecom_export.log reuse_dumpfiles=yes'
docker compose exec oracle bash -c 'impdp ecom/$APP_USER_PASSWORD@//localhost:1521/XEPDB1 tables=ORDERS directory=DATA_PUMP_DIR dumpfile=ecom_backup.dmp logfile=ecom_import.log table_exists_action=replace'
```
Dump files are copied out of the container with `docker compose cp`
and are git-ignored.

## Query tuning demo (Oracle)
Built a separate 200,000-row table (`sql/generate_load.sql`) and
compared execution plans for a one-day date-range query
(`sql/tuning_demo.sql`). Dates are loaded in order, like a real orders
table.

| Plan | Operation | Estimated cost |
|------|-----------|----------------|
| Index on order_date available | INDEX RANGE SCAN | 12 |
| Index made invisible | TABLE ACCESS FULL | 319 |
| `TRUNC(order_date) = ...`, index available | TABLE ACCESS FULL | 324 |

Index clustering factor: 1137 for 200,000 rows (good: rows for the
same day are stored together).

What I learned:
- My first test data scattered the dates, and Oracle correctly ignored
  the index (full scan, cost 344). The clustering factor explains why.
- A function around an indexed column (`TRUNC(order_date)`) blocks the
  index, so filter with a date range instead.

Cost is Oracle's own estimate, not measured run time. The data is
synthetic and the tests ran on a laptop, so this shows plan behaviour,
not production performance.

## Project structure
```
api/       Flask REST API
data/      Sample raw CSV
etl/       ETL pipeline
scripts/   Shell script for cron
sql/       Schema, sample data, stored procedure
tests/     pytest unit tests
```

## Limitations
- The AWS parts are tested on LocalStack, not on real AWS
- LocalStack data is lost when its container restarts
- Uses small sample data, not production volumes
- Cron runs only while the machine is on
- Full reload of the summary table (not incremental)

## Roadmap
- [ ] Deploy to real AWS with Terraform
- [ ] Incremental summary refresh
