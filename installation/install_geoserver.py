"""Install new Geoserver system wide

Usage:

sudo python install_geoserver.py
"""

import sys, os, commands
from config import geoserver, java_home, geoserver_url, geoserver_rest_plugin, geoserver_rest_plugin_url, webdir, workdir
from utilities import run, makedir, header


def install_ubuntu_packages():    
    """Get required Ubuntu packages for geoserver.
       It is OK if they are already installed
    """

    header('Installing Ubuntu packages')     
    
    s = 'apt-get clean'
    run(s, verbose=True)

    for package in ['apache2', 'openjdk-6-jre-lib', 'gdal-bin', 'curl', 'python-pycurl', 'python-gdal', 'python-setuptools']:

        s = 'apt-get -y install %s' % package
        
        log_base = workdir + '/' + '%s_install' % package
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

    # OWSLIB frozen at r1672 (5 August 2010)
    try:
        import owslib
    except:    
        cmd = 'cd /tmp; svn co -r 1672 http://svn.gispython.org/svn/gispy/OWSLib/trunk OWSLib'
        run(cmd)
    
        cmd = 'cd /tmp/OWSLib; sudo python setup.py install'
        run(cmd)

#def get_packages_from_source():
#    """Get packages that shouldn't come from the Ubuntu repository - such as newer versions
#    """
#    
#    
#    # GDAL 1.6.3
#    gdal_version = '1.6.3'
#    s = commands.getoutput('gdalinfo --version')
#    print s
#    if s.find(version) > 0:
#        # Nothing to do
#        return
#    
#    archive = 'gdal-%s.tar.gz' % gdal_version
#    path = 'http://download.osgeo.org/gdal/%s' % archive
#    
#    if not os.path.isfile(archive): 
#        # FIXME: Should also check integrity of tgz file.
#        cmd = 'wget ' + path
#        run(cmd, verbose=True)
#    
#        cmd = 'tar -zvxf %s' % archive
#        run(cmd, verbose=True)
#        
#        cmd = 'cd gdal-%s; ./configure --with-static-proj4=/usr/local/lib --with-threads --with-libtiff=internal --with-geotiff=internal --with-jpeg=internal --with-gif=internal --with-png=internal --with-libz=internal' % gdal_version
#        run(cmd, verbose=True)        
#        
#        cmd = 'cd gdal-%s; make; make install' % gdal_version
#        run(cmd, verbose=True)                
        

def download_and_unpack():    
    """Download geoserver OS independent files
    """

    archive = workdir + '/' + geoserver + '-bin.zip'


    path = os.path.join(geoserver_url, archive)

    if not os.path.isfile(archive): 
        # FIXME: Should also check integrity of zip file.
        cmd = 'cd %s; wget %s' % (workdir, path)
        run(cmd, verbose=True)


    # Clean out
    s = '/bin/rm -rf /usr/local/%s' % geoserver
    run(s, verbose=True)

    # Unpack
    s = 'unzip %s -d /usr/local' % archive
    run(s, verbose=True)    

    
def get_plugins():
    """Get plugins such as REST
    """
    
    path = geoserver_rest_plugin_url
    
    archive = workdir + '/' + geoserver_rest_plugin
    print 'Archive', archive
    if not os.path.isfile(archive): 
        # FIXME: Should also check integrity of zip file.
        cmd = 'cd %s; wget %s' % (workdir, path)        
        run(cmd, verbose=True)
    
    # Unpack into geoserver installation
    s = 'unzip %s -d /usr/local/%s/webapps/geoserver/WEB-INF/lib' % (archive, 
                                                                     geoserver)
    run(s, verbose=True)        

    
def change_permissions():
    """Make ../data_dir/www writable to all and make web dir
    """
    
    s = 'chmod -R a+w /usr/local/%s/data_dir/www' % geoserver
    run(s, verbose=True)            

    makedir(webdir)
    s = 'chown -R www-data:www-data %s' % webdir
    run(s, verbose=True)                
        
    s = 'chmod -R a+w %s' % webdir
    run(s, verbose=True)                


    
def set_environment():
    """Set up /etc/default/geoserver
    """

    fid = open('/etc/default/geoserver', 'wb')
    
    fid.write('USER=geoserver\n')
    fid.write('GEOSERVER_DATA_DIR=/usr/local/%s/data_dir\n' % geoserver)    
    fid.write('GEOSERVER_HOME=/usr/local/%s\n' % geoserver)
    fid.write('JAVA_HOME=%s\n' % java_home)
    fid.write('JAVA_OPTS="-Xms128m -Xmx512m"\n')

    #GEOSERVER_DATA_DIR=/home/$USER/data_dir
    #GEOSERVER_HOME=/home/$USER/geoserver
    
    fid.close()

def run_startup():
    """Run geoserver startup script
    """

    geo_home = '/usr/local/%s' % geoserver
    cmd = 'export JAVA_HOME=%s; export GEOSERVER_HOME=%s; $GEOSERVER_HOME/bin/startup.sh' % (java_home, 
                                                                                             geo_home)
                                                                                             
    os.system(cmd)
    
def install_openlayers():
    """Install OpenLayers locally
    This will allow web frontend to run without Internet access
    """
    
    ol_dir = '/var/www/openlayers'
    cmd = 'svn checkout http://svn.openlayers.org/trunk/openlayers/ %s' % ol_dir 
    run(cmd, verbose=True)

    cmd = 'chown -R www-data:www-data %s' % ol_dir
    run(cmd, verbose=True)
    
    

if __name__ == '__main__':

    s = commands.getoutput('whoami')
    if s != 'root':
        print
        print 'Script must be run as root e.g. using: sudo python %s' % sys.argv[0]
        import sys; sys.exit() 

    print ' - Installing new Geoserver'

    # Create area for logs and downloads
    makedir(workdir)

    # Install GeoServer and dependencies
    install_ubuntu_packages()
    install_python_packages()
    download_and_unpack()
    get_plugins()
    change_permissions()
    set_environment()    
    install_openlayers()
    print 'Geoserver installed. To start it run'
    print 'python start_geoserver.py'
    #run_startup()
