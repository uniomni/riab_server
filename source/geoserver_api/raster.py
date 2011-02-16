"""This module provides functionality to convert between ESRI ASCII files and Python using numpy
"""

import os 
import numpy

from osgeo import gdal


# FIXME (Ole): Gdal rounds everything to single precision. Wrote to the mailing list with a test example 6th August 2010  
# There are also large errors in extrema computed by ComputeRasterMinMax(). This has not been reported.
# See also TRAC pages: http://www.aifdr.org/projects/riat    


class Raster:
    """Internal representation of raster (coverage) data
    """
    
    def __init__(self, filename):

        # Open data file for reading
        # File must be kept open, otherwise GDAL methods segfault.
        fid = self.fid = gdal.Open(filename, gdal.GA_ReadOnly)
        if fid is None:
            msg = 'Could not open file %s' % filename            
            raise Exception(msg)            

        # Record raster metadata from file
        basename, ext = os.path.splitext(filename)
        coveragename = os.path.split(basename)[-1] # Aways use basename without leading directories as name
    
        self.filename = filename
        self.name = coveragename

        self.columns = fid.RasterXSize
        self.rows = fid.RasterYSize
        self.number_of_bands = fid.RasterCount

        
        # Assume that file contains all data in one band        
        msg = 'Only one raster band currently allowed'
        if self.number_of_bands > 1:
            print 'WARNING: Number of bands in %s are %i. Only the first band will currently be used.' % (filename, self.number_of_bands)
        
        # Get first band. 
        band = self.band = fid.GetRasterBand(1)
        if band is None:
            msg = 'Could not read raster band from %s' % filename    
            raise Exception(msg)


        
    def get_data(self, nan=False):
        """Get raster data as numeric array
        If keyword nan is True, nodata values will be replaced with NaN
        """
        
        A = self.band.ReadAsArray()
            
        M, N = A.shape
        msg = 'Dimensions of raster array do not match those of raster file %s' % self.filename
        assert M == self.rows, msg
        assert N == self.columns, msg        
        
        if nan:
            # Replace NODATA_VALUE with NaN            
            nodata = self.get_nodata_value()        
            
            NaN = numpy.zeros(A.shape, A.dtype)*numpy.nan
            A = numpy.where(A == nodata, NaN, A)
         
        return A
            
        
    def get_projection(self):
        return self.fid.GetProjection()
        
    def get_geotransform(self):
        return self.fid.GetGeoTransform()

    def __mul__(self, other):
        return self.data * other.data
        
    def __add__(self, other):
        return self.data + other.data        

    def get_extrema(self, use_numeric=False):
        """Get min and max from raster
        
        Return min, max
        """

        if use_numeric:
            # This seems to be much more accurate than GDAL
            A = self.get_data(nan=True)
            min = numpy.nanmin(A.flat[:])
            max = numpy.nanmax(A.flat[:])            
        else:    
            min, max = self.band.ComputeRasterMinMax(1)        
            
        return min, max

    def get_nodata_value(self):
        """Get the internal representation of NODATA
        """
        
        nodata = self.band.GetNoDataValue()
        if nodata is None:
            min, max = self.get_extrema()
            nodata = min            
        
        return nodata
        
        
    def get_bins(self, N=10, quantiles=False):
        """Get N values between the min and the max occurred in this dataset.
        
        Return sorted list of length N+1 where the first element is min and the last is max.
        Intermediate values depend on the keyword quantiles:
        If quantiles is True (the default) the values represent boundaries between quantiles. 
        If quantiles is False, the values represent equidistant interval boundaries.
        """
        
        
        # FIXME (Ole): GDAL gives wrong min/max values. 
        # The flag use_numeric will use the real values, but I have left things as the are
        # for the moment.
        min, max = self.get_extrema() #use_numeric=True)

        levels = []
        if quantiles is False:
            # Linear intervals
            d = (max - min)/N
            
            for i in range(N):
                levels.append(min+i*d)
        else:
            # Quantiles
            # FIXME (Ole): Not 100% sure about this algorithm, but it is close enough
            
            
            A = self.get_data(nan=True).flat[:]
            
            mask = numpy.logical_not(numpy.isnan(A)) # Omit NaN's
            A = A.compress(mask)
            
            A.sort()
            
            assert len(A) == A.shape[0]
            
            d = float(len(A) + 0.5)/N
            for i in range(N):
                levels.append(A[int(i*d)])

        levels.append(max)

            
        return levels    
         

