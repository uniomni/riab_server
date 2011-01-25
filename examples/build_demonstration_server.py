"""Build test server and upload data

# Data is assumed to reside in subdirectories of ./data named by their workspace.
# The standard workspace names are
# - hazard
# - exposure
# - boundaries
# - impact
# - sources
             
Two websites are made

http://localhost/riab/layers.html
http://localhost/riab/layers_local.html

The latter can run without internet access provided the geoserver is run locally.
To avoid firefox starting in off-line mode, create new boolean variable
network.manage-offline-status and set it to false.
To do this type in about:config as the url, right click and create.


"""


# Specify order of known layers
vector_layer_order = ['boundaries:Province_Boundaries', 'boundaries:District_Boundaries', 'boundaries:Subdistrict_Boundaries', 'boundaries:Village_Boundaries', 'sources:Subduction_Zones', 'sources:Earthquake_Faults', 'sources:Active_Volcanoes', 'exposure:AIBEP_schools', 'impact:School_lembang_buildingloss']

raster_layer_order = ['exposure:Population_2010', 'hazard:Earthquake_Ground_Shaking', 'hazard:Lembang_Earthquake_Scenario', 'hazard:Shakemap_Padang_2009', 'impact:Earthquake_Fatalities']

# Excluded files
excluded_files = ['Village_Boundaries.shp']

             
import sys, os, string, os
from config import webhost, datadir, webdir

# Add location of source code to search path so that API can be imported
parent_dir = os.path.split(os.getcwd())[0]
source_path = os.path.join(parent_dir, 'source') 
sys.path.append(source_path)


# Import everything from the API
from geoserver_api.geoserver import *
from geoserver_api.utilities import header



if __name__ == '__main__':

    # Build and activate new geoserver
    geoserver_url = 'http://localhost:8080/geoserver'
    web_url = 'http://localhost/riab'     # FIXME: Rationalise this later
    
    geoserver_username = 'admin' 
    geoserver_userpass = 'geoserver'    
    
    parent_dir = os.path.split(os.getcwd())[0]    
    
    
    # Stop Geoserver
    s = 'cd %s/installation; python stop_geoserver.py' % parent_dir    
    os.system(s)
            
    # Install Geoserver
    print ' - Installing new Geoserver from scratch'    
    #s = 'cd %s/install_geoserver; sudo python install_geoserver.py > install_geoserver.log 2>install_geoserver.err' % parent_dir    
    s = 'cd %s/installation; sudo python install_geoserver.py' % parent_dir        
    os.system(s)
        
    # Start Geoserver
    s = 'cd %s/installation; python start_geoserver.py' % parent_dir    
    os.system(s)

    
    geoserver = Geoserver(geoserver_url, 
                          geoserver_username, 
                          geoserver_userpass)            
    
        
    # Upload test data and record layers for subsequent generation of Open Layers file
    raster_layers = []
    vector_layers = []    
    
    for workspace in os.listdir(datadir):
        subdir = os.path.join(datadir, workspace)
            
        if os.path.isdir(subdir):

            # Create new workspace
            geoserver.create_workspace(workspace, verbose=True)

            for filename in os.listdir(subdir):

                if filename in excluded_files:
                    continue
            
                basename, extension = os.path.splitext(filename)
                
                if extension in ['.asc', '.txt', '.tif', '.shp', '.zip']:                
                    header('Uploading %s' % filename)
                    lyr = geoserver.upload_layer(filename='%s/%s' % (subdir, filename),
                                                 workspace=workspace,
                                                 verbose=True)                
                

                    if extension in ['.asc', '.txt', '.tif']:
                        raster_layers.append(lyr)

                    if extension in ['.shp']:        
                        vector_layers.append(lyr)                                                

    # Ensure that rasters come first and observe specified order                
    layers = []                    
    for raster in raster_layer_order:                    
        if raster in raster_layers:
            layers.append(raster)
        else: 
            try:
                raster_layers.remove(raster)
            except ValueError:
                pass
    layers += raster_layers
            
    leftovers = []
    for vector in vector_layer_order:                    
        if vector in vector_layers:
            layers.append(vector)
        else:
            try:
                vector_layers.remove(vector)
            except ValueError:
                pass
                
    layers += vector_layers
     
    #print    
    #print 'Got layers: %s' % layers
    
    # Generate Open Layers content
    html = ''
    for layer in layers:
        html += '\n\n'
        
        wk, lr = layer.split(':')
        
        if lr.lower().startswith('base'):
            baselayer = 'true'
        else:
            baselayer = 'false'
        
        html += 'var %s = new OpenLayers.Layer.WMS("%s",\n' % (lr, lr[:29].replace('_', ' '))
        html += '                        "http://%s:8080/geoserver/wms?service=wms",\n' % webhost
        html += '                        {\n'
        html += '                            layers: "%s",\n' % layer
        html += '                            transparent: "true",\n'
        html += '                            format: "image/png"\n'
        html += '                        },\n'
        html += '                        {isBaseLayer: %s, visibility: false, opacity: 0.8}\n' % baselayer
        html += '                        );\n'                
            

    #print html

    
#-------------------------------------------------    
# Build open layers web site with the above layers


#cmd = 'cp bnpb_logo.jpg aifdr_logo.jpg %s' % webdir
#run(cmd)


layers = [layer.split(':')[1] for layer in layers]

baselayers = ['gphy', 'gmap', 'gsat', 'veaer', 'yahoosat', 'ol_wms'] # Do not change
wwwfid = open('%s/layers.html' % webdir, 'w')
wwwfid_local = open('%s/layers_local.html' % webdir, 'w')

from html_templates import body, header_template, footer_template, header_template_local
wwwfid.write(header_template); wwwfid_local.write(header_template_local)

wwwfid.write(html); wwwfid_local.write(html)
wwwfid.write('\n'); wwwfid_local.write('\n');

# Add layers code to main site
s = '// Add the created layers to the map\n'
s += 'map.addLayers(['
for layer in baselayers + layers:
    s += layer + ', '
s = s[:-2] + ']);\n\n'
wwwfid.write(s)


# Add layers code to local site
s = '// Add the created layers to the map\n'
s += 'map.addLayers(['
for layer in layers:
    s += layer + ', '
s = s[:-2] + ']);\n\n'
wwwfid_local.write(s)



# Add footers to both

wwwfid.write(footer_template); wwwfid_local.write(footer_template)
wwwfid.write(body); wwwfid_local.write(body)
wwwfid.close(); wwwfid_local.close()


print 
header('Website created at URL: %s/riab/layers.html' % webhost)
print
print


# Copy back to geoserver for legacy
cmd = 'cp -R %s/* %s' % (webdir, '/usr/local/geoserver-2.0.2/data_dir/www')
run(cmd, verbose=False)
