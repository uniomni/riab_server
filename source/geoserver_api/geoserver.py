"""This is a Python interface to the Geoserver REST API
"""

import os
from utilities import get_web_page, run, curl, get_pathname_from_package
import numpy
import coverage
import raster
import sld_template
import osgeo.gdal
import pycurl
import StringIO
import json
import re

class Geoserver:
    """Connection to one instance of a geoserver  
    """
    
    def __init__(self, geoserver_url, geoserver_username, geoserver_userpass):
        """Instantiate class and verify connection to specified geoserver through the REST API.
        """
        
        # Record login information
        self.geoserver_url = geoserver_url
        self.geoserver_username = geoserver_username
        self.geoserver_userpass = geoserver_userpass
        
        # Verify that Geoserver is running
        found = False
        page = get_web_page(os.path.join(geoserver_url, 'rest'), 
                            username=geoserver_username, 
                            password=geoserver_userpass)
        for line in page:
            if line.find('workspaces') > 0:
                found = True

        msg = 'Could not connect to geoserver at %s' % geoserver_url        
        assert found, msg
        
        
    # Methods for manipulating the geoserver (e.g. add and delete workspaces)
    def create_workspace(self, name, verbose=False):
        """Create new workspace on the geoserver

        Generate and execute curl commands of the form
        curl -u admin:geoserver -v -X POST -H "Content-type: text/xml" \
         "http://localhost:8080/geoserver/rest/workspaces" --data-ascii \
         "<workspace><name>aifdr</name></workspace>"
        """

        try:
            curl(self.geoserver_url, 
                 self.geoserver_username, 
                 self.geoserver_userpass, 
                 'POST', 
                 'text/xml', 
                 'workspaces', 
                 '--data-ascii', 
                 '<workspace><name>%s</name></workspace>' % name, 
                 verbose=verbose)
        except Exception, e:
            
            if str(e).find('already exists') > 0:
                # Workspace already exists, no worries
                pass
            else:
                # Reraise
                msg = 'Could not create workspace %s: %s' % (name, e)
                raise Exception(msg)
             
        
        # Record this workspace as default FIXME - obsolete?
        self.workspace = name
        
        
    def get_workspace(self, name, verbose=False):
        """Get workspace info from the geoserver
        """

        # FIXME(Ole): Unfortunate name as it doesn't return anything
        
        out = curl(self.geoserver_url, 
                   self.geoserver_username, 
                   self.geoserver_userpass, 
                   'GET', 
                   'text/xml', 
                   'workspaces/%s' % name, 
                   '', 
                   '', 
                   verbose=verbose)

        succes = False
        for line in out:
            if line.startswith('Workspace'):
                if line.split()[1][1:-1] == name:                
                    succes = True
                    break

        if not succes:        
            msg = 'Could not find workspace %s in geoserver %s' % (name, self.geoserver_url)
            raise Exception(msg)



    # Methods for up and downloading layers as files
    def download_coverage(self, 
                          coverage_name, 
                          bounding_box=None, 
                          output_filename=None, 
                          workspace=None, 
                          format='GeoTIFF',
                          verbose=False):
        """Retrieve named raster layer as file.
        
        The specified format relates to what the Geoserver is asked to produce. So far it should be GeoTIFF.
        This file will then be converted to an ASCII file and the name returned.
        
        """

        # Input checks (Shoaib) no need to check since the coverage.py checks this against the WCS server 
        supported_formats = ['GIF', 'PNG', 'JPEG', 'TIFF', 'GeoTIFF', 'ArcGrid', 'ImageMosaic', 'Gtopo30']
        msg = 'Requested format %s is not support. Supported formats are %s' % (format, supported_formats)
        assert format.lower() in [fmt.lower() for fmt in supported_formats], msg
        
        if workspace is None:
            raise Exception('Default workspace not yet implemented')
        
        if bounding_box is None:
            bounding_box = [] # FIXME (Ole): Not sure about default value
            
        if output_filename is None:
            output_filename = coverage_name + '.tif'
            
        if verbose:
            print 'Downloading coverage %s to %s' % (coverage_name, output_filename)        
            
        # Get coverage    
        wcs_url = os.path.join(self.geoserver_url, 'wcs')
        layer_name = '%s:%s' % (workspace, coverage_name)

        try:
            c = coverage.Coverage(wcs_url, layer_name)
        except KeyError, e:
            msg = 'Could not download layer %s from %s' % (layer_name, wcs_url)
            raise KeyError(msg)
            
        c.download(format=format, bounding_box=bounding_box, outputfile=output_filename)

        # Convert downloaded data to ASCII (without FORCE_CELLSIZE we get a warning suggesting this option)
        basename, _ = os.path.splitext(output_filename)
        ascii_filename = basename + '.asc'   
        cmd = 'gdal_translate -ot Float64 -of AAIGrid -co "FORCE_CELLSIZE=TRUE" -a_nodata -9999 %s %s' % (output_filename, ascii_filename)
        
        if verbose:
            run(cmd, verbose=verbose)
        else:
            run(cmd, stdout='/dev/null', stderr='/dev/null', verbose=verbose)
        
        return ascii_filename
        
        
    def download_vector_layer(self, name):
        """Retrieve named vector layer as file
        """
        
        pass
        
        
    def upload_layer(self, filename, workspace, verbose=False):
        """Upload coverage (raste) or vector data to geoserver.
        
        Files with extensions asc, txt or tif will be treated as raster data where as the 
        extension shp will be taken to mean vector data.
        
        See docstrings for upload_coverage(0 and upload_vector_data() for more details.
        """
        
        # FIXME: We should let GDAL take care of filetypes.
        
        _, extension = os.path.splitext(filename)        
        
        if extension in ['.asc', '.txt', '.tif']:
            return self.upload_coverage(filename, workspace, verbose)
        elif extension in ['.zip', '.shp']:
            return self.upload_vector_layer(filename, workspace, verbose)        
        else:
            msg = 'Unknown extention for spatial data: %s' % extension
            raise Exception(msg)
            
        
    def upload_coverage(self, filename, workspace, verbose=False):
        """Upload raster file to named layer
        Valid file types are
        
        ASCII with appropriate projection file: *.asc (*.txt) & *.prj
        GEOTIFF file: *.tif 

        If style file (sld) is present it will be used.
        Otherwise an autogenerated sld will be made for ASCII rasters. 
                     Geotiffs will rely on their native styling.  (FIXME: Rethink semantics of all this)
        
        
        Uploads are done using curl commands of the form
        curl -u admin:geoserver -v -X PUT -H "Content-type: image/tif" "http://localhost:8080/geoserver/rest/workspaces/futnuh/coveragestores/population_padang_1/file.geotiff" --data-binary "@data/population_padang_1.tif
        """
        
        # Form derived variables
        pathname, extension = os.path.splitext(filename)
        layername = os.path.split(pathname)[-1]
        
        msg = 'Coverage must have extension asc, txt or tif'
        assert extension in ['.asc', '.txt', '.tif'], msg

        # Check to see if the dataset has a coordinate system
        # FIXME: Do this for vector layers also
        dataset = osgeo.gdal.Open(filename, osgeo.gdal.GA_ReadOnly)
        msg = filename+' had no Coordinate/Spatial Reference System (CRS)'
        assert dataset.GetProjectionRef().startswith('GEOGCS'), msg

        # Style file in case it accompanies the file        
        provided_style_filename = pathname + '.sld'
        
        # Locally stored                
        upload_filename = layername + '.tif'             
        style_filename = layername + '.sld'         

        
        if extension == '.tif':
            generate_sld = False
                    
            cmd = 'cp %s %s' % (filename, os.getcwd()) # upload_filename)
            run(cmd, verbose=False)            
        else:
            # Convert to Geotiff
            generate_sld = True            
            cmd = 'gdal_translate -ot Float64 -of GTiff -co "PROFILE=GEOTIFF" %s %s' % (filename, 
                                                                                        upload_filename)
            if verbose:
                run(cmd, verbose=verbose)
            else:
                run(cmd, stdout='upload_raster.stdout', stderr='upload_raster.stderr', verbose=verbose)        
        
        # Upload raster data to Geoserver
        curl(self.geoserver_url, 
             self.geoserver_username, 
             self.geoserver_userpass, 
             'PUT', 
             'image/tif', 
             'workspaces/%s/coveragestores/%s/file.geotiff' % (workspace, layername), 
             '--data-binary', 
             '@%s' % upload_filename, 
             verbose=verbose)


        # Take care of styling 
        if os.path.isfile(provided_style_filename):
            # Use provided style file

            # Copy provide file to local directory because the REST interface
            # spits the dummy with pathnames.
            cmd = 'cp %s %s' % (provided_style_filename, os.getcwd())
            run(cmd, verbose=False)    
        else:        
            # Automatically create new style file for raster file
            
            self.create_raster_sld(upload_filename, quantiles=False, verbose=verbose)
 
            
        if generate_sld:
            # Upload style file to Geoserver    
            self.upload_style(layername, style_filename, verbose=verbose)            
            
            # Make it the default for this layer
            self.set_default_style(layername, layername, verbose=verbose)

        return '%s:%s' % (workspace, layername)
        
        

    def upload_vector_layer(self, filename, workspace, verbose=False):
        """Upload vector file to named layer
        Valid file types are
        
        Zipped shapefile with extension *.zip
        Or it can be the name of the main shapefiel (*.shp) in which case it will be zipped up
        before upload.
                
        Uploads are done using curl commands of the form
        curl -u admin:geoserver -v -X PUT -H "Content-type: application/zip" "http://localhost:8080/geoserver/rest/workspaces/futnuh/datastores/volcanoes/file.shp" --data-binary @volcanoes.zip
        """
        
        subdir = os.path.split(filename)[0]
        local_filename = os.path.split(filename)[1]
        
        layername, extension = os.path.splitext(local_filename)
        upload_filename = layername + '.zip'             
        style_filename = layername + '.sld'         # Locally stored
        provided_style_filename = os.path.join(subdir, style_filename) # In case it accompanies the file
        
        
        msg = 'Vector data must have extension zip or shp'
        assert extension in ['.zip', '.shp'], msg
        
        if extension == '.shp':
            projection_filename = os.path.join(subdir,  layername) + '.prj'                     
            try:
                fid = open(projection_filename)
            except:
                msg = 'Could not open projection file %s' % projection_filename
                raise Exception(msg)
            else:
                fid.close()
        
            # Zip shapefile and auxiliary files 
            cmd = 'cd %s; zip %s %s*' % (subdir, upload_filename, layername)
            run(cmd, stdout='zip.stdout', stderr='zip.stderr', verbose=verbose)
            
            # Move to cwd
            # FIXME (Ole): For some reason geoserver won't accept the zip file unless
            # located in CWD.       
            # FIXME (Ole): If zip file already exists with different owner, this
            # will silently wait for a newline. Annoying.     
            cmd = 'mv %s/%s .' % (subdir, upload_filename)
            run(cmd, stdout='mvzip.stdout', stderr='mvzip.stderr', verbose=verbose)            
        else:
            # Already zipped - FIXME: Need to test if it is indeed a zipped shape file
            pass
        
        
        # Upload vectore data to Geoserver        
        curl(self.geoserver_url, 
             self.geoserver_username, 
             self.geoserver_userpass, 
             'PUT', 
             'application/zip', 
             'workspaces/%s/datastores/%s/file.shp' % (workspace, layername), 
             '--data-binary', 
             '@%s' % upload_filename, 
             verbose=verbose)
             
             
        # Take care of styling 
        if os.path.isfile(provided_style_filename):
            # Use provided style file
                
            # Copy provide file to local directory because the REST interface
            # spits the dummy with pathnames.
            cmd = 'cp %s %s' % (provided_style_filename, os.getcwd())
            run(cmd, verbose=False)    
        else:        
            # Automatically create new style file for vector file (FIXME: Not yet implemented)
            #self.create_vector_sld(upload_filename)
            return '%s:%s' % (workspace, layername)        
                        
 
        # Upload style file to Geoserver    
        self.upload_style(layername, style_filename, verbose=verbose)            
            
        # Make it the default for this layer
        self.set_default_style(layername, layername, verbose=verbose)
             
        
        return '%s:%s' % (workspace, layername)        
                
        
        
    # Methods for up and downloading layers directly into Python structures
    def get_raster_data(self, 
                        coverage_name,
                        bounding_box=None, 
                        workspace=None, 
                        verbose=False):

        """Retrieve named coverage layer as Python numpy struture
        """

        # Download coverage into ASCII file
        ascii_filename = self.download_coverage(coverage_name, 
                                                bounding_box=bounding_box, 
                                                workspace=workspace, 
                                                format='GeoTIFF',
                                                verbose=verbose)

        # Read resulting ASCII file into internal numerical structure and return
        return raster.read_coverage(ascii_filename)
        
        # FIXME (Ole): Include georef, projection info etc in return
                
        

        
        
    def get_vector_data(self, name):
        """Retrieve named vector layer in some kind of Python numeric structure
        """
        
        pass
        
        
    def store_raster_data(self, name):
        """
        """
        
        pass

        
        
    def store_vector_data(self, name):
        """
        """
        
        pass        
        

    def find_style(self, name):
        """Does the style exist"""
        c = pycurl.Curl()
        url = ((self.geoserver_url+"/rest/styles/%s") % name)
        c.setopt(pycurl.URL, url)
        c.setopt(pycurl.HTTPHEADER, ["Accept: text/json"])
        c.setopt(pycurl.USERPWD, "%s:%s" % (self.geoserver_username, self.geoserver_userpass))
        c.setopt(pycurl.VERBOSE, 0)
        b = StringIO.StringIO()
        c.setopt(pycurl.WRITEFUNCTION, b.write)
        c.perform()
        m = re.match("No such style: ", b.getvalue())
        if m: return None
        d = json.loads(b.getvalue())
        return d


    def find_coverage(self, name):
        """Given a name of a coverage returns the coverage object
        the coverage name can be given by itself or with the workspace
        name prepended followed by a colon e.g. test_workspace:coverage_name
        """
        
        n = name
        
        # Determine if workspace is given:
        workspace_give = False
        if len(n.split(':')) == 2:
            workspace_give = True
        if workspace_give:
            workspace, coveragename = n.split(':')
            # url = ((self.geoserver_url+"rest/workspaces/%s/coveragestores/%s") % (workspace, coveragename))
            try:
                c = coverage.Coverage(self.geoserver_url+'/wcs', n)
                return c
            except:
                return None
        else:
            # TODO : add the case where no workspace is given
            return None
            

    def create_raster_sld(self, filename, quantiles=False, verbose=False):
        """given a raster file and a predefined SLD template it should find the min,max,nodata values
        for the dataset and create a custom style with a color map using the predefined template sld
        which is located in module sld_template.py
        
        If quantiles is True, 10 quantiles will be used for colour coding. Othewise 10 equidistant intervals will be used.
        """

        pathname, extension = os.path.splitext(filename)
        layername = os.path.basename(pathname)
        
        R = raster.read_coverage(filename)
        levels = R.get_bins(N=10, quantiles=quantiles)
        nodata = R.get_nodata_value()         


        #if verbose:
        #    print 'Styling %s' %layername        
        #    print 'Levels', levels
        #    print 'NoData', nodata    
        
        # Write the SLD file    
        sld = layername+'.sld'
        text = sld_template.sld_template

        text = text.replace('MIN',str(levels[0]))
        text = text.replace('MAX',str(levels[-1]))
        text = text.replace('TEN',str(levels[1]))
        text = text.replace('TWENTY',str(levels[2]))
        text = text.replace('THIRTY',str(levels[3]))
        text = text.replace('FOURTY',str(levels[4]))
        text = text.replace('FIFTY',str(levels[5]))
        text = text.replace('SIXTY',str(levels[6]))
        text = text.replace('SEVENTY',str(levels[7]))
        text = text.replace('EIGHTY',str(levels[8]))
        text = text.replace('NINETY',str(levels[9]))


        # Getting round an sld parsing bug in geoserver
        if nodata >= max:
            text = text.replace('<!--Higher-->', '<ColorMapEntry color="#ffffff" quantity="NODATA" opacity="0"/>')
        else:   
            text = text.replace('<!--Lower-->', '<ColorMapEntry color="#ffffff" quantity="NODATA" opacity="0"/>')
            
        text = text.replace('NODATA', str(nodata))
        fout = open(sld, 'w')
        fout.write(text)
        fout.close()
    
    def upload_style(self, style_name, style_file, verbose=False):
        """Upload style file to geoserver
        """     
           
        # curl -u geoserver -XPOST -H 'Content-type: text/xml' -d 
        # '<style><name>sld_for_Pk50095_geotif_style</name><filename>Pk50095.sld</filename></style>' 
        # localhost:8080/geoserver/rest/styles/ 
        try:
            curl(self.geoserver_url, 
                 self.geoserver_username, 
                 self.geoserver_userpass, 
                 'POST', 
                 'text/xml', 
                 'styles', 
                 '--data-ascii', 
                 '<style><name>%s</name><filename>%s</filename></style>' % (style_name, style_file),  
                 verbose=verbose)
        except Exception, e:
            
            if str(e).find('already exists') > 0:
                # Style already exists, no worries
                pass
            else:
                # Reraise
                msg = 'Could not create style %s: %s' % (style_name, e)
                raise Exception(msg)
                

        # curl -u geoserver -XPUT -H 'Content-type: application/vnd.ogc.sld+xml' -d @sld_for_Pk50095_geotif.sld
        # localhost:8080/geoserver/rest/styles/sld_for_Pk50095_geotif_style
        curl(self.geoserver_url, 
            self.geoserver_username, 
            self.geoserver_userpass, 
            'PUT', 
            'application/vnd.ogc.sld+xml', 
            'styles/%s' % (style_name), 
            '--data-binary', 
            '@%s' % style_file, 
            verbose=verbose)


        
    def set_default_style(self, style_name, layer_name, verbose=False):
        """Set given style as default for specified layer"""
        
        curl(self.geoserver_url, 
            self.geoserver_username, 
            self.geoserver_userpass, 
            'PUT', 
            'text/xml', 
            'layers/%s' % (layer_name), 
            '--data-ascii', 
            '<layer><defaultStyle><name>%s</name></defaultStyle><enabled>true</enabled></layer>' % style_name,
            verbose=verbose)
        
        # curl -u admin:geoserver -XPUT -H 'Content-type: text/xml' -d 
        # '<layer><defaultStyle><name>Pk50095_geotif_style</name></defaultStyle><enabled>true</enabled></layer>' 
        # localhost:8080/geoserver/rest/layers/Pk50095_geotif

        
    def delete_style(self, style_name, verbose=False):
        """docstring for delete_style"""
        
        # TODO: add test
        run('curl -u %s:%s -d "purge=true" -X DELETE localhost:8080/geoserver/rest/styles/%s' % (self.geoserver_username, 
                                                                                                 self.geoserver_userpass, 
                                                                                                 style_name))            
    def delete_layer(self, layer_name, workspace, verbose=False):
        """Delete layer on server
        
        This is done through REST in three steps with commands like this:
        
        curl -u admin:geoserver -v -X DELETE "http://localhost:8080/geoserver/rest/layers/shakemap_padang_20090930"
        curl -u admin:geoserver -v -X DELETE "http://localhost:8080/geoserver/rest/workspaces/hazard/coveragestores/shakemap_padang_20090930/coverages/shakemap_padang_20090930"
        curl -u admin:geoserver -v -X DELETE "http://localhost:8080/geoserver/rest/workspaces/hazard/coveragestores/shakemap_padang_20090930"
        
        
        In newer versions of GeoServer it can done like this:
        curl -u admin:geoserver -v -X DELETE "http://localhost:8080/geoserver/rest/workspaces/hazard/coveragestores/shakemap_padang_20090930?recurse=true"        
        """
        
        if not layer_name:
            msg = 'Valid layer name was not provided for deletion. I got "%s"' % str(layer_name)
            raise Exception(msg)
            
        
        # Delete layer
        curl(self.geoserver_url, 
             self.geoserver_username, 
             self.geoserver_userpass, 
             'DELETE', 
             '', 
             'layers/%s' % layer_name, 
             '', 
             '',
             verbose=verbose)        
             
             
        # Delete associated coverages
        curl(self.geoserver_url, 
             self.geoserver_username, 
             self.geoserver_userpass, 
             'DELETE', 
             '', 
             'workspaces/%s/coveragestores/%s/coverages/%s' % (workspace, layer_name, layer_name),
             '', 
             '',
             verbose=verbose)                     
             
        # Delete associated coverage store
        curl(self.geoserver_url, 
             self.geoserver_username, 
             self.geoserver_userpass, 
             'DELETE', 
             '', 
             'workspaces/%s/coveragestores/%s' % (workspace, layer_name),
             '', 
             '',
             verbose=verbose)                                  
             
             

        
