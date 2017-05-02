#!/usr/bin/env python
'''    
Created on Jul 19, 2016

@author: mwachs
'''

import sys, signal, os, logging, traceback, datetime
import sqlite3

import DnsResolver
from Certificate import Certificate
from Connection import Connection
from fileinput import filename
from datetime import time
import DatabaseSqlite
import DatabaseSQLWriter
import DatabaseCsvWriter

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
certificates_corrupt = 0;
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

include_include_ports = [443, 5223, 2195, 2196]
include_client_certs = True
include_server_certs = False
loglevel = logging.WARNING

inputFile="../../files/capture_iphone_20160706.pcap"
#inputFile="../../files/test2.pcap" 
dbFile="results.sql"
Database=None

def resultCallback (ip, error, name, alias, addresslist):
    global commit_counter
    global dbcon
    global ipmappings_added_failed
    global ipmappings_added_successful
    if None == error:
        logging.info ("Resolved new IP address: " +str(ip) + " <-> " + name)
        Database.insertIpHostnameMapping(dbcon, ip, name, None)
        commit_counter +=1
        ipmappings_added_successful +=1 
    else:
        logging.info ("Failed to resolve new IP address: " +str(ip))
        Database.insertIpHostnameMapping(dbcon, ip, name, error)
        commit_counter +=1
        ipmappings_added_failed +=1            

            
commit_counter = 0
def process_packet (pkt):
    try: 
        global packets_total
        global packets_processed
        global packets_discarded
        global packets_included
        global verbose
        global connections
        global certificates_added
        global certificates_skipped
        global certificates_corrupt
        global connections_added
        global connections_skipped
        global relations_added
        global relations_skipped
        global dbcon
        global db_commit_after
        global commit_counter
        global ipmappings_added_failed
        global ipmappings_added_successful
        global ipmappings_skipped
        global packet_counter
        global packet_counter_timestamp
             
        if pkt is None:
            return        
        packets_total += 1
        packet_counter += 1
        if packet_counter == 1000:
            delta = datetime.datetime.now() - packet_counter_timestamp
            logging.error("{} packets processed, duration for 1000 packets: {}".format(packets_total, delta))
            packet_counter_timestamp = datetime.datetime.now() 
            packet_counter = 0        
                    
        if not pkt.haslayer(TCP):
            logging.info ("Not a TCP packet from client")
            packets_discarded +=1        
            return
        if not ( (include_client_certs and (pkt[TCP].dport in include_include_ports)) or 
                 (include_server_certs and (pkt[TCP].sport in include_include_ports)) ) :
            logging.debug ("Source or destinaton port not matched")
            packets_discarded +=1
            return         
        
        if not (pkt.haslayer(SSL)):
            if (pkt[TCP].dport == 5223):
                logging.error ("Not a SSL/TLS packet")
            logging.debug ("Not a SSL/TLS packet")
            packets_discarded +=1
            return
        if not (pkt.haslayer(TLSHandshake)):
            if (pkt[TCP].dport == 5223):
                logging.error ("Not a SSL/TLS handshake packet")
            logging.debug ("Not a SSL/TLS handshake packet")
            packets_discarded +=1
            return    
        if not (pkt.haslayer(TLSCertificate)):
            if (pkt[TCP].dport == 5223):
                logging.error ("SSL/TLS handshake client hello packet does not contain certificates")
            logging.debug ("SSL/TLS handshake client hello packet does not contain certificates")
            packets_discarded +=1
            return   
         
        packets_processed += 1
        direction = "unknown"    
        if (pkt[TCP].dport in include_include_ports):
            direction = "client"
        if (pkt[TCP].sport in include_include_ports):
            direction = "server"
    
        srcIp = pkt[IP].src
        srcPort = pkt[TCP].sport
        dstIp = pkt[IP].dst
        dstPort = pkt[TCP].dport
    
        connection = Connection(pkt.time, direction, srcIp, srcPort, dstIp, pkt[TCP].dport)
        conKey = '{}-{}_{}:{}_{}:{}'.format(pkt.time, direction, srcIp, srcPort, dstIp, dstPort)        
        logging.info ('{} {}: {}:{} -> {}:{}'.format(pkt.time, direction, srcIp, srcPort, dstIp, dstPort))         
        
        if dns_resolve_names:
            res = Database.getIpHostnameMapping(dbcon, srcIp)
            if None == res:
                logging.info ("Resolving new IP address: " +srcIp)
                DnsResolver.reverseNameResolution (srcIp, resultCallback)
            else:
                logging.info ("Skipping resolution for IP address: " +srcIp)
                ipmappings_skipped +=1 
            res = Database.getIpHostnameMapping(dbcon, dstIp)                
            if None == res:
                logging.info ("Resolving new IP address: " +dstIp)
                DnsResolver.reverseNameResolution (dstIp, resultCallback)
            else:
                logging.info ("Skipping resolution for IP address: " +dstIp)
                ipmappings_skipped += 1
        
        for certlist in pkt[TLSCertificateList]:
            certificates_processed = 0
            for cert in certlist.certificates:  
                dercert = str(cert.data)
                try:
                    # Decode certificate
                    parsedCert = Certificate(dercert)                 
                except Exception as ex:
                    logging.info ('Error parsing certificate {}: {}:{} -> {}:{} : {}'.format(certificates_processed, srcIp, srcPort, dstIp, dstPort, ex))
                    certificates_corrupt +=1 
