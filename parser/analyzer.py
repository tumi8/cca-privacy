#!/usr/bin/env python
'''    
Created on Jul 19, 2016

@author: mwachs
'''

import sys, os, logging
from Certificate import Certificate
from Connection import Connection
from NetworkConnection import NetworkConnection
    
try: 
    from sqlitedict import SqliteDict
except ImportError as e:
    print ("SqliteDict module not found: " + str(e))
    sys.exit(1)     
    

loglevel = logging.WARNING

dbFile="connections.db"
 
def printConnections():
    global conDict
    for key, value in conDict.iteritems():
        print("{}:".format(key))
        print("\t {}".format(value))
        
def printCertificates():
    global certDict
    for key, value in certDict.iteritems():
        print("{}:".format(key))
        print("\t {}".format(value))

if __name__ == '__main__':
    global conDict
    global certDict             
    logging.basicConfig(format='%(message)s', level=loglevel)
#     logging.warn ("Scapy imported from "+ __file__)
#     logging.warn ("X.509 cryptography imported from "+ CCX509.__file__)
#     logging.warn ("M2crypto imported from "+ X509.__file__)
    logging.warn ("Current directory: " + os.path.dirname(os.path.realpath(__file__)))

    if (2 == len(sys.argv)):
        dbFile = sys.argv[1];
    
    logging.warn ("Opening database '" + dbFile + "'")
    conDict = SqliteDict(dbFile, tablename="connections", autocommit=True)
    certDict = SqliteDict(dbFile,  tablename="certificates", autocommit=True)
            
    logging.warn ("Connections in database: " + str(len(conDict)))
    logging.warn ("Certificates in database: " + str(len(certDict)))

    printConnections()
    printCertificates()

    conDict.close()
    
    certDict.close()
             
    pass