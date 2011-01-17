#!/usr/bin/env python
#coding:utf-8
# Author:   AIDRF www.aifdr.org
# Purpose:  Common Functions
# Created: 01/16/2011

# Logging #
import logging

LOG_FILENAME="out"
logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG)

# Configuration Support
import ConfigParser

#config = ConfigParser.RawConfigParser()
