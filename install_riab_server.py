"""Install new Riab server

Usage:

sudo python install_geoserver.py
"""

import sys, os, commands
from utilities import run, makedir, header, replace_string_in_file, get_shell, set_bash_variable


def install_ubuntu_packages():    
    """Get required Ubuntu packages for riab_server.
       It is OK if they are already installed
    """

    header('Installing Ubuntu packages')     
    
    s = 'apt-get clean'
    run(s, verbose=True)
    
    
    for package in [ 'curl', 'python-pycurl', 'python-gdal', 'python-setuptools']:

                    
        s = 'apt-get -y install %s' % package
        
        log_base = '%s_install' % package
        try:
            run(s,
                stdout=log_base + '.out',
                stderr=log_base + '.err',                  
                verbose=True)
        except:
            msg = 'Installation of package %s failed. ' % package
            msg += 'See log file %s.out and %s.err for details' % (log_base, log_base)
            raise Exception(msg)
            

def install_python_packages():
    """Python packages that are not part of Ubuntu
    """
    os.system('easy_install argparse')

    
def get_plugins():
    """Get plugins such as REST
    """
    pass
    
def change_permissions():
    """    """
    pass

    
def set_environment():
    """
    """
    pass


    

if __name__ == '__main__':

    s = commands.getoutput('whoami')
    if s != 'root':
        print
        print 'Script must be run as root e.g. using: sudo python %s' % sys.argv[0]
        import sys; sys.exit() 

    print ' - Installing Riab_server Dependancies'
                
    install_ubuntu_packages()
    install_python_packages()
    get_plugins()
    change_permissions()
    set_environment()    
    print 'Riab_server dependancies installed. To start it run'
    print 'python source/riab_server.py'
    print 'Defaults to localhost:8000'
