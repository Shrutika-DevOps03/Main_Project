# E-Commerce Data Pipeline

A small end-to-end data engineering project. It cleans messy order
data from a CSV file, loads it into an Oracle database, builds a
daily sales summary, and serves the results through a REST API.

## Status
Working locally. AWS deployment is planned (see Roadmap).

## How it works

```
raw_orders.csv -> Python ETL (clean + validate) -> Oracle: orders
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

## Sample run
The sample file has 9 rows. The ETL loads 5 and rejects 4
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

## How to run

```bash
# 1. Start Oracle
docker run -d --name oracle-xe -p 1521:1521 \
  -e ORACLE_PASSWORD=<admin-password> gvenzl/oracle-xe:21-slim

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
- Uses small sample data, not production volumes
- Cron runs only while the machine is on
- Full reload of the summary table (not incremental)

## Roadmap
- [ ] AWS: S3 for raw files, Lambda triggered on upload
- [ ] Docker Compose for the whole project
- [ ] GitHub Actions to run tests on every push
- [ ] API error handling and pagination
- [ ] Incremental summary refresh
