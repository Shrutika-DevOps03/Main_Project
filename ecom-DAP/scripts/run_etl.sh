#!/bin/bash
set -e

PROJECT_DIR="$HOME/Main_Project/ecom-DAP"
LOG_DIR="$PROJECT_DIR/logs"
LOG_FILE="$LOG_DIR/etl_$(date +%Y-%m-%d).log"

mkdir -p "$LOG_DIR"
cd "$PROJECT_DIR"
source venv/bin/activate

echo "=== ETL started: $(date) ===" >> "$LOG_FILE"

if [ ! -f data/raw_orders.csv ]; then
    echo "ERROR: data/raw_orders.csv not found" >> "$LOG_FILE"
    exit 1
fi

if python3 etl/etl_pipeline.py >> "$LOG_FILE" 2>&1; then
    echo "=== ETL finished OK: $(date) ===" >> "$LOG_FILE"
else
    echo "=== ETL FAILED: $(date) ===" >> "$LOG_FILE"
    exit 1
fi
