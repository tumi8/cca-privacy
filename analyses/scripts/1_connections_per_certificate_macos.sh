#!/bin/bash
DB=$1
DIR=$2

SQLCMD='SELECT COUNT(*), ra.conKey FROM connections_apple ca, relations_apple ra, certificates_apple cf WHERE ca.conKey=ra.certKey AND ra.conKey=cf.certKey AND NOT cf.cert_subject LIKE "%/C=US/ST=CA/L=Cupertino/O=Apple Inc./OU=iPhone%" GROUP BY ra.conKey ORDER BY COUNT(ra.conKey) DESC;'
IFS='/' read -r -a PARTS <<< "$0"
OUTFILE="$DIR/${PARTS[-1]}.csv"

CMD="sqlite3 $DB '$SQLCMD' > $OUTFILE"
echo $CMD
eval $CMD
