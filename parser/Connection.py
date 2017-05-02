'''
Created on Aug 23, 2016

@author: mwachs
'''

from NetworkConnection import NetworkConnection

class Connection:    
    time = None
    direction = None
    networkconnection = None
    certificates = None
    def append_cert (self, certificate):
        self.certificates.append(certificate)        
    def __init__ (self, time, direction, srcip, srcport, dstip, dstport, certificate=None):
        self.time = time 
        self.direction = direction
        self.networkconnection = NetworkConnection (srcip, srcport, dstip, dstport)
        self.certificates = list()
        if (None != certificate):
            self.certificates.append(certificate)
    def __str__ (self):
        certificates = ""
        for c in self.certificates:
            certificates += '{};'.format(str(c))
        return '{};{};{};{};{}'.format(self.time, self.direction, str(self.networkconnection), str(len(self.certificates)), certificates)