'''
    This file is part of CCA Parser.

    CCA Parser is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Foobar is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with CCA Parser.  If not, see <http://www.gnu.org/licenses/>.

'''

import sys, logging

try: 
    from M2Crypto import X509
except ImportError as e:
    print ("M2Crypto module not found: " + str(e))
    sys.exit(1) 

from CertificateExtension import CertificateExtension

class Certificate:
    der_certificate = None
    m2cert = None
    key = None
    cert_version = None
    cert_serialnumber = None
    cert_subject = None
    cert_pubkey_modulus = None
    cert_pubkey_size = None
    cert_notbefore = None
    cert_notafter = None
    cert_issuer = None
    cert_fingerprint = None
    cert_extension_count = None
    extensions = None
    def __init__ (self, der_certificate):
        self.der_certificate = der_certificate
        self.m2cert = X509.load_cert_der_string(der_certificate)    
        self.extract(self.m2cert)        
    def extract(self, cert):        
        self.cert_version = cert.get_version() + 1
        logging.debug ('\t{} : {}'.format('Version', self.cert_version))
        self.cert_serialnumber = cert.get_serial_number()
        logging.debug ('\t{} : {}'.format('Serialnumber', self.cert_serialnumber))
        self.cert_fingerprint = cert.get_fingerprint()
        logging.debug ('\t{} : {}'.format('Fingerprint', self.cert_fingerprint))        
        self.cert_subject = str(cert.get_subject())
        logging.info ('\t{} : {}'.format('Subject', self.cert_subject))
        self.cert_issuer = str(cert.get_issuer())
        logging.info ('\t{} : {}'.format('Issuer', self.cert_issuer))                
        self.cert_notbefore = str(cert.get_not_before())               
        logging.debug ('\t{} : {}'.format('Not before', self.cert_notbefore))
        self.cert_notafter = str(cert.get_not_after())     
        logging.debug ('\t{} : {}'.format('Not after', self.cert_notafter))                            
        self.cert_pubkey_modulus = str(cert.get_pubkey().get_modulus())
        logging.debug ('\t{} : {}'.format('Public key modulus', self.cert_pubkey_modulus))
        self.cert_pubkey_size = cert.get_pubkey().size() * 8
        logging.debug ('\t{} : {}'.format('Public key size', self.cert_pubkey_size))
        self.cert_extension_count = cert.get_ext_count()
        logging.debug('\t{} : {}'.format('#Extensions', self.cert_extension_count))         
        self.extensions = list()         
        # Iterate extensions
        for c in xrange(0, cert.get_ext_count() -1):
            ext = cert.get_ext_at(c)
            name = ext.get_name().strip()
            value = ext.get_value().strip()
            logging.debug ('\t "{}" : "{}"'.format(name, value))
            self.extensions.append(CertificateExtension(name, value))
    def getPemCertificate (self):
        return self.m2cert.as_pem()
    def setKey (self, key):
        self.key = key    
    def __str__ (self):     
        extensions = ""
        for e in self.extensions:
            extensions += '{};'.format(str(e))
        certstr = '{};{};{};{};{};{};{};{};{};{};{};'.format(
             self.key,
             self.cert_version, self.cert_serialnumber,
             self.cert_fingerprint, self.cert_subject, 
             self.cert_issuer, str(self.cert_notbefore),
             self.cert_notafter,self.cert_pubkey_size,
             self.cert_pubkey_modulus,self.cert_extension_count, 
             extensions)        
        return certstr
    