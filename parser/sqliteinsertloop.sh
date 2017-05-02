#!/bin/bash

DBFILE=${1}
DATADIR=${2}
LOGFILE=${3}

echo "Preparing database ${DBFILE}"

sqlite3 $DBFILE "CREATE TABLE IF NOT EXISTS connections (conKey text NOT NULL UNIQUE PRIMARY KEY, timestamp text, direction text, src_ip text, src_port integer, dst_ip text, dst_port integer);"
sqlite3 $DBFILE "CREATE INDEX IF NOT EXISTS connectionsIndex ON connections (conKey);"

sqlite3 $DBFILE "CREATE TABLE IF NOT EXISTS certificates (certKey text NOT NULL UNIQUE PRIMARY KEY, cert_version text, cert_serialnumber text, cert_subject text, cert_pubkey_modulus text, cert_pubkey_size text, cert_notbefore text, cert_notafter text, cert_issuer text, cert_fingerprint text, cert_extension_count integer);"
sqlite3 $DBFILE "CREATE INDEX IF NOT EXISTS certificatesIndex ON certificates (certKey);"

sqlite3 $DBFILE "CREATE TABLE IF NOT EXISTS extensions (certKey TEXT, ext_name TEXT, ext_value TEXT, FOREIGN KEY(certKey) REFERENCES certificates(certKey));"
sqlite3 $DBFILE "CREATE INDEX IF NOT EXISTS extensionsIndex ON extensions (certKey);"

sqlite3 $DBFILE "CREATE TABLE IF NOT EXISTS relations (conKey TEXT, certKey TEXT, FOREIGN KEY(conKey) REFERENCES connections(conKey), FOREIGN KEY(certKey) REFERENCES certificates(certKey)) ";
sqlite3 $DBFILE "CREATE INDEX IF NOT EXISTS relationsIndex ON relations (certKey, conKey);"

sqlite3 $DBFILE "CREATE TABLE IF NOT EXISTS mappings (ip text NOT NULL, hostname text, error text)"
sqlite3 $DBFILE "CREATE INDEX IF NOT EXISTS mappingsIndex ON mappings (ip);"

sqlite3 $DBFILE "CREATE TABLE IF NOT EXISTS invalid (conKey TEXT, dercert BLOB, FOREIGN KEY(conKey) REFERENCES connections(conKey))";
sqlite3 $DBFILE "CREATE INDEX IF NOT EXISTS invalidIndex ON invalid (conKey);"

sqlite3 $DBFILE "CREATE VIEW IF NOT EXISTS certificates_apple AS SELECT * FROM certificates WHERE cert_issuer LIKE '%/C=US/O=Apple Inc./OU=Apple iPhone/CN=Apple iPhone Device CA%;"

sqlite3 $DBFILE "CREATE VIEW IF NOT EXISTS relations_apple AS SELECT * FROM relations r, certificates_apple ca WHERE r.conKey=ca.certKey;"

sqlite3 $DBFILE "CREATE VIEW IF NOT EXISTS connections_apple AS SELECT * FROM connections c, relations_apple ra WHERE c.conKey=ra.certKey;"


COMPONENTS=(connections certificates extensions relations mappings invalid)

for COMPONENT in "${COMPONENTS[@]}"
do
echo "Processing ${COMPONENT}"
for FILE in ${DATADIR}${COMPONENT}*.csv
do
  echo "Processing $FILE file..."
  SQLCMD="sqlite3 $DBFILE --separator \";\" \".import ${FILE} ${COMPONENT}\""
  echo $SQLCMD
  eval time $SQLCMD >> $LOGFILE 2>&1
done
done
