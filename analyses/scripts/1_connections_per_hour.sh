#!/bin/bash
DB=$1
DIR=$2

IFS='/' read -r -a PARTS <<< "$0"
OUTFILE="$DIR/${PARTS[-1]}.csv"

YEARS=( 2016 )
MONTHS=( 9 10 )


rm $OUTFILE

for YEAR in "${YEARS[@]}"
do
  for MONTH in "${MONTHS[@]}"
  do

    DAYCOUNTER=1
    while [  $DAYCOUNTER -lt 31 ]; do

        HOURCOUNTER=0
        while [  $HOURCOUNTER -lt 24 ]; do
            echo "Running $YEAR $MONTH $DAYCOUNTER - $HOURCOUNTER"
            BEGIN=$(date -d"$YEAR-$MONTH-${DAYCOUNTER}T${HOURCOUNTER}:00" +%s)
            let END=BEGIN+3600

            SQLCMD="SELECT COUNT(*) FROM connections_apple WHERE timestamp >= $BEGIN AND timestamp <= $END"
            CMD="sqlite3 $DB '$SQLCMD'"
            echo $CMD
            RESULT=$(eval $CMD)
            echo $RESULT
            echo "$YEAR|$MONTH|$DAYCOUNTER|$HOURCOUNTER|$RESULT" >> $OUTFILE

            let HOURCOUNTER=HOURCOUNTER+1
        done
        let DAYCOUNTER=DAYCOUNTER+1
    done
  done
done
