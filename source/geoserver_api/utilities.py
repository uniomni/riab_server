"""General utilities for testing
"""

import os
import urllib, urllib2, osgeo
from subprocess import Popen, PIPE	


def run(cmd, 
        stdout=None,
        stderr=None, 
        verbose=True):
    """Run command with or without echoing
    Possible redirect stdout and stderr
    """
    
    if verbose:
        print cmd
    
        
    s = cmd    
    if stdout:
        s += ' > %s' % stdout
        
    if stderr:
        s += ' 2> %s' % stderr        
        
    err = os.system(s)
    
    if err != 0:
        msg = 'Command "%s" failed with errorcode %i. ' % (cmd, err)
        if stdout and stderr: msg += 'See logfiles %s and %s for details' % (stdout, stderr)
        raise Exception(msg)

    return err

    
    
def pipe(cmd, verbose=False):
    """Simplification of the new style pipe command
    
    One object p is returned and it has
    p.stdout, p.stdin and p.stderr
    
    If p.stdout is None an exception will be raised.
    """
    
    if verbose:
        print cmd
        
    p = Popen(cmd, shell=True,
              stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True)
              
    if p.stdout is None:
        msg = 'Piping of command %s could be executed' % cmd
        raise Exception(msg)
        
    return p

    
def header(s):
    dashes = '-'*len(s)
    print
    print dashes
    print s
    print dashes
    
def makedir(newdir):
    """works the way a good mkdir should :)
        - already exists, silently complete
        - regular file in the way, raise an exception
        - parent directory(ies) does not exist, make them as well

    Based on            
    http://code.activestate.com/recipes/82465/
    
    Note os.makedirs does not silently pass if directory exists.
    """
    
    if os.path.isdir(newdir):
        pass
    elif os.path.isfile(newdir):
        msg = 'a file with the same name as the desired ' \
            'dir, "%s", already exists.' % newdir
        raise OSError(msg)
    else:
        head, tail = os.path.split(newdir)
        if head and not os.path.isdir(head):
            makedir(head)
        #print "_mkdir %s" % repr(newdir)
        if tail:
            os.mkdir(newdir)


    

    	  
def get_web_page(url, username=None, password=None):
    """Get url page possible with username and password
    """

    if username is not None:

        # Create password manager
        passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
        passman.add_password(None, url, username, password)

        # create the handler
        authhandler = urllib2.HTTPBasicAuthHandler(passman)
        opener = urllib2.build_opener(authhandler)
        urllib2.install_opener(opener)
        
    try:
        pagehandle = urllib2.urlopen(url)
    except urllib2.URLError, e:
        msg = 'Could not open URL "%s": %s' % (url, e)
        raise urllib2.URLError(msg)
    else:    
        page = pagehandle.readlines()

    return page

    
def curl(url, username, password, request, content_type, rest_dir, data_type, data, verbose=False):
    """Aggregate and issue curl command:
    
    curl -u username:password -X request -H type geoserver_url/rest/rest_dir data_type data
    For example:
    
    curl -u admin:geoserver -X POST -H "Content-type: text/xml" "http://localhost:8080/geoserver/rest/workspaces" --data-ascii "<workspace><name>futnuh</name></workspace>"
    
    or 
    
    curl -u admin:geoserver -X PUT -H "image/tif" http://localhost:8080/geoserver/rest/workspaces/futnuh/coveragestores/shakemap_padang_20090930/file.geotiff  --data-binary @./data/shakemap_padang_20090930.tif
    
    """

    # Build curl command
    # FIXME (Ole): Can we use flag -S to get more error messages?
    
    # FIXME (Ole): Make content_type an optional keyword arg (e.g. not necessary in case of DELETE).
    
    cmd = 'curl -u %s:%s' % (username, password)
    cmd += ' -v' # Always add verbose flag to get error messages
    
    cmd += ' -X %s' % request
    cmd += ' -H "Content-type: %s"' % content_type     
    cmd += ' "%s"' % os.path.join(url, 'rest', rest_dir)
    if data_type:
        cmd += ' %s' % data_type
        
        assert len(data) > 0
        cmd += ' "%s"' % data

    curl_stdout = 'curl.stdout'    
    curl_stderr = 'curl.stderr'
    run(cmd, stdout=curl_stdout, stderr=curl_stderr, verbose=verbose)

    out = open(curl_stdout).readlines()
    err = open(curl_stderr).read()

    # FIXME (Ole): Check for other error conditions 
    
    if err.find('HTTP/1.1 500') > 0:
        msg = 'Curl command failed (Internal Server Error): %s, %s' % (cmd, out)        
        raise Exception(msg)
        
    if err.find('HTTP/1.1 404') > 0:
        msg = 'Curl command failed (Not Exist): %s, %s' % (cmd, out)            
        raise Exception(msg)                
        
    if err.find('HTTP/1.1 405') > 0:
        msg = 'Curl command failed (Method Not Allowed): %s, %s' % (cmd, out)                
        raise Exception(msg)        

    return out

