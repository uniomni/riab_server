"""Stop all servers used by test_all.py
"""

import os
        
# Add location of source code to search path so that API can be imported
parent_dir = os.path.split(os.getcwd())[0]
source_path = os.path.join(parent_dir, 'source') 
geoserver_path = os.path.join(parent_dir, 'installation') 

# Stop the XMLRPC Riab Server
os.system('python %s/%s --stop' % (source_path, 'riab_server.py'))

# Stop GeoServer
os.system('python %s/%s' % (geoserver_path, 'stop_geoserver.py'))
