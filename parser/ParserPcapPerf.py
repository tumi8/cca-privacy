#!/usr/bin/env python
'''    
Created on Jul 19, 2016

@author: mwachs
'''

import sys, signal, os, logging, traceback, datetime
import sqlite3

import DnsResolver
from parser import DatabaseSqlite
from Certificate import Certificate
from Connection import Connection
from fileinput import filename
from datetime import time

try: 
    from scapy.all import sniff, IP, TCP, SSL, TLSHandshake, TLSCertificateList, TLSCertificate
except ImportError as e:
    print ("Scapy module not found: " + str(e))
    sys.exit(1) 
    
try: 
    from M2Crypto import X509
except ImportError as e:
    print ("M2Crypto module not found: " + str(e))
    sys.exit(1) 


packets_total = 0;
packets_processed = 0;
packets_discarded = 0;
packets_included = 0;
connections_added = 0;
connections_skipped = 0;
certificates_added = 0;
certificates_skipped = 0;
relations_added = 0;
relations_skipped = 0;
ipmappings_added_successful = 0;
ipmappings_added_failed = 0;
ipmappings_skipped = 0;

dns_resolve_names = True

db_check_existing = True
db_commit_after = 500
packet_counter = 0
packet_counter_timestamp = datetime.datetime.now()

include_client_certs = True
include_server_certs = False
loglevel = logging.INFO

inputFile="../../files/capture_iphone_20160706.pcap"
#inputFile="../../files/test2.pcap" 
dbFile="connections.db"

def resultCallback (ip, error, name, alias, addresslist):
    global commit_counter
    global dbcon
    global ipmappings_added_failed
    global ipmappings_added_successful
    if None == error:
        logging.warn ("Resolved new IP address: " +str(ip) + " <-> " + name)
        DatabaseSqlite.insertIpHostnameMapping(dbcon, ip, name, None)
        commit_counter +=1
        ipmappings_added_successful +=1 
    else:
        logging.info ("Failed to resolve new IP address: " +str(ip))
        DatabaseSqlite.insertIpHostnameMapping(dbcon, ip, name, error)
        commit_counter +=1
        ipmappings_added_failed +=1            

            
commit_counter = 0
def process_packet (pkt):
#     try: 
#         global packets_total
#         global packets_processed
#         global packets_discarded
#         global packets_included
#         global verbose
#         global connections
#         global certificates_added
#         global certificates_skipped
#         global connections_added
#         global connections_skipped
#         global relations_added
#         global relations_skipped
#         global dbcon
#         global db_commit_after
#         global commit_counter
#         global ipmappings_added_failed
#         global ipmappings_added_successful
#         global ipmappings_skipped
    global packet_counter
    global packet_counter_timestamp
     
    packet_counter += 1
    if packet_counter >= 1000:
        delta = datetime.datetime.now() - packet_counter_timestamp
        logging.error("\t Duration for 1000 packets " + str (delta))
        packet_counter_timestamp = datetime.datetime.now() 
        packet_counter = 0        
    
    return 
                 
    if pkt is None:
        return        
    packets_total += 1
    if not pkt.haslayer(TCP):
        logging.debug ("Not a TCP packet from client")        
        return
    if not ( (include_client_certs and (443 == pkt[TCP].dport)) or 
             (include_server_certs and (443 == pkt[TCP].sport)) ) :
        logging.debug ("Not a SSL/TLS packet from client")
        return    
