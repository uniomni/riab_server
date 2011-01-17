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
        
        
################################################################################

if __name__ == '__main__':
    suite = unittest.makeSuite(Test_API, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
