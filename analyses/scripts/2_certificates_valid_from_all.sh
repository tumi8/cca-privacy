#!/bin/bash
DB=$1
DIR=$2

IFS='/' read -r -a PARTS <<< "$0"
OUTFILE="$DIR/${PARTS[-1]}.csv"

echo "OUTFILE: $OUTFILE"

    SQLCMD="SELECT cert_notbefore from certificates_apple;"
    echo Running $CMD

    CMD="sqlite3 $DB '$SQLCMD' > $OUTFILE"
    eval $CMD
    #echo "$YEAR|$MONTH|$RESULT" > $OUTFILE
