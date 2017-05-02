#!/bin/bash
DB=$1
DIR=$2

SQLCMD="SELECT COUNT(*), cert_issuer FROM certificates GROUP BY cert_issuer ORDER BY COUNT(cert_issuer) DESC;"
OUTFILE="$DIR/0_cert_issuer.csv"

CMD="sqlite3 $DB '$SQLCMD' > $OUTFILE"
echo $CMD
eval $CMD
