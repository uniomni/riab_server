"""Start Geoserver instance
"""

import sys, os, time, commands
import urllib
import platform
from install_geoserver import run_startup

# This is the local address for the server running on host
geoserver_url = 'http://localhost:8080/geoserver'


# Stop any geoserver process first
execfile('stop_geoserver.py')


# Install and start new geoserver
print 'Starting Geoserver (please wait 20-30 seconds or so)'
cmd = 'sudo python __geoserver_start__.py > geoserver.log 2> geoserver.err &'
os.system(cmd)


# Wait until ready
t0 = time.time()
time_out = 60 # Wait no more than these many seconds 
running = False
while not running and time.time()-t0 < time_out:

    time.sleep(1)
            
    try:        
        fid = urllib.urlopen(geoserver_url)            
    except IOError, e:
        running = False
    else:
        running = True


if not running:
    raise Exception('Geoserver did not start.')
else:
    print 'Geoserver ready at %s (installed in %i seconds).' % (geoserver_url, time.time()-t0)