def get_bounding_box(filename, verbose=False):
    """Get bounding box for specified file using gdalinfo
    
    gdalinfo produces this information:
    
    Corner Coordinates:
    Upper Left  (  96.9560000,   2.2894973) ( 96d57'21.60"E,  2d17'22.19"N)
    Lower Left  (  96.9560000,  -5.5187330) ( 96d57'21.60"E,  5d31'7.44"S)
    Upper Right ( 104.6412660,   2.2894973) (104d38'28.56"E,  2d17'22.19"N)
    Lower Right ( 104.6412660,  -5.5187330) (104d38'28.56"E,  5d31'7.44"S)
    Center      ( 100.7986330,  -1.6146179) (100d47'55.08"E,  1d36'52.62"S)

    
    """

    # p = pipe('gdalinfo %s' % filename)
    
    fid = osgeo.gdal.Open(filename, osgeo.gdal.GA_ReadOnly)
    if fid is None:
        msg = 'Could not open file %s' % filename            
        raise Exception(msg)            
            
    geotransform = fid.GetGeoTransform()    
    if geotransform is None:
        msg = 'Could not read geotransform from %s' % filename    
        raise Exception(msg)
    
    x_origin    = geotransform[0] # top left x
    x_res       = geotransform[1] # w-e pixel resolution 
    y_origin    = geotransform[3] # top left y 
    y_res       = geotransform[5] # n-s pixel resolution 
    # geotransform[4]  # rotation, 0 if image is "north up" 
    # geotransform[2]  # rotation, 0 if image is "north up"
    x_pix       = fid.RasterXSize
    y_pix       = fid.RasterYSize

    minx = x_origin
    maxx = x_origin + (x_pix * x_res) 
    miny = y_origin + (y_pix * y_res) # x_res -ve
    maxy = y_origin

    if verbose:
        print '\n-------------- get_bounding_box calculations --------------'    
        print 'file: %s' % filename
        print 'x origin: %s' % x_origin
        print 'y origin: %s' % y_origin
        print 'x res: %s' % x_res
        print 'y res: %s' % y_res
        print 'x pixels: %s' % x_pix
        print 'y pixels: %s' %y_pix
        print 'data type: %s' % osgeo.gdal.GetDataTypeName(fid.GetRasterBand(1).DataType)
        print [minx, miny, maxx, maxy]
        print '------------------------------------------------------------\n'
        
    
    return [minx, miny, maxx, maxy]
    
    # ll = ur = False
    # for line in p.stdout.readlines():
    #     fields = line.split()
    #     
    #     if line.startswith('Lower Left'):
    #         minlon = float(fields[3][:-1])
    #         minlat = float(fields[4][:-1])
    #         ll = True
    #         
    #     if line.startswith('Upper Right'):
    #         maxlon = float(fields[3][:-1])
    #         maxlat = float(fields[4][:-1])            
    #         ur = True            
    # 
    # 
    # if ll and ur:
    #     return [minlon, minlat, maxlon, maxlat]

    # What is this doing here?
    # This code will never be reached        
    #if dataset is None:
    #    msg = 'Bounding box could not be established for %s' % filename
    #    raise Exception(msg)


