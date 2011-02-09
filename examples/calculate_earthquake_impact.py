"""Calculate estimated fatalities based on nat'l hazard map and landscan data
"""

import sys, os, string, os
from config import webhost, datadir, webdir

# Add location of source code to search path so that API can be imported
parent_dir = os.path.split(os.getcwd())[0]
source_path = os.path.join(parent_dir, 'source') 
sys.path.append(source_path)

# Import everything from the API
from geoserver_api.geoserver import *
from geoserver_api.utilities import header


# Output workspace
workspace = 'impact'


# Fatality model parameters (Allen 2010:-)
a = 0.97429
b = 11.037

# Locations
bounding_box = [95.06, -10.997, 141.001, 5.911] # Taken from Geoserver
#bounding_box = [99.36, -2.199, 102.237, 0.000] # Padang area

geoserver = Geoserver('http://%s:8080/geoserver' % webhost,
                      'admin',
                      'geoserver')        
    

# Download hazard and exposure data
layername = 'Earthquake_Ground_Shaking'
print 'Get hazard level:', layername
hazard_raster = geoserver.get_raster_data(coverage_name=layername,
                                          bounding_box=bounding_box,
                                          workspace='hazard',
                                          verbose=False)            
            
#layername = 'landscan_2008'
layername = 'Population_2010'
print 'Get exposure data:', layername            
exposure_raster = geoserver.get_raster_data(coverage_name=layername,
                                            bounding_box=bounding_box,
                                            workspace='exposure',
                                            verbose=False)            
                                                 
# Calculate impact
print 'Calculate impact'            
E = exposure_raster.get_data(nan=True)
H = hazard_raster.get_data(nan=True)
#E = exposure_raster.data
#H = hazard_raster.data
F = 10**(a*H-b)*E 

# Store result and upload
layername = 'Earthquake_Fatalities_National_Padang'          
                
output_file = '%s/%s/%s.asc' % (datadir, workspace, layername)
print 'Store result in:', output_file
raster.write_coverage_to_ascii(F, output_file, 
                        xllcorner = bounding_box[0],
                        yllcorner = bounding_box[1])
                                                
# And upload it

print 'Upload to Geoserver:', layername
geoserver.create_workspace(workspace)
geoserver.upload_coverage(filename=output_file, 
                          workspace=workspace)
