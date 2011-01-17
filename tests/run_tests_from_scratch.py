import os
import sys
import xmlrpclib
from config import test_url
        
# Add location of source code to search path so that API can be imported
parent_dir = os.path.split(os.getcwd())[0]
source_path = os.path.join(parent_dir, 'source') 

# Stop any running XMLRPC server(s)

try:
    xmlrpclib.ServerProxy(test_url).stop()
except:
    pass


# Start XMLRPC Riab Server
os.system('python %s/%s &' % (source_path, 'riab_server.py'))

while(True):
    riab_server = xmlrpclib.ServerProxy(test_url)
    try:
        riab_server.reload()
    except:
        # Server is not running
        pass
    else:
        # Server is up and running
        break
    
# Run test suite
os.system('python test_riab_server.py')
