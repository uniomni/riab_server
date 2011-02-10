"""Low level interface to download of coverage (raster) from Geoserver

Shoaib Burq 2010
"""

# FIXME (Ole): This needs some rethinking and testing.


import pycurl
import numpy
from osgeo import osr, gdal
import sys

class Coverage:
  
  def __setattr__(self, name, val):
    self.__dict__[name] = val
  
  def __init__(self, base_url, layername ):
    """Given a URL of a WCS server and a layername it will instatiate an object for downloading data for that layer"""
    
    # print layername
    self.service = 'wcs'
    self.base_url = base_url
    self.layername = layername
    self.version = '1.0.0'
    self.request = 'getcoverage'
    self.workspace = None
    
    # ------------------------------------------------------------------------------------------------------------
    # Grab as much metadata as possible from DescribeCoverage and setup the coverage object with sensible defaults
    # ------------------------------------------------------------------------------------------------------------
    from owslib.wcs import WebCoverageService

    wcs = WebCoverageService(base_url, version='1.0.0') # Raises a deprecation waring
    if len(self.layername.split(':')) == 2:
      self.workspace, self.layername = layername.split(':')
    # try:
    #     print wcs.contents[layername]
    # except:
    #     print wcs.contents[self.layername]
    # FIXME: Temporary construction until OWS Lib is OK 
    try:
      metadata = wcs.contents[self.layername]
    except:  
      metadata = wcs.contents[layername]    

    #print metadata.supportedCRS
    #print metadata.supportedFormats
    
    self.bbox     = metadata.boundingBoxWGS84 # FIXME (Ole): Is this a default bbox and if so can it be used as such?
    try:
        self.crs  = metadata.supportedCRS[0]    # FIXME (Ole): supportedCRS may be an empty list 
    except(IndexError):                         # FIXME (shoaib): not sure why this would be empty,
        self.crs  = "EPSG:4326"                 # all data we are dealing with should have a CRS
        
    self.format   = metadata.supportedFormats[0]
    self.formats  = metadata.supportedFormats
    self.resx     = metadata.grid.offsetvectors[0][0]
    #FIXME (shoaib) not sure why it was working earlier without the abs
    self.resy     = abs(float(metadata.grid.offsetvectors[1][1])) # -ve since the grid origin is top-left 
    self.coverage = self.layername
    
    # some WCS version 1.1.1 - params for later 
    self.identifier = self.layername                                        
    self.crs_urn = 'urn:ogc:def:crs:EPSG::4326'
    self.store = 'false'

  
  def get_url(self):
    self.__url= self.base_url+'?version='+self.version \
    +'&service='+self.service \
    +'&request='+self.request \
    +'&identifier='+self.identifier \
    +'&format='+self.format \
    +'&BoundingBox=%f,%f,%f,%f,%s' % (self.bbox[1], self.bbox[0], self.bbox[3], self.bbox[2], self.crs_urn) \
    +'&store='+self.store \
    +'&coverage='+self.coverage \
    +'&crs='+self.crs \
    +'&bbox=%f,%f,%f,%f' % tuple(self.bbox) \
    +'&resx='+str(self.resx) \
    +'&resy='+str(self.resy)
            
    return self.__url
    
  def download(self, format='GeoTiff', bounding_box=[-1.0,96.0,4.0,100.0], outputfile='test.tif'):
    """given an outputformat and a bounding_box in WGS84 [minx,miny,maxx,maxy] returns the layer"""
    
    # Check if format is supported
    msg = 'Requested format %s is not supported. Supported formats are %s' % (format, self.formats)
    assert format.lower() in [fmt.lower() for fmt in self.formats], msg
    
    self.format = format
    self.bbox=bounding_box

          
    c = pycurl.Curl()
    f = open(outputfile, 'w+')
    c.setopt(pycurl.URL, self.get_url())
    c.setopt(pycurl.WRITEFUNCTION, f.write)
    
    #print pycurl.URL, self.get_url()
    #print pycurl.WRITEFUNCTION
    
    c.perform()