#                     Database.insertInvalidCertificate(dbcon, conKey, parsedCert.getPemCertificate())                    
                    continue
                certKey = parsedCert.cert_fingerprint  
                parsedCert.setKey(certKey)                              

                # Add certificate              
                if db_check_existing and None != Database.getCertificate (dbcon, certKey):
                    logging.info ('Existing certificate ' +certKey)
                    certificates_skipped += 1
                else:
                    logging.info ('Adding new certificate ' + certKey)
                    Database.insertCertificate (dbcon, certKey, parsedCert)
                    certificates_added += 1
                    # Adding extensions
                    for e in parsedCert.extensions:
                        if e.name == None:
                            logging.error ("Error: Invalid extension, no name")
                            Database.insertInvalidCertificate(dbcon, conKey, dercert)
                            commit_counter += 1
                            continue
                        if e.value == None:                            
                            logging.error ("Error: Invalid extension" +e.name+ ", no value")
                            Database.insertInvalidCertificate(dbcon, conKey, dercert)
                            commit_counter += 1
                            continue
                        if db_check_existing and None != Database.getExtension(dbcon, certKey, e.name) :
                            logging.info ('Existing extension: ' + certKey + " - " + e.name)
                        else:
                            logging.info ('Adding new extension ' + certKey + " - " + e.name)
                            Database.insertExtension(dbcon, certKey, e)
                            commit_counter += 1
                # Adding relation
                if db_check_existing and None != Database.getRelation(dbcon, conKey, certKey):
                    logging.info ('Existing relation '  + conKey + " <-> " + certKey)
                    relations_skipped += 1     
                else:
                    logging.info ('Adding new relation '  + conKey + " <-> " + certKey)
                    Database.insertRelation(dbcon, conKey, certKey)
                    commit_counter += 1
                    relations_added += 1                                           
                certificates_processed += 1
                  
        logging.info ('{} {}: {}:{} -> {}:{} : {} certificate(s)'.format(pkt.time, direction, srcIp, srcPort, dstIp, dstPort, certificates_processed))                
        
        if certificates_processed == 0 or db_check_existing and None != Database.getConnection (dbcon, conKey):
            logging.info ('Existing connection ' +conKey)
            connections_skipped += 1        
        else:
            logging.info ('Adding new connection ' +conKey)
            Database.insertConnection(dbcon, conKey,connection)
            commit_counter += 1
            connections_added += 1
    
        if (commit_counter >= db_commit_after):
            commit_counter = 0
            logging.info ("Committing database!")
            Database.databaseCommit(dbcon)
        packets_included +=1
    except Exception as e:
        logging.error ("Error parsing packet!: ")
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback,
                              limit=2, file=sys.stdout)

