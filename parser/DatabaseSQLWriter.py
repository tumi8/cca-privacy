existingCertificates = {}
existingConnections = {}
existingRelations = {}
existingHostmappings = {}
existingExtensions = {}

dummyValue = "ABCDE"

def databaseGetFileExtension ():
    return ".sql"

def databaseOpen (dbFile):
    return open (dbFile,'w')

def databaseClose (dbCon):
    dbCon.close()

def databaseCommit (dbCon):
    return

def databaseSetup (dbCon):
    createConnectionTable(dbCon)
    createCertificateTable(dbCon)
    createRelationsTable(dbCon)
    createExtensionsTable(dbCon)
    createInvalidCertificateTable(dbCon)
    createIpHostnameMappingTable(dbCon)       
    
# CREATE TABLE IF NOT EXISTS connections
#              (conkey VARCHAR(60) NOT NULL, PRIMARY KEY(conkey), UNIQUE INDEX `conkey_INDEX` (conkey ASC),
#              timestamp VARCHAR(60), direction VARCHAR(10), 
#              src_ip VARCHAR(15), src_port INTEGER, 
#              dst_ip VARCHAR(15), dst_port INTEGER);
# 
# CREATE TABLE IF NOT EXISTS certificates
#              (certKey VARCHAR(60) NOT NULL, PRIMARY KEY(certkey), UNIQUE INDEX `certKey_INDEX` (certKey ASC),
#              cert_version VARCHAR(60), cert_serialnumber VARCHAR(60), 
#              cert_subject TEXT, cert_pubkey_modulus TEXT, 
#              cert_pubkey_size VARCHAR(60), 
#              cert_notbefore VARCHAR(60), cert_notafter VARCHAR(60), 
#              cert_issuer TEXT, cert_fingerprint VARCHAR(60), 
#              cert_extension_count integer);
#                           
# CREATE TABLE IF NOT EXISTS relations
#              (conkey VARCHAR(60), FOREIGN KEY (conkey) REFERENCES connections(conkey), 
#              certKey VARCHAR(60), FOREIGN KEY (certKey) REFERENCES certificates(certkey));             
# CREATE TABLE IF NOT EXISTS extensions
#              (certKey VARCHAR(60), FOREIGN KEY (certKey) REFERENCES certificates(certkey), 
#              ext_name VARCHAR(60), ext_value VARCHAR(255));
# CREATE TABLE IF NOT EXISTS invalid_certificates
#              (conKey VARCHAR(60) NOT NULL, dercert TEXT);
# CREATE TABLE IF NOT EXISTS ip_hostnames
#              (ip VARCHAR(60) NOT NULL, hostname VARCHAR(60), error VARCHAR(60));
    
    
def createConnectionTable (dbCon):    
    dbCon.write ('''CREATE TABLE IF NOT EXISTS connections
             (conKey VARCHAR(60) NOT NULL, PRIMARY KEY(conKey), UNIQUE INDEX `conKey_INDEX` (conKey ASC),
             timestamp VARCHAR(60), direction VARCHAR(10), 
             src_ip VARCHAR(15), src_port INTEGER, 
             dst_ip VARCHAR(15), dst_port INTEGER);\n''') 
    
def createCertificateTable (dbCon):
    dbCon.write ('''CREATE TABLE IF NOT EXISTS certificates
             (certKey VARCHAR(60) NOT NULL, PRIMARY KEY(certkey), UNIQUE INDEX `certKey_INDEX` (certKey ASC), 
             cert_version VARCHAR(60), cert_serialnumber VARCHAR(60), 
             cert_subject TEXT, cert_pubkey_modulus TEXT, 
             cert_pubkey_size VARCHAR(60), 
             cert_notbefore VARCHAR(60), cert_notafter VARCHAR(60), 
             cert_issuer TEXT, cert_fingerprint VARCHAR(60), 
             cert_extension_count integer);\n''')

def createRelationsTable (dbCon):
    dbCon.write ('''CREATE TABLE IF NOT EXISTS relations
             (conKey VARCHAR(60), FOREIGN KEY (conKey) REFERENCES connections(conKey), 
             certKey VARCHAR(60), FOREIGN KEY (certKey) REFERENCES certificates(certkey));\n''')

