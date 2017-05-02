#!/bin/bash
DB=$1
DIR=$2

IFS='/' read -r -a PARTS <<< "$0"
OUTFILE="$DIR/${PARTS[-1]}.csv"

YEARS=( 2008 2009 2010 2011 2012 2013 2014 2015 2016 2017 2018 )
MONTHS=( Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec )

rm $OUTFILE

for YEAR in "${YEARS[@]}"
do
  for MONTH in "${MONTHS[@]}"
  do
    SQLCMD="SELECT COUNT(*) FROM certificates_apple WHERE cert_notafter LIKE \"%"$YEAR"%\" AND cert_notafter LIKE \"%"$MONTH"%\" AND cert_subject LIKE \"%/C=US/ST=CA/L=Cupertino/O=Apple Inc./OU=iPhone%\";"
    echo Running $CMD

    CMD="sqlite3 $DB '$SQLCMD'"
    RESULT=$(eval $CMD)
    echo "$YEAR|$MONTH|$RESULT" >> $OUTFILE
  done
done
