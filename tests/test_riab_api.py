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

        
    def test_create_geoserver_handles_1(self):
        """Test that handles without workspace are created correctly
        """

        s = self.api.create_geoserver_layer_handle('ted', 'test', 'www.geo.com', 'map', '')
        msg = 'Wrong handle returned %s' % s
        assert s == 'ted:test@www.geo.com/map', msg
        
        
    def test_create_geoserver_handles_2(self):
        """Test that handles with workspace and port are created correctly
        """
        
        username = 'alice'
        userpass = 'cooper'
        layer_name = 'poison'
        geoserver_url = 'schools.out.forever:88'
        workspace = 'black'        

        s = self.api.create_geoserver_layer_handle(username, 
                                                   userpass, 
                                                   geoserver_url, 
                                                   layer_name, 
                                                   workspace)                    
            
        msg = 'Wrong handle returned %s' % s
        assert s == 'alice:cooper@schools.out.forever:88/[black]/poison', msg        
         
    def test_geoserver_layer_handles_3(self):
        """Test that layer handles are correctly formed and unpacked again"""
        
        # Test with and without workspaces as well as with and without port and html prefix
        username='alice'
        userpass='cooper'
        layer_name='poison'
        
        for port in ['', ':88']:
            for prefix in ['', 'html://']:
                geoserver_url = prefix + 'schools.out.forever' + port
            
                for workspace in ['black', '']:
            
                    s = self.api.create_geoserver_layer_handle(username, 
                                                               userpass, 
                                                               geoserver_url, 
                                                               layer_name, 
                                                               workspace)


                    s1, s2, s3, s4, s5 = self.api.split_geoserver_layer_handle(s)
                    assert s1 == username
                    assert s2 == userpass
                    assert s3 == geoserver_url
                    assert s4 == layer_name
                    assert s5 == workspace
                    

    def test_another_layer_handle_unpack_example(self):
        """Test unpack of admin:geoserver@http://localhost:8080/geoserver/[topp]/tasmania_roads           
        """
        
        layer_handle = 'admin:geoserver@http://localhost:8080/geoserver/[topp]/tasmania_roads'
        s1, s2, s3, s4, s5 = self.api.split_geoserver_layer_handle(layer_handle)
        
        assert s1 == 'admin'
        assert s2 == 'geoserver'
        assert s3 == 'http://localhost:8080/geoserver'
        assert s4 == 'tasmania_roads'
        assert s5 == 'topp'
        

    def test_connection_to_geoserver(self):
        """Test that geoserver can be reached using layer handle"""
        
        # FIXME(Ole): I think these should be defaults e.g. in config.py
        geoserver_url = 'http://localhost:8080/geoserver'
        username = 'admin'
        userpass = 'geoserver'
        layer_name = 'tasmania_roads'
        workspace = 'topp'        

        lh = self.api.create_geoserver_layer_handle(username, userpass, geoserver_url, layer_name,
                                                    workspace)
        res = self.api.check_geoserver_layer_handle(lh) 
        
        msg = 'Was not able to access Geoserver layer %s: %s' % (lh, res)
        assert res == 'SUCCESS', msg               
        
        
################################################################################

if __name__ == '__main__':
    suite = unittest.makeSuite(Test_API, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
