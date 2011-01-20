"""Top test script for riab_server

Start all test servers, run the test suite and stop servers
"""

import os

# Run installation scripts
os.system('cd ../installation; sudo python install_geoserver.py')
os.system('cd ../installation; sudo python install_riab_server.py')
        
# Make sure all local servers are running
execfile('start_all_servers.py')

# Run test suite
os.system('python test_all.py')

# Stop all test servers
execfile('stop_all_servers.py')
