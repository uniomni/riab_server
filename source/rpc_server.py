#!/usr/bin/env python
#coding:utf-8
# Author:   AIDRF www.aifdr.org
# Purpose:  Generalizaed RPC server
# Created: 01/16/2011

from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
import sys
import unittest
import ConfigParser
import logging
from common import *

class APITest():
    API_VERSION="0.1a"
    
    def version(self):
        return self.API_VERSION
    
    def test(self):
        print "hello"
        return True
        
class RPCServer():
    # The stateless RIAB server
    
    
    def __init__(self, url, port, api_class, api_module=None):
        # Restrict to a particular path.
        class RequestHandler(SimpleXMLRPCRequestHandler):
            xmlrpcpath="/RPC2"
    
            rpc_paths = (xmlrpcpath)

        self.api_class=api_class
        self.api_module=api_module

        # Create server
        self.server = SimpleXMLRPCServer((url, port),
                                    requestHandler=RequestHandler)
        logging.debug('XMLRPC Server instantiated.')
        # register functions that allow listMethods, methodHelp and methodSignature.
        self.server.register_introspection_functions()
        
        # Register an instance; all the methods of the apiclass instance are
        # published as XML-RPC methods 
        self.server.register_instance(api_class())
        logging.debug('API Registered.')
        
        self.server.register_function(self.stop)
        self.server.register_function(self.reload)


    def reload(self):
        if self.api_module:
            reload(self.api_module)
        # To do work out how to handle this without direct ref
        self.server.register_instance(self.api_module.RiabAPI())
        return "SUCESS: %s reloaded"%str(self.api_module)

            
    def start(self):
        # Run the server's main loop
        logging.debug('Server Started.')
        self.server.serve_forever()
        
    def stop(self):
        logging.debug('Server Stopped.')
        self.server.shutdown()
        return "stopping"
    

if __name__=='__main__':
    unittest.main()
