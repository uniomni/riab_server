"""Test suite for Risk-in-a-Box use cases
"""

import os, sys, unittest

# Add location of source code to search path so that API can be imported
parent_dir = os.path.split(os.getcwd())[0]
source_path = os.path.join(parent_dir, 'source') 
sys.path.append(source_path)

# Import everything from the API
from riab_api import *
from config import test_workspace_name, geoserver_url, geoserver_username, geoserver_userpass


class Test_Usecases(unittest.TestCase):

    def setUp(self):
        self.api = RiabAPI()
            
    def tearDown(self):
        pass


    def test_earthquake_fatality_estimation(self):
        """Test that fatalities from ground shaking can be computed correctly
        """
        
        # Create workspace
        self.api.create_workspace(geoserver_username, geoserver_userpass, geoserver_url, test_workspace_name)
                
        # Common variables
        bounding_box = [99.36, -2.199, 102.237, 0.000] # Padang area (same as BB of test data)
        
        # Upload hazard data
        lh = self.api.create_geoserver_layer_handle(geoserver_username, 
                                                    geoserver_userpass, 
                                                    geoserver_url, 
                                                    '',
                                                    test_workspace_name)

        hazard_level = 'Earthquake_Ground_Shaking_clip'                                                    
        self.api.upload_geoserver_layer('data/%s.tif' % hazard_level, lh)
        
                    
        for exposure_data, expected_fatality_data in [('Population_2010_clip', 'Earthquake_Fatalities_National_clip')]:
            
            # Upload exposure and expected fatalities
            self.api.upload_geoserver_layer('data/%s.tif' % exposure_data, lh)
            self.api.upload_geoserver_layer('data/%s.tif' % expected_fatality_data, lh)
            
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
            
            # Create handle for expected impact result                                             
            ref_handle = self.api.create_geoserver_layer_handle(geoserver_username, 
                                                                geoserver_userpass, 
                                                                geoserver_url, 
                                                                expected_fatality_data,
                                                                test_workspace_name)    
                                                                                               
            # Create handle for calculated result
            imp_handle = self.api.create_geoserver_layer_handle(geoserver_username, 
                                                                geoserver_userpass, 
                                                                geoserver_url, 
                                                                expected_fatality_data + '_calculated_by_riab',
                                                                test_workspace_name)                
                                                             
            # Calculate impact using API: using default impact function for the moment
            self.api.calculate(haz_handle, exp_handle, 0, imp_handle, bounding_box, '')
            
            
            # Do calculation manually and check result
            hazard_raster = self.api.get_raster_data(haz_handle, bounding_box)
            H = hazard_raster.get_data()            
            
            exposure_raster = self.api.get_raster_data(exp_handle, bounding_box)
            E = exposure_raster.get_data()                        
            
            print
            print H.shape
            print E.shape            
            
            # Compare numerical data
            calculated_raster = self.api.get_raster_data(imp_handle, bounding_box)
            C = calculated_raster.get_data()
            
            reference_raster = self.api.get_raster_data(ref_handle, bounding_box)
            R = reference_raster.get_data()            
            
            # FIXME (Ole): Why do the layers have different shapes? 
            print C.shape
            print R.shape
            


            
            
        
################################################################################

if __name__ == '__main__':
    suite = unittest.makeSuite(Test_Usecases, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
