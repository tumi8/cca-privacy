#!/bin/bash
DB=$1
DIR=$2

IFS='/' read -r -a PARTS <<< "$0"
OUTFILE="$DIR/${PARTS[-1]}.csv"


    SQLCMD="SELECT cert_notbefore from certificates_apple WHERE NOT cert_subject LIKE \"%/C=US/ST=CA/L=Cupertino/O=Apple Inc./OU=iPhone%\";"
    echo Running $CMD

    CMD="sqlite3 $DB '$SQLCMD' > $OUTFILE"
    eval $CMD
