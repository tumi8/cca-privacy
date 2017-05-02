#!/bin/bash
DB=$1
DIR=$2

SQLCMD='SELECT DISTINCT COUNT(cert_subject) FROM certificates_apple WHERE NOT cert_subject LIKE "%/C=US/ST=CA/L=Cupertino/O=Apple Inc./OU=iPhone%";'
IFS='/' read -r -a PARTS <<< "$0"
OUTFILE="$DIR/${PARTS[-1]}.csv"

CMD="sqlite3 $DB '$SQLCMD' > $OUTFILE"
echo $CMD
eval $CMD
