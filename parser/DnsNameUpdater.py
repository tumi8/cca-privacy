#!/usr/bin/env python
'''    
Created on Jul 19, 2016

@author: mwachs
'''

import logging, sys, sqlite3
import DnsResolver
from parser import DatabaseSqlite

loglevel = logging.INFO
dbFile="connections.db"
dbTable="connections"
dbColumn="src_ip"
dbCon=None

def resultCallback (ip, error, name, alias, addresslist):
    global dbCon
    if None == error:
        logging.info("Resolved " + ip + " ->" + name)
        DatabaseSqlite.insertIpHostnameMapping(dbCon, ip, name, None)
    else:
        logging.info("Failed to resolve "+ ip + " : " + error)
        DatabaseSqlite.insertIpHostnameMapping(dbCon, ip, None, error)

def getIPs (table, column):
    ips = []
    global dbCon
    c = dbCon.cursor()
    c.execute('SELECT DISTINCT ' + column + ' FROM ' + table )
    for r in c:
        ip = str(r[0])
        ips.append(ip)
    return ips

def main ():
    global dbFile
    global dbCon
    logging.basicConfig(format='%(message)s', level=loglevel)
    
    if (3 == len(sys.argv)):
        dbFile = sys.argv[1];
        dbTable = sys.argv[2];
        dbColumn = sys.argv[3];

    logging.warn ("Opening database '" + dbFile + "'")
    dbCon = DatabaseSqlite.databaseOpen(dbFile)
    DatabaseSqlite.databaseSetup(dbCon)
    
    logging.info("Starting DNS reverse resolution")

    ips = getIPs("connections", "src_ip")
    logging.info("Found " +str(len(ips))+" IPs ")

    for ip in ips:
        if None == DatabaseSqlite.getIpHostnameMapping (dbCon, ip):
            logging.info("Resolving " + ip)
            DnsResolver.reverseNameResolution(ip, resultCallback)
            DatabaseSqlite.databaseCommit(dbCon)
        else:
            logging.info("Existing IP mapping for " + ip)
        
    logging.info("Done DNS reverse resolution")
    DatabaseSqlite.databaseClose(dbCon)
    
    return

if __name__ == '__main__':
    main()
    