#         if not (pkt.haslayer(SSL)):
#             logging.debug ("Not a SSL/TLS packet")
#             return
#         if not (pkt.haslayer(TLSHandshake)):
#             logging.debug ("Not a SSL/TLS handshake packet")
#             return    
    if not (pkt.haslayer(TLSCertificate)):
        logging.debug ("Not a SSL/TLS handshake client hello packet does not contain certificates")
        return   
     
    packets_processed += 1
    direction = "unknown"    
    if (443 == pkt[TCP].dport):
        direction = "client"
    if (443 == pkt[TCP].sport):
        direction = "server"

    srcIp = pkt[IP].src
    srcPort = pkt[TCP].sport
    dstIp = pkt[IP].dst
    dstPort = pkt[TCP].dport

    connection = Connection(pkt.time, direction, srcIp, srcPort, dstIp, pkt[TCP].dport)
    conKey = '{}-{}_{}:{}_{}:{}'.format(pkt.time, direction, srcIp, srcPort, dstIp, dstPort)        
    
    if dns_resolve_names:
        res = DatabaseSqlite.getIpHostnameMapping(dbcon, srcIp)
        if None == res:
            logging.warn ("Resolving new IP address: " +srcIp)
            DnsResolver.reverseNameResolution (srcIp, resultCallback)
        else:
            logging.warn ("Skipping resolution for IP address: " +srcIp)
            ipmappings_skipped +=1 
        res = DatabaseSqlite.getIpHostnameMapping(dbcon, dstIp)                
        if None == res:
            logging.warn ("Resolving new IP address: " +dstIp)
            DnsResolver.reverseNameResolution (dstIp, resultCallback)
        else:
            logging.warn ("Skipping resolution for IP address: " +dstIp)
            ipmappings_skipped += 1
    
    logging.warn ('{} {}: {}:{} -> {}:{} : '.format(pkt.time, direction, srcIp, srcPort, dstIp, dstPort)) 
    
    for certlist in pkt[TLSCertificateList]:
        certificates_processed = 0
        for cert in certlist.certificates:  
            dercert = str(cert.data)
            try:
                # Decode certificate
                parsedCert = Certificate(dercert)                 
            except Exception as ex:
                logging.error ('Error parsing certificate {}: {}:{} -> {}:{} : {}'.format(certificates_processed, srcIp, srcPort, dstIp, dstPort, ex))
                DatabaseSqlite.insertInvalidCertificate(dbcon, conKey, dercert)
                packets_discarded +=1
                continue
            certKey = parsedCert.cert_fingerprint  
            parsedCert.setKey(certKey)                              

            # Add certificate              
            if db_check_existing and None != DatabaseSqlite.getCertificate (dbcon, certKey):
                logging.warn ('Existing certificate ' +certKey)
                certificates_skipped += 1
            else:
                logging.warn ('Adding new certificate ' + certKey)
                DatabaseSqlite.insertCertificate (dbcon, certKey, parsedCert)
                certificates_added += 1
                # Adding extensions
                for e in parsedCert.extensions:
                    if e.name == None:
                        logging.error ("Error: Invalid extension, no name")
                        DatabaseSqlite.insertInvalidCertificate(dbcon, conKey, dercert)
                        commit_counter += 1
                        continue
                    if e.value == None:                            
                        logging.error ("Error: Invalid extension" +e.name+ ", no value")
                        DatabaseSqlite.insertInvalidCertificate(dbcon, conKey, dercert)
                        commit_counter += 1
                        continue
                    if db_check_existing and None != DatabaseSqlite.getExtension(dbcon, certKey, e.name) :
                        logging.warn ('Existing extension: ' + certKey + " - " + e.name)
                    else:
                        logging.warn ('Adding new extension ' + certKey + " - " + e.name)
                        DatabaseSqlite.insertExtension(dbcon, certKey, e)
                        commit_counter += 1
            # Adding relation
            if db_check_existing and None != DatabaseSqlite.getRelation(dbcon, conKey, certKey):
                logging.warn ('Existing relation '  + conKey + " <-> " + certKey)
                relations_skipped += 1     
            else:
                logging.warn ('Adding new relation '  + conKey + " <-> " + certKey)
                DatabaseSqlite.insertRelation(dbcon, conKey, certKey)
                commit_counter += 1
                relations_added += 1                                           
            certificates_processed += 1
              
    logging.warning ('{} {}: {}:{} -> {}:{} : {} certificate(s)'.format(pkt.time, direction, srcIp, srcPort, dstIp, dstPort, certificates_processed))                
    
    if certificates_processed == 0 or db_check_existing and None != getConnection (conKey):
        logging.warn ('Existing connection ' +conKey)
        connections_skipped += 1        
    else:
        logging.warn ('Adding new connection ' +conKey)
        DatabaseSqlite.insertConnection(dbcon, conKey,connection)
        commit_counter += 1
        connections_added += 1

    if (commit_counter >= db_commit_after):
        commit_counter = 0
        logging.info ("Committing database!")
        dbcon.commit()
    packets_included +=1
#     except Exception as e:
#         logging.error ("Error parsing packet!: ")
#         exc_type, exc_value, exc_traceback = sys.exc_info()
#         traceback.print_exception(exc_type, exc_value, exc_traceback,
#                               limit=2, file=sys.stdout)

def parse_file(filename):
    global dbcon
    try:
        sniff (offline=filename, prn=process_packet)
    except IOError:
        print ("File '" +filename+ "' not found")
        return
    dbcon.commit()

def getConnection (key):
    global dbcon
    c = dbcon.cursor()
    args = (key,)
    c.execute('SELECT * FROM connections WHERE key=?', args)
    res = c.fetchone()
    return res

def main():
    global certificates_added
    global certificates_skipped
    global connections_added
    global connections_skipped
    global relations_added
    global relations_skipped
    global inputFile     
    global dbFile
    global dbcon
    
    
    infoLogger = logging.getLogger()
    infoLogger.setLevel(logging.ERROR)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)-7s - %(message)s')
    ch.setFormatter(formatter)
    infoLogger.addHandler(ch)    
 
    
#     logging.warn ("Scapy imported from "+ __file__)
#     logging.warn ("X.509 cryptography imported from "+ CCX509.__file__)
#     logging.warn ("M2crypto imported from "+ X509.__file__)
    infoLogger.info ("Current directory: " + os.path.dirname(os.path.realpath(__file__)))
    logging.info ("Loading client certificates: " + str(include_client_certs))
    logging.info ("Loading server certificates: " + str(include_server_certs))

    if (2 == len(sys.argv)):
        inputFile = sys.argv[1];

    if (3 == len(sys.argv)):
        inputFile = sys.argv[1];
        dbFile = sys.argv[2];
    
    logging.info ("Loading input file '" + inputFile + "'")
    
    logging.info ("Opening database '" + dbFile + "'")
    dbcon = DatabaseSqlite.databaseOpen(dbFile)
    
    logging.info ("Checking for connection table in database '" + dbFile + "'")
    DatabaseSqlite.databaseSetup(dbcon)

    parse_file(inputFile)
     
    logging.info  ("Packets total: " + str(packets_total))
    logging.info ("Packets processed: " + str(packets_processed))
    logging.info ("Packets discarded: " + str(packets_discarded))
    logging.info ("Packets included: " + str(packets_included))

    logging.info ("Connections added: " + str(connections_added))
    logging.info ("Connections skipped: " + str(connections_skipped))

    logging.info ("Certificates added: " + str(certificates_added))
    logging.info ("Certificates skipped: " + str(certificates_skipped))

    logging.info ("Relations added: " + str(relations_added))
    logging.info ("Relations skipped: " + str(relations_skipped))

    logging.info ("IP mappings added successful: " + str(ipmappings_added_successful))
    logging.info ("IP mappings added failing: " + str(ipmappings_added_failed))
    logging.info ("IP mappings skipped: " + str(ipmappings_skipped))

    logging.info ("Closing database '" + dbFile + "'")
    DatabaseSqlite.databaseClose(dbcon)     

if __name__ == '__main__':
    main()
    
    
