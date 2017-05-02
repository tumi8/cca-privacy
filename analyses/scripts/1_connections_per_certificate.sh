#!/bin/bash
DB=$1
DIR=$2

SQLCMD="SELECT COUNT(*), ra.conKey FROM connections_apple ca, relations_apple ra WHERE ca.conKey=ra.certKey GROUP BY ra.conKey ORDER BY COUNT(ra.conKey) DESC;"
IFS='/' read -r -a PARTS <<< "$0"
OUTFILE="$DIR/${PARTS[-1]}.csv"

CMD="sqlite3 $DB '$SQLCMD' > $OUTFILE"
echo $CMD
eval $CMD
