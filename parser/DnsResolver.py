'''
Created on Aug 26, 2016

@author: mwachs
'''

import logging, socket

def resultCallback (ip, error, name, alias, addresslist):
    if None == error:
        logging.debug("Resolved " + ip + " ->" + name)
    else:
        logging.debug("Failed to resolve " + ip + " : " + error)

def reverseNameResolution (ip, resCb=resultCallback):
    logging.debug("Resolving '" + ip + "'")
    name = None
    alias= None
    addresslist = None 
    try:
        name, alias, addresslist  = socket.gethostbyaddr(ip)
    except Exception as e:
        pass
        logging.debug("Failed to resolve '" + ip + "' : " +str(e))
        resCb (ip, str(e), None, None, None)
        return
    resCb (ip, None, name, alias, addresslist)