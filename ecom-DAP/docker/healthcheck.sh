#!/bin/bash
echo "select object_name from user_objects where object_name = 'REFRESH_DAILY_SUMMARY';" | sqlplus -s "$APP_USER/$APP_USER_PASSWORD@//localhost:1521/XEPDB1" | grep -q REFRESH_DAILY_SUMMARY
