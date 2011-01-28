"""Start all servers for use with test_all.py
"""

import os
import sys
import xmlrpclib
from config import test_url
        
# Add location of source code to search path so that API can be imported
parent_dir = os.path.split(os.getcwd())[0]
source_path = os.path.join(parent_dir, 'source') 
geoserver_path = os.path.join(parent_dir, 'installation') 

# Stop the XMLRPC Riab Server if its running
os.system('python %s/%s --stop' % (source_path, 'riab_server.py'))

# Start XMLRPC Riab Server
os.system('python %s/%s 2> riab_server_start.stderr & ' % (source_path, 
                                                     'riab_server.py'))
while(True):
    riab_server = xmlrpclib.ServerProxy(test_url)
    try:
        riab_server.reload()
    except:
        # Server is not running
        pass
    else:
        # Server is ready
        break



