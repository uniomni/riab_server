#!/usr/bin/env python

import sys, os, string
import numpy
import unittest
import pycurl
import StringIO
import json
import xmlrpclib
from config import test_url

class Test_Riab_Server(unittest.TestCase):

    have_reloaded = False
    
    def setUp(self):
        """Connect to test geoserver with new instance
        """
            
        self.riab_server = xmlrpclib.ServerProxy(test_url)
        try:
            if not self.have_reloaded:
                s = self.riab_server.reload()
                self.have_reloaded = True
        except:
            print 'Warning can\'t reload classes!'
            
    def tearDown(self):
        """Destroy test geoserver again next test
        """
        
        pass
        

    def test_riab_server_reload(self):
        """Test the reload function
        """
        # make sure the latest classes are being used
        
        s = self.riab_server.reload()
        assert s.startswith('SUCCESS'), 'Problem with the reload'
        
        # Exception will be thrown if there is no server

    def test_riab_server_version(self):
        """Test that local riab server is running
        """
        # make sure the latest classes are being used
        
        s = self.riab_server.version()
        assert s.startswith('0.1a'), 'Version incorrect %s' % s
        
        # Exception will be thrown if there is no server

    
    
    def test_create_geoserver_handle(self):
        """Test that handles are created correctly
        """

        s = self.riab_server.create_geoserver_layer_handle('ted', 'test', 'www.geo.com', 'map')
        msg = 'Wrong handle returned %s' % s
        assert s == 'ted:test@www.geo.com:map', msg

        # FIXME (Ole): Think of some more testing here
        
            
 

################################################################################

if __name__ == '__main__':
    suite = unittest.makeSuite(Test_Riab_Server, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
