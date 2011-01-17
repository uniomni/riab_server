#!/usr/bin/env python
#coding:utf-8
# Author:   AIDRF www.aifdr.org
# Purpose:  Common Functions
# Created: 01/16/2011

# Logging #
import logging
import io

LOG_FILENAME="out"
logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG)

# Configuration Support
import ConfigParser
default_config="""
[Server]
port=8000
server_url=localhost
[Plugins]
basepath="."
"""

config = ConfigParser.ConfigParser()
config.readfp(io.BytesIO(default_config))
config.read('riab_server.cfg')

port=config.getint("Server","port")
server_url=config.get("Server","server_url")


