import sys, os, string
import numpy
import unittest


# Add location of source code to search path so that API can be imported
parent_dir = os.path.split(os.getcwd())[0]
source_path = os.path.join(parent_dir, 'source') 
sys.path.append(source_path)

# Import everything from the API
from geoserver_api.raster import read_coverage, write_coverage_to_ascii, read_coverage_asc, Raster
#from geoserver_api.raster import *


class Test_raster(unittest.TestCase):


    def setUp(self):
        """Connect to test geoserver with new instance
        """
        
        pass

    
    def tearDown(self):
        """Destroy test geoserver again next test
        """
        
        pass
        #execfile('stop_geoserver.py')    


    def test_read_raster(self):
        """Test that raster can be read from file and accessed.
        """

        # FIXME (Ole): Some datasets show very large differences between extrema in the array and 
        # those computed by GDAL. This may warrant another bug report to GEOS
        
        for coverage_name in ['test_grid', 
                              'shakemap_padang_20090930',
                              'population_padang_1',
                              'population_padang_2',
                              #'fatality_padang_1',
                              #'fatality_padang_2'
                              ]:
    
            
            filename = 'data/%s.asc' % coverage_name
            
            for R in [Raster(filename), read_coverage(filename)]:
                        
                min, max = R.get_extrema()
                
                A = R.get_data(nan=True)
                B = R.get_data(nan=True)

                assert numpy.nanmax(A - B) == 0

            
                # FIXME (Ole): These tolerances are not really acceptable. Report to GEOS.
                assert numpy.allclose(min, numpy.nanmin(A[:]), rtol=1e-2)
            
                if coverage_name != 'population_padang_2':
                    assert numpy.allclose(max, numpy.nanmax(A[:]), rtol=1e-2)
            
        
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
        
        
            
                        
################################################################################

if __name__ == '__main__':
    suite = unittest.makeSuite(Test_raster, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