# FIXME: Here's how to get metadata out
# See http://www.gdal.org/gdal_tutorial.html

#So gdal stores all the geospatial info in an array called geotransform.
#It contains everything you need to go from pixel space to coordinate space.
#This is how you would normally use it:
#
#dataset = gdal.Open(filename, gdal.GA_ReadOnly) geotransform = dataset.GetGeoTransform()
#
## origin - top left
#x_origin    = geotransform[0] # top left x
#y_origin    = geotransform[3] # top left y
#
## cell size
#x_res       = geotransform[1] # w-e pixel resolution
#y_res       = geotransform[5] # n-s pixel resolution
#
## width and height of the image in number of pixels
#x_pix       = dataset.RasterXSize
#y_pix       = dataset.RasterYSize
#
## Corners (lower-left/top-right)
#minx = x_origin
#miny = y_origin + (y_pix * y_res) # x_res -ve maxx = x_origin + (x_pix * x_res) maxy = y_origin
#
## rotation information but in our case this should be 0 # geotransform[4]  # rotation, 0 if image is "north up"
## geotransform[2]  # rotation, 0 if image is "north up"
#
#
#    print 'Driver: ', dataset.GetDriver().ShortName,'/', \
#          dataset.GetDriver().LongName
#    print 'Size is ',dataset.RasterXSize,'x',dataset.RasterYSize, \
#          'x',dataset.RasterCount
#    print 'Projection is ',dataset.GetProjection()
#    
#    geotransform = dataset.GetGeoTransform()
#    if not geotransform is None:
#        print 'Origin = (',geotransform[0], ',',geotransform[3],')'
#        print 'Pixel Size = (',geotransform[1], ',',geotransform[5],')'
#
#
#
#band = dataset.GetRasterBand(1)
#
#        print 'Band Type=',gdal.GetDataTypeName(band.DataType)#
#
#        min = band.GetMinimum()
#        max = band.GetMaximum()
#        if min is None or max is None:
#            (min,max) = band.ComputeRasterMinMax(1)
#        print 'Min=%.3f, Max=%.3f' % (min,max)
#
#        if band.GetOverviewCount() > 0:
#            print 'Band has ', band.GetOverviewCount(), ' overviews.'
#
#        if not band.GetRasterColorTable() is None:
#            print 'Band has a color table with ', \
#            band.GetRasterColorTable().GetCount(), ' entries.'


        
            
def read_coverage(filename, verbose=False):
    """Read coverage from file and return Coverage object
    All gdal formats are supported.
    """

    return Raster(filename)
                  

def write_coverage_to_geotiff(A, filename, projection, geotransform):
    """Convert coverage into geotiff file with specified metadata and one data layer
    """
    
    format = 'GTiff'
    driver = gdal.GetDriverByName(format)
    
    N, M = A.shape # Dimensions. Note numpy and Gdal swap order
    
    # Create empty file
    fid = driver.Create(filename, M, N, 1, gdal.GDT_Float64)
    
    # Write metada
    fid.SetProjection(projection)
    fid.SetGeoTransform(geotransform)
    
    # Write data
    fid.GetRasterBand(1).WriteArray(A)
    
    
