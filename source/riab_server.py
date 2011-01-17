#!/usr/bin/env python
#coding:utf-8
# Author:   AIDRF www.aifdr.org
# Purpose:  Act as the RIAB server
# Created: 01/16/2011

import sys
import unittest
import common
import riab_api

from rpc_server import RPCServer


class RiabServer(RPCServer):
    """Base class for the Risk-in-a-Box server"""
    
    def __init__(self):
        
        # Register the api
        RPCServer.__init__(self, 
                           common.server_url, 
                           common.port, 
                           riab_api.RiabAPI, 
                           riab_api)
        
if __name__=='__main__':
    # TODO: Read from commandline args or from config
    # config = ConfigParser.RawConfigParser()
    # plugin files base
    RiabServer().start()
    unittest.main()
