
import sqlite3

def databaseGetFileExtension ():
    return ".db"

def databaseOpen (dbFile):
    return sqlite3.connect(dbFile)

def databaseClose (dbcon):
    dbcon.close()

def databaseSetup (dbcon):
    createConnectionTable(dbcon)
    createRelationsTable(dbcon)
    createCertificateTable(dbcon)
    createExtensionsTable(dbcon)
    createInvalidCertificateTable(dbcon)
    createIpHostnameMappingTable(dbcon)       

def databaseCommit (dbcon):
    dbcon.commit()
    

def createConnectionTable (dbcon):
    dbcon.execute('''CREATE TABLE IF NOT EXISTS connections
             (conKey text NOT NULL UNIQUE PRIMARY KEY,
             timestamp text, direction text, 
             src_ip text, src_port integer, 
             dst_ip text, dst_port integer)''')    
    dbcon.execute('''CREATE INDEX IF NOT EXISTS connectionsIndex ON connections (conKey);''')    
    dbcon.commit()      
    
def createCertificateTable (dbcon):
    dbcon.execute('''CREATE TABLE IF NOT EXISTS certificates
             (certKey text NOT NULL UNIQUE PRIMARY KEY, 
             cert_version text, cert_serialnumber text, 
             cert_subject text, cert_pubkey_modulus text, cert_pubkey_size text, 
             cert_notbefore text, cert_notafter text, 
             cert_issuer text, cert_fingerprint text, 
             cert_extension_count integer)''')
    dbcon.execute('''CREATE INDEX IF NOT EXISTS certificatesIndex ON certificates (certKey);''')          
    dbcon.commit()    
    
def createRelationsTable (dbcon):
    dbcon.execute('''CREATE TABLE IF NOT EXISTS relations
             (certKey TEXT, conKey TEXT, 
              FOREIGN KEY(conKey) REFERENCES connections(conKey),  
              FOREIGN KEY(certKey) REFERENCES certificates(certKey))''')
    dbcon.execute('''CREATE INDEX IF NOT EXISTS relationsIndex ON relations (certKey, conKey);''')      

def createExtensionsTable (dbcon):  
    dbcon.execute('''CREATE TABLE IF NOT EXISTS extensions
             (certKey TEXT,ext_name TEXT, ext_value TEXT,
             FOREIGN KEY(certKey) REFERENCES certificates(certKey))''')
    dbcon.execute('''CREATE INDEX IF NOT EXISTS extensionsIndex ON extensions (certKey);''')      
    dbcon.commit()

    
def createIpHostnameMappingTable (dbcon):
    dbcon.execute('''CREATE TABLE IF NOT EXISTS mappings
             (ip text NOT NULL, hostname text, error text)''')
    dbcon.execute('''CREATE INDEX IF NOT EXISTS mappingsIndex ON mappings (ip);''')  
    dbcon.commit()
    
def createInvalidCertificateTable (dbcon):  
    dbcon.execute('''CREATE TABLE IF NOT EXISTS invalid 
            (conKey TEXT, dercert BLOB, 
            FOREIGN KEY(conKey) REFERENCES connections(conKey))''')
    dbcon.execute('''CREATE INDEX IF NOT EXISTS invalidIndex ON invalid (conKey);''')      
    dbcon.commit()    
    
def getConnection (dbcon, key):
    c = dbcon.cursor()
    args = (key,)
    c.execute('SELECT * FROM connections WHERE conKey=?', args)
    res = c.fetchone()
    return res

def insertConnection (dbcon, key, connection):
    c = dbcon.cursor()
    args = (key, connection.time, connection.direction,
            connection.networkconnection.src_ip,
            connection.networkconnection.src_port,
            connection.networkconnection.dst_ip,
            connection.networkconnection.dst_port)
    c.execute('INSERT INTO connections (conKey, timestamp, direction, src_ip, src_port, dst_ip, dst_port) VALUES (?,?,?,?,?,?,?)', args)

def getRelation (dbcon, connKey, certKey):
    c = dbcon.cursor()
    args = (connKey, certKey,)
    c.execute('SELECT * FROM relations WHERE conKey=? AND certKey=? ', args)
    res = c.fetchone()
    return res

def insertRelation (dbcon, connKey, certKey):
    c = dbcon.cursor()
    args = (connKey, certKey)
    c.execute('INSERT INTO relations (conKey, certKey) VALUES (?,?)', args)


def getCertificate (dbcon, key):
    c = dbcon.cursor()
    args = (key,)
    c.execute('SELECT * FROM certificates WHERE certKey=?', args)
    res = c.fetchone()
    return res

def insertCertificate (dbcon, key, certificate):
    c = dbcon.cursor()    
    conn = (key, 
            certificate.cert_version, str(certificate.cert_serialnumber), 
            certificate.cert_subject, certificate.cert_pubkey_modulus, 
            certificate.cert_pubkey_size, certificate.cert_notbefore, 
            certificate.cert_notafter, certificate .cert_issuer, 
            certificate.cert_fingerprint, certificate.cert_extension_count)
    c.execute('INSERT INTO certificates (certKey,cert_version, cert_serialnumber, cert_subject, cert_pubkey_modulus,cert_pubkey_size, cert_notbefore,cert_notafter, cert_issuer,cert_fingerprint, cert_extension_count) VALUES (?,?, ?,?, ?,?, ?,?, ?,?, ?)', conn)

def getExtension (dbcon, certKey, name):
    c = dbcon.cursor()
    args = (certKey, name)
    c.execute('SELECT * FROM extensions WHERE certKey=? AND ext_name=?', args)
    res = c.fetchone()
    return res

def insertExtension(dbcon, certKey, extension):
    c = dbcon.cursor()
    args = (certKey, extension.name, extension.value,)
    c.execute('INSERT INTO extensions (certKey, ext_name, ext_value) VALUES (?,?,?)', args)


def insertInvalidCertificate(dbcon, conKey, certificate):
    c = dbcon.cursor()
    args = (conKey, sqlite3.Binary(certificate),)
    c.execute('INSERT INTO invalid (conKey, dercert) VALUES (?,?)', args)


def getIpHostnameMapping(dbcon, ip):
    c = dbcon.cursor()
    args = (ip, )
    c.execute('SELECT * FROM mappings WHERE ip=?', args)
    res = c.fetchone()
    return res

def insertIpHostnameMapping(dbcon, ip, hostname, error):
    c = dbcon.cursor()
    args = (ip, hostname,error, )
    c.execute('INSERT INTO mappings (ip, hostname, error) VALUES (?,?,?)', args)


