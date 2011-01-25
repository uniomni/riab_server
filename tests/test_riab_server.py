#!/usr/bin/env python

import sys, os
import unittest
import xmlrpclib
import pycurl, StringIO, json
from config import test_workspace_name, geoserver_url, geoserver_username, geoserver_userpass
from config import test_url

from utilities import get_web_page, get_bounding_box

class Test_Riab_Server(unittest.TestCase):

    have_reloaded = False
    
    def setUp(self):
        """Connect to test geoserver with new instance
        """
            
        self.api = xmlrpclib.ServerProxy(test_url)
        try:
            if not self.have_reloaded:
                s = self.api.reload()
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
        
        s = self.api.reload()
        assert s.startswith('SUCCESS'), 'Problem with the reload'
        
        # Exception will be thrown if there is no server

    def test_riab_server_version(self):
        """Test that local riab server is running
        """
        # make sure the latest classes are being used
        
        s = self.api.version()
        assert s.startswith('0.1a'), 'Version incorrect %s' % s
        
        # Exception will be thrown if there is no server

    
    
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
        
        # Test with and without workspaces as well as with and without port
        username='alice'
        userpass='cooper'
        layer_name='poison'

        for layer_name in ['poison', '']:
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
        
                

    def test_connection_to_geoserver(self):
        """Test that geoserver can be reached using layer handle"""
        
        geoserver_url = 'http://localhost:8080/geoserver'
        username = 'admin'
        userpass = 'geoserver'
        layer_name = '' # This is not verified
        workspace = 'topp'
        
        s = self.api.create_geoserver_layer_handle(username, userpass, geoserver_url, layer_name, 
                                                   workspace)
        res = self.api.check_geoserver_layer_handle(s)
        
        msg = 'Was not able to access Geoserver with handle: %s' % s
        assert res == 'SUCCESS', msg
        
        
    def test_create_workspace(self):            
        """Test that new workspace can be created
        """
        
        geoserver_url = 'http://localhost:8080/geoserver'
        username = 'admin'
        userpass = 'geoserver'
        
        # Create workspace
        
        # FIXME(Ole): XMLRPC complains: cannot marshal None unless allow_none is enabled
        # FIXME(Ole): However, no variable is None here. Does my head in.
        for var in [username, userpass, geoserver_url, test_workspace_name]:
            assert var is not None
        
        self.api.create_workspace(username, userpass, geoserver_url, test_workspace_name)
        
        # Check that workspace is there
        found = False
        page = get_web_page(os.path.join(geoserver_url, 'rest/workspaces'), 
                            username=username, 
                            password=userpass)
        for line in page:
            if line.find('rest/workspaces/%s.html' % test_workspace_name) > 0:
                found = True

        msg = 'Workspace %s was not found in %s' % (test_workspace_name, geoserver_url)        
        assert found, msg
        
        
    def test_upload_coverage(self):
        """Test that a coverage can be uploaded and a new style is created
        """
        
        # Create workspace
        self.api.create_workspace(geoserver_username, geoserver_userpass, geoserver_url, test_workspace_name)        
        
        # setup layer, file, sld and style names
        layername = 'shakemap_padang_20090930'
        raster_file = 'data/%s.asc' % layername
        expected_output_sld_file = '%s.sld' % layername 
        stylename = layername 
        
        # Form layer handle
        lh = self.api.create_geoserver_layer_handle(geoserver_username, 
                                                    geoserver_userpass, 
                                                    geoserver_url, 
                                                    '',   # Empty layer means derive from filename
                                                    test_workspace_name)
                
        # Upload coverage
        self.api.upload_geoserver_layer(raster_file, lh)

        # Check that layer is there
        found = False
        page = get_web_page(os.path.join(geoserver_url, 'rest/layers'), 
                            username=geoserver_username, 
                            password=geoserver_userpass)
        for line in page:
            if line.find('rest/layers/%s.html' % layername) > 0:
                found = True
        
        msg = 'Did not find layer %s in geoserver %s' % (layername, geoserver_url)
        assert found, msg        
        

        # Test style by grabbing the json
        c = pycurl.Curl()
        url = ((geoserver_url+'/rest/layers/%s') % layername)
        c.setopt(pycurl.URL, url)
        c.setopt(pycurl.HTTPHEADER, ['Accept: text/json'])
        c.setopt(pycurl.USERPWD, '%s:%s' % (geoserver_username, geoserver_userpass))
        c.setopt(pycurl.VERBOSE, 0)
        b = StringIO.StringIO()
        c.setopt(pycurl.WRITEFUNCTION, b.write)
        c.perform()

        try:
            d = json.loads(b.getvalue())
            def_style = d['layer']['defaultStyle']['name']
        except:
            def_style = b.getvalue()
            
        msg =   'Expected: '+stylename
        msg +=   'Got: '+def_style+"\n"
        assert def_style == stylename, msg

            
    def test_impact_model_using_riab_api(self):
        """Test that impact model can be computed correctly using riab server api through XMLRPC
        """
        
        # Common variables
        bounding_box = [96.956, -5.519, 104.641, 2.289]        
        
        # Upload hazard data
        lh = self.api.create_geoserver_layer_handle(geoserver_username, 
                                                    geoserver_userpass, 
                                                    geoserver_url, 
                                                    '',
                                                    test_workspace_name)

        hazard_level = 'shakemap_padang_20090930'                                                    
        self.api.upload_geoserver_layer('data/%s.asc' % hazard_level, lh)
        
                    
        for exposure_data, expected_fatality_data in [('population_padang_1', 'fatality_padang_1'),
                                                      ('population_padang_2', 'fatality_padang_2')]:
            
            # Upload exposure and expected fatalities
            self.api.upload_geoserver_layer('data/%s.asc' % exposure_data, lh)
            self.api.upload_geoserver_layer('data/%s.asc' % expected_fatality_data, lh)
            
            # Create handles for hazard and exposure
            haz_handle = self.api.create_geoserver_layer_handle(geoserver_username, 
                                                                geoserver_userpass, 
                                                                geoserver_url, 
                                                                hazard_level,
                                                                test_workspace_name)            

            exp_handle = self.api.create_geoserver_layer_handle(geoserver_username, 
                                                                geoserver_userpass, 
                                                                geoserver_url, 
                                                                exposure_data,
                                                                test_workspace_name)  
            
            # Get raster for for expected impact result                                             
            lh = self.api.create_geoserver_layer_handle(geoserver_username, 
                                                        geoserver_userpass, 
                                                        geoserver_url, 
                                                        expected_fatality_data,
                                                        test_workspace_name)    
                                                                                               
            #XX reference_raster = self.api.get_raster_data(lh, bounding_box)         
            
            # Create handle for calculated result
            imp_handle = self.api.create_geoserver_layer_handle(geoserver_username, 
                                                                geoserver_userpass, 
                                                                geoserver_url, 
                                                                expected_fatality_data + '_calculated_by_riab',
                                                                test_workspace_name)                
                                                             
            # Calculate impact using API: using default impact function for the moment
            self.api.calculate(haz_handle, exp_handle, 0, imp_handle, bounding_box, '')
            filename = 'download.tif'
            try:
                os.unlink(filename)
            except:
                pass 
            calculated_raster_layer = self.api.download_geoserver_raster_layer(imp_handle, bounding_box, filename)
            open(filename)

            # FIXME: Check with gdalinfo that file contents are correct
            # Also compare contents with reference file
            return

            # Download calculated layer 
            #XXcalculated_raster = self.api.get_raster_data(imp_handle, bounding_box)         
                        # Extract calculated and reference data
            C = calculated_raster.get_data()            
            R = reference_raster.get_data()
            
            R = R[:-1,:-1] # FIXME(Ole): Hack - GeoServer does not preserve this

            assert numpy.allclose(C.shape, R.shape)
                        
            # Verify correctness
            msg = 'Computed impact not as expected'
            
            err = C-R

            
            # FIXME(Ole): Look at these tolerances once bounding box and precision issues with GDAL and Geoserver have been resolved.
            max_dif = numpy.max(numpy.abs(err[:]))
            #print 'max_dif', max_dif
            assert max_dif < 1.0e-2, msg
            
            rel_dif = max_dif/numpy.max(numpy.abs(R[:]))
            #print 'rel_dif', rel_dif            
            assert rel_dif < 1.0e-2, msg
                        
            assert numpy.allclose(C, R, rtol=1.0e-6, atol=1.0e-2), msg
            

################################################################################

if __name__ == '__main__':
    suite = unittest.makeSuite(Test_Riab_Server, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
