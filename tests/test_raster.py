import sys, os, string
import numpy
import unittest


# Add location of source code to search path so that API can be imported
parent_dir = os.path.split(os.getcwd())[0]
source_path = os.path.join(parent_dir, 'source') 
sys.path.append(source_path)

# Import everything from the API
from geoserver_api.raster import read_coverage, write_coverage_to_geotiff, read_coverage_asc, Raster


class Test_raster(unittest.TestCase):


    def setUp(self):
        pass

    
    def tearDown(self):
        pass


    def test_read_and_write_of_rasters(self):        
        """Test that rasters can be read and written correctly
        """    
        
        for coveragename in ['Earthquake_Ground_Shaking_clip.tif',
                             'Population_2010_clip.tif',
                             'shakemap_padang_20090930.asc',
                             'population_padang_1.asc']:
        
            filename = 'data/%s' % coveragename
            for R1 in [Raster(filename), read_coverage(filename)]:
                
                # Check consistency of raster
                A1 = R1.get_data()
                M, N = A1.shape
                
                msg = 'Dimensions of raster array do not match those of raster file %s' % R1.filename
                assert M == R1.rows, msg
                assert N == R1.columns, msg        

                # Write back to new file
                outfilename = '/tmp/%s' % coveragename
                try:
                    os.remove(outfilename)
                except:    
                    pass
                
                write_coverage_to_geotiff(A1, outfilename, R1.get_projection(), R1.get_geotransform())
                
                # Read again and check consistency
                R2 = Raster(outfilename)                
                
                msg = 'Dimensions of written raster array do not match those of input raster file\n'
                msg += '    Dimensions of input file %s:  (%s, %s)\n' % (R1.filename, R1.rows, R1.columns)
                msg += '    Dimensions of output file %s: (%s, %s)' % (R2.filename, R2.rows, R2.columns)                
                assert R1.rows == R2.rows, msg
                assert R1.columns == R2.columns, msg                        
        
                A2 = R2.get_data()     
                
                assert numpy.allclose(numpy.min(A1), numpy.min(A2))
                assert numpy.allclose(numpy.max(A1), numpy.max(A2))                

                msg = 'Array values of written raster array were not as expected'
                assert numpy.allclose(A1, A2), msg           
                
                # NOTE: This does not always hold as projection text might differ slightly. E.g.
                #assert R1.get_projection() == R2.get_projection(), msg  
                #E.g. These two refer to the same projection
                #GEOGCS["GCS_WGS_1984",DATUM["WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]]
                #GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.2572235630016,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433],AUTHORITY["EPSG","4326"]]
                
                msg = 'Geotransforms were different'
                assert R1.get_geotransform() == R2.get_geotransform(), msg                  


        
    def test_raster_extrema(self):
        """Test that raster extrema are correct.
        """

        # FIXME (Ole): Some datasets show very large differences between extrema in the array and 
        # those computed by GDAL. This may warrant another bug report to GEOS
        
                              
        for coveragename in ['Earthquake_Ground_Shaking_clip.tif',
                             'Population_2010_clip.tif',
                             'shakemap_padang_20090930.asc',
                             'population_padang_1.asc',
                             'population_padang_2.asc']:
        
            
            filename = 'data/%s' % coveragename
            for R in [Raster(filename), read_coverage(filename)]:
                
                # Check consistency of raster
                minimum, maximum = R.get_extrema()
                
                # Check that arrays with NODATA value replaced by NaN's agree
                A = R.get_data(nan=False)
                B = R.get_data(nan=True)
                
                assert A.dtype == B.dtype
                assert numpy.nanmax(A-B) == 0                
                assert numpy.nanmax(B-A) == 0                                
                assert numpy.nanmax(numpy.abs(A-B)) == 0

                # Check that GDAL's reported extrema match real extrema
                # FIXME (Ole): The discrepancies are not acceptable. Report to GEOS.                
                assert numpy.allclose(maximum, numpy.max(A[:]), rtol=1.0e-1) # FIXME: Very very high rtol                         
                assert numpy.allclose(maximum, numpy.nanmax(B[:]), rtol=1.0e-1) # FIXME: Very very high rtol         

                assert numpy.allclose(minimum, numpy.min(A[:]), rtol=1e-2) # FIXME: Not good either           
                #assert numpy.allclose(minimum, numpy.nanmin(B[:]), rtol=1e-2) # This shows that the minimum is -9999. Is that perhaps OK? 

            
        
    def test_bins(self):
        """Test that linear and quantile bins are correct
        """

        
        for filename in ['data/population_padang_1.asc', 
                         'data/test_grid.asc']: 
        
            R = read_coverage(filename)
        
            min, max = R.get_extrema() #use_numeric=True)
        
            for N in [2,3,5,7,10,16]:
                linear_intervals = R.get_bins(N=N, quantiles=False)                
        
                assert linear_intervals[0] == min
                assert linear_intervals[-1] == max        
        
                d = (max-min)/N
                for i in range(N):
                    assert numpy.allclose(linear_intervals[i], min + i*d) 
                
                
                quantiles = R.get_bins(N=N, quantiles=True)

                A = R.get_data(nan=True).flat[:]                        
                
                mask = numpy.logical_not(numpy.isnan(A)) # Omit NaN's
                l1 = len(A)
                A = A.compress(mask)                
                l2 = len(A)
                
                if filename == 'data/test_grid.asc':
                    # Check that NaN's were removed
                    
                    assert l1 == 35
                    assert l2 == 30
                    
                    
                # Assert that there are no NaN's    
                assert not numpy.alltrue(numpy.isnan(A))
                                
                number_of_elements = len(A)
                average_elements_per_bin = number_of_elements/N
                
                # Count elements in each bin and check

                i0 = quantiles[0]
                for i1 in quantiles[1:]:
                    count = numpy.sum((i0 < A) & (A < i1))
                    if i0 == quantiles[0]:
                        refcount = count
                        
                        
                    if i1 < quantiles[-1]:
                        # Number of elements in each bin must vary by no more than 1
                        assert abs(count - refcount) <= 1    
                        assert abs(count - average_elements_per_bin) <= 3
                        
                        
                    else:
                        # The last bin is allowed vary by more
                        pass
                        
                    i0 = i1


            
    def test_nodata(self):
        """Test that NODATA is treated correctly
        """

        
        filename = 'data/test_grid.asc'
        R = read_coverage(filename)
        
        nan = R.get_nodata_value()
        assert nan == -9999
        
        A = R.get_data(nan=False)
        assert numpy.min(A[:]) == -9999
        assert numpy.allclose(numpy.max(A[:]), 50.9879837036)                
        
        A = R.get_data(nan=True)
        assert numpy.allclose(numpy.nanmin(A[:]), -50.60135540866)
        assert numpy.allclose(numpy.nanmax(A[:]), 50.9879837036)        
        
        
            
    #FIXME: Need test of read and write: data, metadata, M and N!!
                                    
################################################################################

if __name__ == '__main__':
    suite = unittest.makeSuite(Test_raster, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
