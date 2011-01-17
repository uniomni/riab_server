#!/usr/bin/env python
#coding:utf-8
# Author:   AIDRF www.aifdr.org
# Purpose:  Act as the RIAB server
# Created: 01/16/2011

import sys
import unittest
import common
import riab_api
import argparse

from rpc_server import RPCServer,stop_server


class RiabServer(RPCServer):
    """Base class for the Risk-in-a-Box server"""
    
    def __init__(self, server_url, port):
           
        # register the api
        RPCServer.__init__(self, server_url, port, riab_api.RiabAPI, riab_api)


def start_server(server_url,port):
    RiabServer(server_url,port).start()
    
if __name__=='__main__':
    parser = argparse.ArgumentParser(description = 'Riab Server')
    parser.add_argument('--port', type=int, default = common.port,
                   help='port for the server')
    parser.add_argument('--server', type=str, default = common.server_url,
                   help='server type')
    parser.add_argument('--stop', action='store_const',
                        const = stop_server, default = start_server,
                   help='stop the server if its running.')
    
    args = parser.parse_args()
    
    # By default call the server start
    args.stop(args.server,args.port) #TODO: Better naming convention for args??