def parse_file(filename):
    global dbcon
    try:
        sniff (offline=filename, prn=process_packet, store=0)
    except IOError:
        print ("File '" +filename+ "' not found")
        return
    Database.databaseCommit(dbcon)
    
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
    global Database
        
    infoLogger = logging.getLogger()
    infoLogger.setLevel(logging.INFO)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.WARN)
    formatter = logging.Formatter('%(asctime)s - %(levelname)-7s - %(message)s')
    ch.setFormatter(formatter)
    infoLogger.addHandler(ch)  
    
    dbDir = None
    logDir = None
    parser = None
    
    if (5 == len(sys.argv)):
        parser = sys.argv[1]
        inputFile = sys.argv[2];
        dbDir = sys.argv[3];
        logDir = sys.argv[4];
    else:
        print ("Supported parseModules:\n\tDatabaseSQLWriter\t: writes SQL insert statements\n\tDatabaseSqlite\t: writes directly to sqlite db\n\tDatabaseCsvWriter\t: writes CSV output\n")
        print ("Usage: ./Parser.py <parserModule> <inputfile> <result dir/file> <logdir>\n")        
        sys.exit(1);

    if not logDir.endswith("/"):
        logDir = logDir + "/"
        
    if ("DatabaseSQLWriter" == parser):
        Database = DatabaseSQLWriter
    elif ("DatabaseSqlite" == parser):
        Database = DatabaseSqlite
    elif ("DatabaseCsvWriter" == parser):
        Database = DatabaseCsvWriter    
    else: 
        logging.error("Invalid database module")
        sys.exit(1)    
         
        
    if (None == logDir):
        logDir = "./"    
    logfilename = logDir + inputFile.split("/")[len(inputFile.split("/"))-1] + '.log'

    logging.warn ("Writing logs to " + logfilename) 
    logFile = open(logfilename,'w')
    ch = logging.StreamHandler(logFile)
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)-7s - %(message)s')
    ch.setFormatter(formatter)
    infoLogger.addHandler(ch)      
    
    logging.warn ("Current directory: " + os.path.dirname(os.path.realpath(__file__)))
    logging.warn ("Loading input file '" + inputFile + "'")
    logging.warn ("Loading client certificates: " + str(include_client_certs))
    logging.warn ("Loading server certificates: " + str(include_server_certs))
    
    if ((parser == "DatabaseSQLWriter") or (parser == "DatabaseCsvWriter")):
        if not dbDir.endswith("/"):
            dbDir = dbDir + "/"    
        dbFile = dbDir + inputFile.split("/")[len(inputFile.split("/"))-1]
        
    if (parser == "DatabaseSqlite"):
        dbFile = dbDir
    
    if (not dbFile.endswith(Database.databaseGetFileExtension())):
        dbFile += Database.databaseGetFileExtension()
        
    
    logging.warn ("Opening database '" + dbFile + "'")
    dbcon = Database.databaseOpen(dbFile)
    
    logging.warn ("Setting up database '" + dbFile + "'")
    Database.databaseSetup(dbcon)

    packet_counter_timestamp = datetime.datetime.now()
    timestamp_start = datetime.datetime.now()
    parse_file(inputFile)
    timestamp_end = datetime.datetime.now()
    
    logging.warn  ("Start time: " + str(timestamp_start))
    logging.warn  ("End time: " + str(timestamp_end))
    logging.warn  ("Duration: " + str(timestamp_end - timestamp_start))
     
    logging.warn  ("Packets total: " + str(packets_total))
    logging.warn ("Packets processed: " + str(packets_processed))
    logging.warn ("Packets discarded: " + str(packets_discarded))
    logging.warn ("Packets included: " + str(packets_included))

    logging.warn ("Connections added: " + str(connections_added))
    logging.warn ("Connections skipped: " + str(connections_skipped))

    logging.warn ("Certificates added: " + str(certificates_added))
    logging.warn ("Certificates skipped: " + str(certificates_skipped))
    logging.warn ("Certificates corrupt: " + str(certificates_corrupt))

    logging.warn ("Relations added: " + str(relations_added))
    logging.warn ("Relations skipped: " + str(relations_skipped))

    logging.warn ("IP mappings added successful: " + str(ipmappings_added_successful))
    logging.warn ("IP mappings added failing: " + str(ipmappings_added_failed))
    logging.warn ("IP mappings skipped: " + str(ipmappings_skipped))

    logging.warn ("Closing database '" + dbFile + "'")
    Database.databaseClose(dbcon)   
    logFile.close()  

if __name__ == '__main__':
    main()
    
    
