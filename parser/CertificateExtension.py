'''
Created on Aug 23, 2016

@author: mwachs
'''

class CertificateExtension:
    name = None
    value = None
    def __init__ (self, name, value):
        self.name = name
        self.value = value
    def __str__(self):
        return '{}:{}'.format(self.name,self.value)