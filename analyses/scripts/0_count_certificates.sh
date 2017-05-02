#!/bin/bash
DB=$1
DIR=$2

SQLCMD="SELECT DISTINCT COUNT(certKey) from certificates;"
IFS='/' read -r -a PARTS <<< "$0"
OUTFILE="$DIR/${PARTS[-1]}.csv"

CMD="sqlite3 $DB '$SQLCMD' > $OUTFILE"
echo $CMD
eval $CMD
