existingCertificates = {}
existingConnections = {}
existingRelations = {}
existingHostmappings = {}
existingExtensions = {}

dummyValue = "ABCDE"

class Handler:
    fileCert = None
    fileConnections = None
    fileRelations = None
    fileMappings = None 
    fileExtensions = None
    fileInvalidCertificates = None   
    test = "1234"

def databaseGetFileExtension ():
    return ".csv"

def databaseOpen (dbFile):
    handler = Handler()    
    fileOnly = dbFile.split("/")[len(dbFile.split("/"))-1]
    
    k = dbFile.rfind("/")    
    pathOnly = dbFile[:k+1] 
        
    fileName = pathOnly + "certificates_" + fileOnly; 
    print (fileName)
    handler.fileCert = open (fileName,'w')

    fileName = pathOnly + "connections_" + fileOnly; 
    print (fileName)
    handler.fileConnections = open (fileName,'w')

    fileName = pathOnly + "relations_" + fileOnly; 
    print (fileName)
    handler.fileRelations = open (fileName,'w')

    fileName = pathOnly + "extensions_" + fileOnly; 
    print (fileName)
    handler.fileExtensions = open (fileName,'w')

    fileName = pathOnly + "mappings_" + fileOnly; 
    print (fileName)
    handler.fileMappings = open (fileName,'w')

    fileName = pathOnly + "invalid_" + fileOnly; 
    handler.fileInvalidCertificates = open (fileName,'w')
    return handler

def databaseClose (dbCon):
    dbCon.fileCert.close()
    dbCon.fileConnections.close()
    dbCon.fileRelations.close()
    dbCon.fileMappings.close()
    dbCon.fileExtensions.close()
    dbCon.fileInvalidCertificates.close()        

def databaseCommit (dbCon):
    return

def databaseSetup (dbCon):
    createConnectionTable(dbCon)
    createCertificateTable(dbCon)
    createRelationsTable(dbCon)
    createExtensionsTable(dbCon)
    createInvalidCertificateTable(dbCon)
    createIpHostnameMappingTable(dbCon)       
        
    
def createConnectionTable (dbCon):    
    dbCon.fileConnections.write ("#conKey;timestamp;direction;src_ip;src_port;dst_ip;dst_port\n")
    
def createCertificateTable (dbCon):
    dbCon.fileCert.write ("#certKey;cert_version;cert_serialnumber;cert_subject;cert_pubkey_modulus;cert_pubkey_size; cert_notbefore;cert_notafter;cert_issuer;cert_fingerprint;cert_extension_count\n")
    
def createRelationsTable (dbCon):
    dbCon.fileRelations.write ("#conKey;certKey;\n")

def createExtensionsTable (dbCon):
    dbCon.fileExtensions.write ("#conKey;ext_name;ext_value\n")
     
def createIpHostnameMappingTable (dbCon):
    dbCon.fileMappings.write ("#ip;hostname;error\n")

def createInvalidCertificateTable (dbCon):  
    dbCon.fileInvalidCertificates.write ("#conKey;dercert;\n")
    return
     
def getConnection (dbCon, key):
    if existingConnections.has_key(key):
        return dummyValue;
    return None

def insertConnection (dbCon, key, connection):
    existingConnections[key] = dummyValue;
    dbCon.fileConnections.write ("{};{};{};{};{};{};{}\n".format(
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
    dbCon.fileRelations.write ('{};{}\n'.format(conKey, certKey))
    return


def getCertificate (dbCon, key):
    if existingCertificates.has_key(key):
        return dummyValue;
    return None

def insertCertificate (dbCon, key, certificate):
    existingCertificates[key] = dummyValue;
    dbCon.fileCert.write ("{};{};{};{};{};{};{};{};{};{};{}\n".format(
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
    dbCon.fileExtensions.write ("{};{};{}\n".format(certKey, extension.name,extension.value))
    return

def insertInvalidCertificate(dbCon, conKey, pemcertificate):
    dbCon.fileInvalidCertificates.write ("{};{}\n".format(conKey, pemcertificate))
    return

def getIpHostnameMapping(dbCon, ip):
    if existingHostmappings.has_key(ip):
        return dummyValue;
    return None

def insertIpHostnameMapping(dbCon, ip, hostname, error):
    existingHostmappings[ip] = dummyValue;
    dbCon.fileMappings.write ("{};{};{}\n".format(ip, hostname, error))
    return