def createExtensionsTable (dbCon):  
    dbCon.write  ('''CREATE TABLE IF NOT EXISTS extensions
             (certKey VARCHAR(60), FOREIGN KEY (certKey) REFERENCES certificates(certkey), 
             ext_name VARCHAR(60), ext_value VARCHAR(255));\n''')
     
def createIpHostnameMappingTable (dbCon):
    dbCon.write ('''CREATE TABLE IF NOT EXISTS ip_hostnames
             (ip VARCHAR(60) NOT NULL, hostname VARCHAR(60), error VARCHAR(60));\n''')    

def createInvalidCertificateTable (dbCon):  
    dbCon.write ('''CREATE TABLE IF NOT EXISTS invalid_certificates
             (conKey VARCHAR(60) NOT NULL, dercert TEXT);\n''')
    return
     
def getConnection (dbCon, key):
    if existingConnections.has_key(key):
        return dummyValue;
    return None

def insertConnection (dbCon, key, connection):
    existingConnections[key] = dummyValue;
    dbCon.write ('''INSERT IGNORE INTO connections (conKey, timestamp, direction, src_ip, src_port, dst_ip, dst_port) VALUES ('{}','{}','{}','{}','{}','{}','{}');\n'''.format(
            key,
            connection.time,
            connection.direction, 
            connection.networkconnection.src_ip,
            connection.networkconnection.src_port,
            connection.networkconnection.dst_ip,
            connection.networkconnection.dst_port))
    return
    

def getRelation (dbCon, conKey, certKey):
    if existingRelations.has_key(str(conKey)+str(certKey)):
        return dummyValue;
    return None

def insertRelation (dbCon, conKey, certKey):
    existingRelations[str(conKey)+str(certKey)] = str(conKey)+str(certKey);
    dbCon.write ('INSERT IGNORE INTO relations (conKey, certKey) VALUES ("{}","{}");\n'.format(conKey, certKey))
    return


def getCertificate (dbCon, key):
    if existingCertificates.has_key(key):
        return dummyValue;
    return None

def insertCertificate (dbCon, key, certificate):
    existingCertificates[key] = dummyValue;
    dbCon.write ('''INSERT IGNORE INTO certificates (certKey,cert_version, cert_serialnumber, cert_subject, cert_pubkey_modulus,cert_pubkey_size, cert_notbefore, cert_notafter, cert_issuer,cert_fingerprint, cert_extension_count) VALUES ("{}","{}", "{}","{}", "{}","{}", "{}","{}", "{}","{}", "{}");\n'''.format(
            key, certificate.cert_version, str(certificate.cert_serialnumber), 
            certificate.cert_subject, certificate.cert_pubkey_modulus, 
            certificate.cert_pubkey_size, certificate.cert_notbefore, 
            certificate.cert_notafter, certificate .cert_issuer, 
            certificate.cert_fingerprint, certificate.cert_extension_count))
    return

def getExtension (dbCon, certKey, name):
    if existingExtensions.has_key(str(certKey)+str(name)):
        return dummyValue;
    return None

def insertExtension(dbCon, certKey, extension):
    existingExtensions[str(certKey)+str(extension.name)] = dummyValue;
    dbCon.write ('INSERT IGNORE INTO extensions (certKey, ext_name, ext_value) VALUES ("{}","{}","{}");\n'.format(certKey, extension.name,extension.value))
    return

def insertInvalidCertificate(dbCon, conKey, pemcertificate):
    dbCon.write ('''INSERT IGNORE INTO invalid_certificates (conKey, dercert) VALUES ("{}","{}");\n'''.format(conKey, pemcertificate))
    return

def getIpHostnameMapping(dbCon, ip):
    if existingHostmappings.has_key(ip):
        return dummyValue;
    return None

def insertIpHostnameMapping(dbCon, ip, hostname, error):
    existingHostmappings[ip] = dummyValue;
    dbCon.write ('INSERT IGNORE INTO ip_hostnames (ip, hostname, error) VALUES ("{}","{}","{}");\n'.format(ip, hostname, error))
    return

    
