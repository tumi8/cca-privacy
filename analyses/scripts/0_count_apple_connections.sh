#!/bin/bash
DB=$1
DIR=$2

SQLCMD="SELECT COUNT(*) FROM connections_apple;"
IFS='/' read -r -a PARTS <<< "$0"
OUTFILE="$DIR/${PARTS[-1]}.csv"

CMD="sqlite3 $DB '$SQLCMD' > $OUTFILE"
echo $CMD
eval $CMD
