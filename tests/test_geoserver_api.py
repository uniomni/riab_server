#!/usr/bin/env python

import os
import sys
import numpy
import unittest


# Add location of source code to search path so that API can be imported
parent_dir = os.path.split(os.getcwd())[0]
source_path = os.path.join(parent_dir, 'source') 
sys.path.append(source_path)

# Import everything from the API
from riab_api import *


class Test_API(unittest.TestCase):

    def setUp(self):
        self.api = RiabAPI()
            
    def tearDown(self):
        pass

    def test_geoserver_layer_handles(self):
        """Test that layer handles are correctly formed and unpacked"""
        
        username='alice'
        userpass='cooper'
        geoserver_url='schools.out.forever'
        layer_name='poison'
        lh = self.api.create_geoserver_layer_handle(username, userpass, geoserver_url, layer_name)
        assert lh == 'alice:cooper@schools.out.forever:poison'

        s1, s2, s3, s4 = self.api.split_geoserver_layer_handle(lh)                
        assert s1 == username
        assert s2 == userpass
        assert s3 == geoserver_url        
        assert s4 == layer_name

    def test_connection_to_geoserver(self):
        """Test that geoserver can be reached using layer handle"""
        
        # FIXME(Ole): I think these should be defaults e.g. in config.py
        geoserver_url = 'http://localhost:8080/geoserver'
        username = 'admin'
        userpass = 'geoserver'
        layer_name = 'tasmania_roads'

        lh = self.api.create_geoserver_layer_handle(username, userpass, geoserver_url, layer_name)        
        res = self.api.check_geoserver_layer_handle(lh) 
        
        msg = 'Was not able to access Geoserver layer: %s' % lh
        assert res == 'SUCCESS', msg               
        
        
################################################################################

if __name__ == '__main__':
    suite = unittest.makeSuite(Test_API, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