# FIXME (Ole) Hack to get demo going    
# Use default projection file.
# DELETE THIS VERY SOON!
def XXwrite_coverage_to_ascii(A, filename, xllcorner, yllcorner,
                            cellsize=0.0083333333333333,
                            nodata_value=-9999,
                            projection='GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]]'):

    """Complete hack - need to use GDAL....
    """
    
    
    nrows, ncols = A.shape
    
    
    fid = open(filename, 'w')
    fid.write('ncols         %i\n' % ncols)
    fid.write('nrows         %i\n' % nrows)
    fid.write('xllcorner     %.12f\n' % xllcorner)    
    fid.write('yllcorner     %.12f\n' % yllcorner)        
    fid.write('cellsize      %.12f\n' % cellsize)
    fid.write('NODATA_value  %i\n' % nodata_value)
    for i in range(nrows):
        for j in range(ncols):
            val = A[i,j]
            if numpy.isnan(val):
                fid.write('%i ' % nodata_value)
            else:    
                fid.write('%.12f ' % val)
        fid.write('\n')
    fid.close()
            
    basename, _ = os.path.splitext(filename)    
    fid = open(basename + '.prj', 'w')
    fid.write(projection)
    fid.close()
    
    
      
# Code based directly on ASCII files - used for testing of GDAL floating point precision   
    
class Raster_asc:
    """Internal representation of raster (coverage) data
    """
    
    def __init__(self, name, xllcorner, yllcorner, cellsize, data, nodata_value=-9999):
        self.name = name
        self.xllcorner = xllcorner
        self.yllcorner = yllcorner
        self.cellsize = cellsize
        self.data = data
    
                
def read_coverage_asc(ascfilename, verbose=False):
    """Read coverage from ESRI ASCII file and return Coverage object
    """

    basename, ext = os.path.splitext(ascfilename)
    
    coveragename = os.path.split(basename)[-1] # Aways use basename without leading directories as name
    
    if ext != '.asc':
        msg = 'Coverage %s must be in ASCII format with extension .asc' % ascfilename    
        raise IOError(msg)

    # FIXME (Ole): Also read .prj file as WKT - see AIM project
    

    # Read coverage data
    if verbose: print('Reading coverage from %s' % ascfilename)
    
    datafile = open(ascfilename)
    lines = datafile.readlines()
    datafile.close()

    
    # Check first header and get number of columns
    fields = lines[0].strip().split()
        
    msg = 'Input file %s does not look like an ASCII grd file. It must start with ncols' % ascfilename
    assert fields[0] == 'ncols', msg
    assert len(fields) == 2
    ncols = int(fields[1])

    # Get number of rows
    fields = lines[1].strip().split()    
    nrows = int(fields[1])       

    # Get cellsize
    msg = 'ASCII file does not look right. Check file %s, Traceback and source code %s.' % (ascfilename, __file__)
    assert lines[4].startswith('cellsize'), msg
    fields = lines[4].split()
    cellsize = float(fields[1])        
        
    # Get origin taking care of grid vs pixel registration offset
    assert lines[2].startswith('xllcorner'), msg
    fields = lines[2].split()
    xllcorner = float(fields[1]) + cellsize/2
    
    assert lines[3].startswith('yllcorner'), msg
    fields = lines[3].split()
    yllcorner = float(fields[1]) + cellsize/2    

    # Get NODATA value
    assert lines[5].startswith('NODATA'), msg    
    fields = lines[5].split()
    nodata_value = float(fields[1])
        
    # Get data
    data = numpy.zeros((nrows, ncols))
    data_lines = lines[6:]
                          
    N = len(data_lines) 
    for i, line in enumerate(data_lines):
        fields = line.split()
        if verbose and i % ((N+10)/10) == 0:
            print('Processing row %d of %d' % (i, nrows))
           
        if len(fields) != ncols:
            msg = 'Wrong number of columns in file "%s" line %d\n' % (ascfilename, i)
            msg += 'I got %d elements, but there should have been %d\n' % (len(fields), ncols)
            raise Exception, msg

        data[i, :] = numpy.array([float(x) for x in fields])


    # Create Raster object and return
    return Raster_asc(coveragename, xllcorner, yllcorner, cellsize, data, nodata_value=nodata_value)    