def get_cellsize(filename, verbose=False):
    """Get cellsize for specified file using gdalinfo
    
    gdalinfo produces this information:
    
    Driver: GTiff/GeoTIFF
    Files: Earthquake_Fatalities_National_clip.tif
    Size is 345, 263
    Coordinate System is:
    GEOGCS["WGS 84",
        DATUM["WGS_1984",
            SPHEROID["WGS 84",6378137,298.2572235630016,
                AUTHORITY["EPSG","7030"]],
            AUTHORITY["EPSG","6326"]],
        PRIMEM["Greenwich",0],
        UNIT["degree",0.0174532925199433],
        AUTHORITY["EPSG","4326"]]
    Origin = (99.359999999999999,-0.007333333421000)
    Pixel Size = (0.008333333333000,-0.008333333333000)
    Metadata:
      AREA_OR_POINT=Area
    Image Structure Metadata:
      INTERLEAVE=BAND
    Corner Coordinates:
    Upper Left  (  99.3600000,  -0.0073333) ( 99d21'36.00"E,  0d 0'26.40"S)
    Lower Left  (  99.3600000,  -2.1990000) ( 99d21'36.00"E,  2d11'56.40"S)
    Upper Right ( 102.2350000,  -0.0073333) (102d14'6.00"E,  0d 0'26.40"S)
    Lower Right ( 102.2350000,  -2.1990000) (102d14'6.00"E,  2d11'56.40"S)
    Center      ( 100.7975000,  -1.1031667) (100d47'51.00"E,  1d 6'11.40"S)
    Band 1 Block=345x2 Type=Float64, ColorInterp=Gray

    
    """

    
    #### FIXME: TODO
    
    # p = pipe('gdalinfo %s' % filename)
    
    fid = osgeo.gdal.Open(filename, osgeo.gdal.GA_ReadOnly)
    if fid is None:
        msg = 'Could not open file %s' % filename            
        raise Exception(msg)            
            
    geotransform = fid.GetGeoTransform()    
    if geotransform is None:
        msg = 'Could not read geotransform from %s' % filename    
        raise Exception(msg)
    
    x_origin    = geotransform[0] # top left x
    x_res       = geotransform[1] # w-e pixel resolution 
    y_origin    = geotransform[3] # top left y 
    y_res       = geotransform[5] # n-s pixel resolution 
    # geotransform[4]  # rotation, 0 if image is "north up" 
    # geotransform[2]  # rotation, 0 if image is "north up"
    x_pix       = fid.RasterXSize
    y_pix       = fid.RasterYSize

    minx = x_origin
    maxx = x_origin + (x_pix * x_res) 
    miny = y_origin + (y_pix * y_res) # x_res -ve
    maxy = y_origin

    if verbose:
        print '\n-------------- get_bounding_box calculations --------------'    
        print 'file: %s' % filename
        print 'x origin: %s' % x_origin
        print 'y origin: %s' % y_origin
        print 'x res: %s' % x_res
        print 'y res: %s' % y_res
        print 'x pixels: %s' % x_pix
        print 'y pixels: %s' %y_pix
        print 'data type: %s' % osgeo.gdal.GetDataTypeName(fid.GetRasterBand(1).DataType)
        print [minx, miny, maxx, maxy]
        print '------------------------------------------------------------\n'
        
    
    return [minx, miny, maxx, maxy]
    
    

def get_pathname_from_package(package):
    """Get pathname of given package (provided as string)

    This is useful for reading files residing in the same directory as
    a particular module. Typically, this is required in unit tests depending
    on external files.

    The given module must start from a directory on the pythonpath
    and be importable using the import statement.

    Example
    path = get_pathname_from_package('anuga.utilities')

    """

    exec('import %s as x' %package)

    path = x.__path__[0]

    return path
