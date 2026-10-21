#!/bin/bash
set -e

for file in schema.sql sample_data.sql procedures.sql; do
    echo "Running $file"
    sqlplus -s "$APP_USER/$APP_USER_PASSWORD@//localhost:1521/XEPDB1" @/sql/$file
done
echo "Database initialised"
