#!/bin/bash
DB=$1
DIR=$2

#SQLCMD="CREATE TEMP VIEW connections_apple_days AS select *,strftime(\'\%d-\%m-\%Y\',timestamp,\'unixepoch\',\'localtime\') AS day from connections_apple;"
#SQLCMD="SELECT COUNT(DISTINCT(ca.day)), ra.conKey FROM connections_apple_day ca, relations_apple ra WHERE ca.conKey=ra.certKey GROUP BY ra.conKey ORDER BY COUNT(DISTINCT(ca.day)) DESC;"
IFS='/' read -r -a PARTS <<< "$0"
OUTFILE="$DIR/${PARTS[-1]}.csv"

CMD="sqlite3 $DB < scripts/1_connections_per_certificate_per_day.sql > $OUTFILE"
echo $CMD
eval $CMD
