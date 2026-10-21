#!/bin/bash
set -e

PROJECT_DIR="$HOME/Main_Project/ecom-DAP"
BACKUP_DIR="$PROJECT_DIR/backups"
LOG_DIR="$PROJECT_DIR/logs"
LOG_FILE="$LOG_DIR/backup_$(date +%Y-%m-%d).log"
STAMP=$(date +%Y%m%d_%H%M%S)
DUMP="ecom_$STAMP.dmp"
DPDIR="/opt/oracle/admin/XE/dpdump"
KEEP_DAYS=7

mkdir -p "$BACKUP_DIR" "$LOG_DIR"
cd "$PROJECT_DIR"

trap 'echo "=== Backup FAILED: $(date) ===" >> "$LOG_FILE"' ERR

echo "=== Backup started: $(date) ===" >> "$LOG_FILE"

docker compose exec -T oracle bash -c "expdp ecom/\$APP_USER_PASSWORD@//localhost:1521/XEPDB1 schemas=ECOM directory=DATA_PUMP_DIR dumpfile=$DUMP logfile=ecom_$STAMP.log" >> "$LOG_FILE" 2>&1

FULL_PATH=$(docker compose exec -T oracle bash -c "ls $DPDIR/*/$DUMP")
docker compose cp "oracle:$FULL_PATH" "$BACKUP_DIR/$DUMP" >> "$LOG_FILE" 2>&1
docker compose exec -T oracle bash -c "rm -f $DPDIR/*/$DUMP $DPDIR/*/ecom_$STAMP.log"

if [ ! -s "$BACKUP_DIR/$DUMP" ]; then
    echo "ERROR: backup file is missing or empty" >> "$LOG_FILE"
    exit 1
fi

find "$BACKUP_DIR" -name 'ecom_20*.dmp' -mtime +"$KEEP_DAYS" -delete

echo "=== Backup finished OK: $DUMP ($(du -h "$BACKUP_DIR/$DUMP" | cut -f1)) at $(date) ===" >> "$LOG_FILE"
