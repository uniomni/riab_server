# Enter mapping between local hostname and hostname as accessed by browser
hostnames = {#'shiva': '192.168.40.102',
             'shiva': '203.77.224.75',
             'web-server': 'www.aifdr.org'}
	     

import os
try:
    webhost = hostnames[os.uname()[1]]
except:
    # For example if running off a USB stick
    webhost = 'localhost'

datadir = ('impact_modelling_data')

webdir = '/var/www/riab'
