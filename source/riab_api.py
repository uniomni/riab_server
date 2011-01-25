#!/usr/bin/env python
#coding:utf-8
# Author:   AIFDR www.aifdr.org
# Purpose:  Act as the Riab API
# Created: 01/16/2011

import os, string
from geoserver_api import geoserver
from geoserver_api.raster import write_coverage_to_ascii

class RiabAPI():
    API_VERSION='0.1a'
        
    def version(self):
        return self.API_VERSION
    
    
    def create_geoserver_layer_handle(self, username, userpass, geoserver_url, layer_name, workspace):
        """Create fully qualified geoserver layer name
        
        Arguments
            username=username
            userpass=password 
            geoserver_url=The URL of the geoserver   
            layer_name=name of data layer
            workspace=name of geoserver workspace (default is None)
            
            
        Returns
            layer_handle=string of the form:
                username:password@geoserver_url/[workspace/]layer_name
                
        Example         
            admin:geoserver@http://localhost:8080/geoserver/hazard/shakemap_padang_20090930
                 

                     
        """
        if workspace == '':
            return '%s:%s@%s/%s' % (username, userpass, geoserver_url, layer_name)
        else:
            return '%s:%s@%s/[%s]/%s' % (username, userpass, geoserver_url, workspace, layer_name)        

        
    def split_geoserver_layer_handle(self, geoserver_layer_handle):
        """Split fully qualified geoserver layer name into its constituents
        
        Arguments
            geoserver_layer_handle=string with format: 
                username:password@geoserver_url/[hazard]/shakemap_padang_20090930
            or
                username:password@geoserver_url/shakemap_padang_20090930            
                
                
            geoserver_url may optionally start with 'http://'
        """
        
        # Check that handle is well formed
        msg = 'Geoserver layer handle must have the form username:password@geoserver_url/[workspace]/layer_name. '
        msg += 'I got %s' % geoserver_layer_handle
        assert geoserver_layer_handle.find('@') > 0, msg
        assert geoserver_layer_handle.find(':') > 0, msg        
        assert geoserver_layer_handle.find('/') > 0, msg                
        
        
        # Separate username, password and everything following '@'
        userpass, gurl = geoserver_layer_handle.split('@')
        username, password = userpass.split(':')
        
        # Take care of optional http://, https:// etc
        i = gurl.find('://')
        split_index = i+3
        if i > 0: 
            url_prefix = gurl[:split_index]
            gurl = gurl[split_index:]
        else:
            url_prefix = ''
            
        # Split and get layername as last field    
        dirs = gurl.split('/')
        layer_name = dirs.pop()                            
                        
        # Take care of optional workspace enclosed in [..]    
        i = gurl.find('/[')
        j = gurl.find(']/')
        if i > 0 and j > i:
            workspace = dirs.pop()[1:-1] # Strip brackets ([ and ])            
        else:
            workspace = ''             # No workspace in string
            
        # Join remaining fields to form URL
        geoserver_url = url_prefix + string.join(dirs, '/')

        # Return    
        return username, password, geoserver_url, layer_name, workspace
    
    
    def check_geoserver_layer_handle(self, geoserver_layer_handle):
        """Check geoserver layer name
        
        Verify that layer name exists and can be accessed.
        
        Arguments
            geoserver_layer_handle = fully qualified geoserver layer name 
            
        Returns
            'SUCCESS' if complete
            ####'ERROR: CANNOT CONNECT TO GEOSERVER %s - ERROR MESSAGE IS %s' FIXME ????????

            
        Note    
            Check connection and presence of workspace. Ignore layer name.
                                
        """
        username, userpass, geoserver_url, layer_name, workspace =\
            self.split_geoserver_layer_handle(geoserver_layer_handle)
        
        gs = geoserver.Geoserver(geoserver_url, username, userpass)      
        gs.get_workspace(workspace, verbose=False)        
        
        return 'SUCCESS'

            
    def create_workspace(self, username, userpass, geoserver_url, workspace_name):
        """Create new workspace on GeoServer
        
        Arguments
            username=username
            userpass=password 
            geoserver_url=The URL of the geoserver   
            workspace=name of new geoserver workspace
            
        Returns
            'SUCCESS' if complete, otherwise Exception is raised.

        """
        # FIXME(Ole): This does not work with the general layer handle. Perhaps reconsider general handle syntax.
        
        if self.workspace_exists(username, userpass, geoserver_url, workspace_name):
            # If it already exists, return silently
            return 'SUCCESS'
        
        # Connect to Geoserver
        gs = geoserver.Geoserver(geoserver_url, username, userpass)                  
        gs.create_workspace(workspace_name, verbose=False)
                    
        # Check that it was indeed created 
        if not self.workspace_exists(username, userpass, geoserver_url, workspace_name):
            msg = 'Workspace %s was not created succesfully on geoserver %s' % (workspace_name, geoserver_url)
            raise Exception(msg)
            
        return 'SUCCESS'    
                    
    def workspace_exists(self, username, userpass, geoserver_url, workspace_name):
        """Check that workspace exists on geoserver
        
        Arguments
            username=username
            userpass=password 
            geoserver_url=The URL of the geoserver   
            workspace=name of geoserver workspace        
            
        Returns
            True or False
        """
        
        # FIXME(Ole): Should this use the handle even though layername would be ignored?
        
        gs = geoserver.Geoserver(geoserver_url, username, userpass)                  
        try:
            gs.get_workspace(workspace_name, verbose=False)
        except:
            return False
        else:
            return True


    
    def calculate(self, hazards, exposures, impact_function_id, impact, bounding_box, comment):
        """Calculate the Impact Geo as a function of Hazards and Exposures
        
        Arguments
            impact_function_id=Id of the impact function to be run 
                               (fully qualified path (from base path))
            hazards = A list of hazard levels .. [H1,H2..HN] each H is a geoserver layer path 
                      where each layer follows the format 
                      username:userpass@geoserver_url:layer_name 
                      (Look at REST for inspiration)
            exposure = A list of exposure levels ..[E1,E2...EN] each E is a 
                       geoserver layer path
            impact = Handle to output impact level layer
            bounding_box = ...
            comment = String with comment for output metadata
        
        Returns
            string: 'SUCCESS' if complete, otherwise Exception is raised

                     
        Note
            hazards and exposure may be lists of handles or just a single handle each.             
        """
        
        # Make sure hazards and exposures are lists
        if type(hazards) != type([]):
            hazards = [hazards]
            
        if type(exposures) != type([]):
            exposures = [exposures]            
        
        # Download data - FIXME(Ole): Currently only raster
        
        hazard_layers = []
        for hazard in hazards:
            raster = self.get_raster_data(hazard, bounding_box)
            H = raster.get_data()
            hazard_layers.append(H)

        exposure_layers = []
        for exposure in exposures:
            raster = self.get_raster_data(exposure, bounding_box)
            E = raster.get_data()
            exposure_layers.append(E)
                        
        # Pass hazard and exposure arrays on to plugin    
        # FIXME, for the time being we just calculate the fatality function assuming only one of each layer.
        
        H = hazard_layers[0]
        E = exposure_layers[0]

        # Calculate impact
        a = 0.97429
        b = 11.037
        F = 10**(a*H-b)*E    
        
        # Upload result (FIXME(Ole): still super hacky and not at all general)
        username, userpass, geoserver_url, layer_name, workspace = self.split_geoserver_layer_handle(impact)
        
        output_file = 'data/%s.asc' % layer_name
        write_coverage_to_ascii(F, output_file, 
                                xllcorner = bounding_box[0],
                                yllcorner = bounding_box[1],
                                cellsize=0.030741064,
                                nodata_value=-9999,
                                # FIXME(Ole): Need to get projection for haz and exp from GeoServer. For now use example.
                                projection=open('data/test_grid.prj').read()) 
                                                
        # And upload it again
        lh = self.create_geoserver_layer_handle(username, 
                                                userpass, 
                                                geoserver_url, 
                                                '',
                                                workspace)

        self.upload_geoserver_layer(output_file, lh)
        
        
        return 'SUCCES'
    
    
    def suggest_impact_func_ids(self, hazards, exposures):
        """Return appropriate impact function ids for the given hazards and exposure
        
        Arguments
            hazards = An array of hazard levels .. [H1,H2..HN] each H is a geoserver layer path
            exposure = An array of exposure levels ..[E1,E2...EN] each E is a geoserver layer path
        
        Returns
            impact_function_ids = array of ids of the impact function that can be run
        """
        return 'ERROR: NO IMPLEMENTATION'

            
    def get_impact_func_details(self, impact_function_id):
        """Return appropriate impact function details for the given hazards and exposure
        
        Arguments
            impact_function_id = id of the impact function
        
        Returns
            a hash containing details of the impact function:
            mandatory fields are: 'Name', 'Description', 'Author'
        """
        return 'ERROR: NO IMPLEMENTATION'
    
    
    def get_all_impact_functions(self):
        """Return a list of all impact functions 
        
        Arguments
            impact_function_id = id of the impact function
        
        Returns
            a hash containing details of the impact function:
            mandatory fields are: 'Name', 'Description', 'Author'
        """
        return 'ERROR: NO IMPLEMENTATION'
    
    
    #----------------------
    # GeoServer Interfacing
    #----------------------    

    def upload_geoserver_layer(self, data, name):
        """Upload (raster or vector) data to the specified geoserver
        
        Arguments
            data = the layer data
            name = the fully qualified geoserver layer name
        
        Returns
            'SUCCESS' if complete, otherwise Exception is raised
        
        """

        # FIXME(Ole): Currently, this will ignore the layername in the handle 
        #             and derive it from the filename
        

        # Unpack and connect
        username, userpass, geoserver_url, layer_name, workspace = self.split_geoserver_layer_handle(name)
        gs = geoserver.Geoserver(geoserver_url, username, userpass)                                  
        
        # Check that workspace exists
        gs.get_workspace(workspace)

        # Upload
        gs.upload_layer(filename=data, workspace=workspace, verbose=False)
        
        return 'SUCCESS'

    
    #FIXME(Ole): Keyword arguments appear to be a no-no in XMLRPC. Is that really the case?
    #def download_geoserver_raster_layer(self, name, bounding_box=None):
    def download_geoserver_raster_layer(self, name, bounding_box, filename):
        """Download raster file from the specified geoserver
        
        Arguments
            name = the fully qualified name of the layer i.e. 'username:password@geoserver_url:shakemap_padang_20090930'
            bounding box = array bounds of the downloaded map e.g [96.956,-5.519,104.641,2.289] 
            #(default None, in which case all data is returned)
            (default []??, in which case all data is returned)
          
            filename: Name of file where layer is stored # FIXME(Ole): Actually no need as default is there
        
        Returns
            FIXME(Ole): What is meant by this return value ?
            layerdata = the layer data as a tif, error string if there are any errors
        
        Note: Exceptions are expected to propagate through XMLRPC 
        """

        if bounding_box == [] or bounding_box == '':
            bounding_box = None
        
        # Unpack and connect
        username, userpass, geoserver_url, layer_name, workspace = self.split_geoserver_layer_handle(name)
        gs = geoserver.Geoserver(geoserver_url, username, userpass)                                  

        # Check that workspace exists
        gs.get_workspace(workspace)
        
        # Download
        gs.download_coverage(layer_name, 
                             bounding_box, 
                             output_filename=filename, 
                             workspace=workspace, 
                             format='GeoTIFF',
                             verbose=False)
        
        return 'SUCCESS'

        
        
    def get_raster_data(self, name, bounding_box):
        """Get raster data from the specified geoserver as a numeric array
        
        Arguments
            name = the fully qualified name of the layer i.e. 'username:password@geoserver_url:shakemap_padang_20090930'
            bounding box = array bounds of the downloaded map e.g [96.956,-5.519,104.641,2.289] 
            #(default None, in which case all data is returned)
            (default []??, in which case all data is returned)
        
        Returns
            layerdata = the layer data as a numeric array
        
        Note: Exceptions are expected to propagate through XMLRPC 
        """

        if bounding_box == [] or bounding_box == '':
            bounding_box = None

        # Unpack and connect
        username, userpass, geoserver_url, layer_name, workspace = self.split_geoserver_layer_handle(name)
        gs = geoserver.Geoserver(geoserver_url, username, userpass)                                  
        
        # Check that workspace exists
        gs.get_workspace(workspace)

        # Get raster data
        raster = gs.get_raster_data(layer_name, 
                                    bounding_box, 
                                    workspace, 
                                    verbose=False)

        return raster
        
            
    
    def download_geoserver_vector_layer(self):
        """Download data to the specified geoserver
        
        Note - can this be wrapped up with the raster version? 
        """
        
        return 'ERROR: NO IMPLEMENTATION'
        
        
        
    def delete_layer(self, name):
        """Delete layer on the specified geoserver

        """
        
        # Unpack and connect
        username, userpass, geoserver_url, layer_name, workspace = self.split_geoserver_layer_handle(name)
        gs = geoserver.Geoserver(geoserver_url, username, userpass)                                  
        
        # Delete layer
        gs.delete_layer(layer_name, verbose=False)

        # Delete style
        #gs.delete_style(layer_name, verbose=False)        
        
        return 'SUCCESS'        
    
