#!/bin/bash
set -e

sudo service docker start
sleep 3

cd "$HOME/Main_Project/ecom-DAP"
docker compose up -d --wait

source venv/bin/activate
python3 etl/upload_to_s3.py
python3 scripts/deploy_lambda.py
python3 etl/upload_to_s3.py
echo "All services are ready."
