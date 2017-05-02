'''
Created on Aug 23, 2016

@author: mwachs
'''

class NetworkConnection:
    src_ip = None
    src_port = None
    dst_ip = None
    dst_port = None
    def __init__ (self, srcip, srcport, dstip, dstport):
        self.src_ip = srcip
        self.src_port = srcport
        self.dst_ip = dstip
        self.dst_port = dstport
    def __str__ (self):
        return '{};{};{};{}'.format(self.src_ip,self.src_port,self.dst_ip,self.dst_port)    