"""Start Geoserver instance locally - internal script
Must be run as sudo
"""

import sys, os, commands
import platform
from install_geoserver import run_startup

s = commands.getoutput('whoami')
if s != 'root':
    print
    print 'Script must be run as root e.g. using: sudo python %s' % sys.argv[0]
    import sys; sys.exit() 
        
# Start geoserver
run_startup()



