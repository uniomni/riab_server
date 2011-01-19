
geoserver_url = 'http://downloads.sourceforge.net/geoserver'
geoserver_extension_url = 'http://sourceforge.net/projects/geoserver/files/GeoServer\ Extensions'

geoserver_version = '2.0.2'         
geoserver = 'geoserver-%s' % geoserver_version
geoserver_rest_plugin = 'geoserver-%s-restconfig-plugin.zip' % (geoserver_version)
#geoserver_rest_plugin_url = '%s/%s/%s/download' % (geoserver_extension_url, 
#                                                   geoserver_version, 
#                                                   geoserver_rest_plugin)

geoserver_rest_plugin_url = '%s/%s/%s' % (geoserver_extension_url, 
                                          geoserver_version, 
                                          geoserver_rest_plugin)


java_home = '/usr/lib/jvm/java-6-openjdk'

filenames_updated = {} # Keep track of files edited
update_marker = '# Updated by GeoServer install script'

webdir = '/var/www/riab'
workdir = 'logfiles' # Area for installation logs and downloads
