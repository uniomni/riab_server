#!/usr/bin/env python
#coding:utf-8
# Author:   AIDRF www.aifdr.org
# Purpose:  Act as the RIAB server
# Created: 01/16/2011

import sys
import unittest
import ConfigParser
import common
import riab_api

from rpc_server import RPCServer

#config = ConfigParser.RawConfigParser()



class RiabServer(RPCServer):
    def __init__(self):
        
        
        # register the api
        RPCServer.__init__(self, 'localhost', 8000, riab_api.RiabAPI, riab_api)
        
if __name__=='__main__':
    RiabServer().start()
    unittest.main()
