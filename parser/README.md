# PCAP Parser Readme 

To extract connections and certificates, we employ a python-based parser tool based on [scapy](http://www.secdev.org/projects/scapy/) and [scpay_tls](https://github.com/tintinweb/scapy-ssl_tls)

This parser can be found in the [parser](parser) directory. The parser supports 3 parser modules:

* DatabaseCsvWriter: write results as CSV
* DatabaseSQLWriter: write results as SQL statements
* DatabaseSqlite: write results to SQLite database

### Basic Usage:

`./Parser.py <parserModule> <inputfile> <result dir/file> <logdir>`

To parse `result.pcap`, store the results as CSV in `./results` and have logs in  `./logs` use: 

`./Parser.py DatabaseCsvWriter result.pcap ./results ./logs`

### Parallelized Usage:

To process a large number of pcaps in parallel, we provide `parseloop.sh` wrapper  which runs the parser in parallel. The number of parallel instances can be configured in `parseloop.sh` setting `MAX_PAR`:

`./parseloop.sh <parserModule> <data dir> <result dir/file> <logdir>`

To parse all pcaps in `./pcats`, store the results as CSV in `./results` and have logs in  `./logs` use: 

`./parseloop.sh DatabaseCsvWriter ./pcas ./results ./logs`

## Database insertion

The resulting connection information and handshakes can be inserted into an SQLite database for further analysis. To do so, we provide an database import script `sqliteinsertLoop.sh` in the `parser` folder. This script prepares an SQLite database and iterates over all CSV results in a result directory:

`sqliteinsertLoop.sh <db file> <data director> <logfile>`

To insert all files in `./results` into `results.sqlite` use:

`sqliteinsertLoop.sh results.sqlite ./results ./import.log`

## Database queries

* Top Certificate Issuer  
`SELECT COUNT(*), cert_issuer FROM certificates GROUP BY cert_issuer ORDER BY COUNT(cert_issuer) DESC;`

* Occurence APNs desktop certificates  
`SELECT DISTINCT COUNT(cert_subject) FROM certificates_apple WHERE NOT cert_subject LIKE "%/C=US/ST=CA/L=Cupertino/O=Apple Inc./OU=iPhone%";`

* Occurence APNs iOS certificates  
`SELECT DISTINCT COUNT(cert_subject) FROM certificates_apple WHERE cert_subject LIKE "%/C=US/ST=CA/L=Cupertino/O=Apple Inc./OU=iPhone%";`

* iOS APNs Certificates per day  
`CREATE VIEW IF NOT EXISTS connections_apple_days AS select *,strftime('%d-%m-%Y',timestamp,'unixepoch','localtime') AS day from connections_apple;`  
`SELECT COUNT(DISTINCT(ca.day)), ra.conKey FROM connections_apple_days ca, relations_apple ra, certificates_apple cf WHERE ca.conKey=ra.certKey AND ra.conKey=cf.certKey AND cf.cert_subject LIKE "%/C=US/ST=CA/L=Cupertino/O=Apple Inc./OU=iPhone%" GROUP BY ra.conKey ORDER BY COUNT(DISTINCT(ca.day)) DESC;`

* Desktop APNs Certificates per day  
`CREATE VIEW IF NOT EXISTS connections_apple_days AS select *,strftime('%d-%m-%Y',timestamp,'unixepoch','localtime') AS day from connections_apple;`  
`SELECT COUNT(DISTINCT(ca.day)), ra.conKey FROM connections_apple_days ca, relations_apple ra, certificates_apple cf WHERE ca.conKey=ra.certKey AND  ra.conKey=cf.certKey AND NOT cf.cert_subject LIKE "%/C=US/ST=CA/L=Cupertino/O=Apple Inc./OU=iPhone%" GROUP BY ra.conKey ORDER BY COUNT(DISTINCT(ca.day)) DESC;`

