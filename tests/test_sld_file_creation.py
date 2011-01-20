import unittest

import sys, os, string
import numpy
import StringIO
import json
import pycurl
import unittest
import commands
from config import geoserver_url, geoserver_username, geoserver_userpass

# Add location of source code to search path so that API can be imported
parent_dir = os.path.split(os.getcwd())[0]
source_path = os.path.join(parent_dir, 'source') 
sys.path.append(source_path)

# Import everything from the API
from geoserver_api.geoserver import *



class Test_API_SLD(unittest.TestCase):
    """ This class will test the following:
    1 create a new sld file with a color map based on the raster file range
    2 create a new style on geoserver using the rest api
    3 upload the new style file using the geoserver rest api
    4 set the default style of the raster to be the newly created added style
    """

    def setUp(self):
        """Connect to test geoserver with new instance"""
    
        self.geoserver = Geoserver(geoserver_url,
                                   geoserver_username,
                                   geoserver_userpass)
        
        # Setup some default input parameters:
        self.raster_file = 'data/shakemap_padang_20090930.asc'
        self.layer_name = os.path.basename(os.path.splitext(self.raster_file)[0])
        self.expected_output_sld_file = 'shakemap_padang_20090930.sld' 
        self.reference_output_sld_file = 'data/reference_shakemap_padang_20090930.sld'
        self.style_name = os.path.splitext(self.expected_output_sld_file)[0]
    
    
    def tearDown(self):
        """Destroy test geoserver again next test
        """
        pass



    def test_style_layer_descriptor_creation_for_raster(self):
        """Test a new style layer descriptor file with a color map based on the given raster file's data range is created"""    
    
        if os.path.isfile(self.expected_output_sld_file):
            os.remove(self.expected_output_sld_file)
    
        # API Call to create an custom sld for our raster
        self.geoserver.create_raster_sld(self.raster_file)
        
        msg = 'Expected: file called '+self.expected_output_sld_file+' to be created'
        assert os.path.isfile(self.expected_output_sld_file), msg
        
        # Assert that no difference between expected style file and calculated style file
        diff = commands.getoutput('diff %s %s' % (self.expected_output_sld_file, 
                                                  self.reference_output_sld_file))
        msg =   'Expected: No difference between %s and %s' % (self.expected_output_sld_file, 
                                                               self.reference_output_sld_file)
        
        msg +=  'Got: %s' % diff
        assert diff == '', msg

        
    def test_existing_style_file_for_raster(self):
        """Test that an existing style layer descriptor file with a color map based on the given raster file's data range is uploaded if present"""    
        
        layername = stylename = 'mmi_lembang_68'
        raster_file = 'data/%s.txt' % layername
        workspace = 'ladidadida'
        
        # Create a workspace in case it wasn't there
        self.geoserver.create_workspace(workspace)
        
        # API Call to upload layer including its sld
        self.geoserver.upload_coverage(filename=raster_file, workspace=workspace)

        # Check that layer is there
        found = False
        page = get_web_page(os.path.join(geoserver_url, 'rest/layers'), 
                            username=geoserver_username, 
                            password=geoserver_userpass)
        for line in page:
            if line.find('rest/layers/%s.html' % layername) > 0:
                found = True
        

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
        
        # FIXME (Ole): Need to be able to download style and test

        
        
 
        
        
    # def test_style_layer_descriptor_creation_on_geoserver(self):
    #     """Test that the new custom style layer descriptor was correctly created on geoserver"""
    # 
    #     # load the sld file to server
    #     self.geoserver.create_style(self.style_name, self.expected_output_sld_file)
    # 
    #     c = pycurl.Curl()
    #     url = ((geoserver_url+"/rest/styles/%s") % self.style_name)
    #     c.setopt(pycurl.URL, url)
    #     c.setopt(pycurl.HTTPHEADER, ["Accept: text/json"])
    #     c.setopt(pycurl.USERPWD, "%s:%s" % (geoserver_username, geoserver_userpass))
    #     c.setopt(pycurl.VERBOSE, 0)
    # 
    #     b = StringIO.StringIO()
    #     c.setopt(pycurl.WRITEFUNCTION, b.write)
    #     c.perform()
    #     
    #     d = json.loads(b.getvalue())
    #     assert d['style']['name'] == self.style_name


    # def test_set_default_style_for_a_layer(self):
    #     """Test that the default style for the layer is the newly created custom SLD"""
    #     # Upload first to make sure data is there
    #     self.geoserver.upload_coverage(filename=self.raster_file, workspace=test_workspace_name)
    # 
    #     self.geoserver.set_default_style(self.style_name, self.layer_name)
    #     c = pycurl.Curl()
    #     url = ((geoserver_url+"/rest/layers/%s") % self.layer_name)
    #     c.setopt(pycurl.URL, url)
    #     c.setopt(pycurl.HTTPHEADER, ["Accept: text/json"])
    #     c.setopt(pycurl.USERPWD, "%s:%s" % (geoserver_username, geoserver_userpass))
    #     c.setopt(pycurl.VERBOSE, 0)
    #     b = StringIO.StringIO()
    #     c.setopt(pycurl.WRITEFUNCTION, b.write)
    #     c.perform()
    # 
    #     d = json.loads(b.getvalue())
    #     msg =   "Expected: "+self.style_name
    #     msg +=  " Got: "+d["layer"]["defaultStyle"]["name"]+"\n"
    # 
    #     assert d["layer"]["defaultStyle"]["name"] == self.style_name, msg


if __name__ == '__main__':
    unittest.main()
