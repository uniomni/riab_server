
body = """
<body onload="init()">

    <center>
       <h1>Spatial Data Demo</h1>    
    </center>    

    
    <div id="map"></div>    
        

  </body>
</html>
"""
        
	
header_template = """
<html xmlns="http://www.w3.org/1999/xhtml">
  <head>
  
    <link rel="stylesheet" href="/geoserver/style.css" type="text/css" />
    <link rel="stylesheet" href="openlayers/theme/default/style.css" type="text/css" />
    
    <script src="http://openlayers.org/dev/OpenLayers.js"></script>      
    <script src="http://dev.virtualearth.net/mapcontrol/mapcontrol.ashx?v=6.2&mkt=en-us"></script>
    <script src="http://api.maps.yahoo.com/ajaxymap?v=3.0&appid=euzuro-openlayers"></script>
    
    <script src="http://maps.google.com/maps/api/js?sensor=false"></script>
    
    
    <style type="text/css">
      body {margin: 1em;}
      #map {
        width: 98%%;
        height: 850px;
        border: 5px solid gray;
      }
      div.olControlMousePosition {
        color: white;
      }
    </style>


    <script type="text/javascript">

      function init(){
      
	  var options = {
	      // the "community" epsg code for spherical mercator
	      projection: "EPSG:900913",
	      // map horizontal units are meters
	      units: "m",
	      // this resolution displays the globe in one 256x256 pixel tile
	      maxResolution: 78271.51695,
	      // these are the bounds of the globe in sperical mercator
	      maxExtent: new OpenLayers.Bounds(-20037508, -20037508,
					       20037508, 20037508)
	  };
	    
	  // construct a map with the above options
	  map = new OpenLayers.Map("map", options);
          
          
	  // create Google Physical layer          
          var gphy = new OpenLayers.Layer.Google("Google Physical",
                                                 {type: google.maps.MapTypeId.TERRAIN}
                                                );
                                                
	  // create Google Maps layer
	  var gmap = new OpenLayers.Layer.Google("Google Maps",
						 {numZoomLevels: 20, sphericalMercator: true}
						 );
                                                
	  // create Google Sattelite layer
          var gsat = new OpenLayers.Layer.Google("Google Satellite",
						 {type: google.maps.MapTypeId.SATELLITE, sphericalMercator: true}
						 );
                                                
	  // create Google Hybrid layer                                                          
          var ghyb = new OpenLayers.Layer.Google("Google Hybrid",
                                                 {type: google.maps.MapTypeId.HYBRID, numZoomLevels: 20}
                                                );
          
	  // create Virtual Earth layer
	  var veaer = new OpenLayers.Layer.VirtualEarth("Virtual Earth",
							{type: VEMapStyle.Aerial, sphericalMercator: true}
                                                        );
	    
	  // create Yahoo layer (only the default layer works, the hybrid and the
	  // satellite ones do throw exceptions and rendering goes totally bye bye)
	  var yahoosat = new OpenLayers.Layer.Yahoo("Yahoo Maps",
						    {sphericalMercator: true}
						    );
	    
	  // Openlayers background
	  var ol_wms = new OpenLayers.Layer.WMS("OpenLayers WMS",
						"http://labs.metacarta.com/wms/vmap0",
						{layers: "basic"}
						);
"""


footer_template = """

          // Enable switching of layers	  
	  map.addControl(new OpenLayers.Control.LayerSwitcher());
	 
          // Map extent for Indonesia in Spherical Mercator coordinates
	  //var initial_boundary = new OpenLayers.Bounds(9062374, -1374643, 15891564, 1130045);
          //var initial_boundary = new OpenLayers.Bounds(9062374, -1374643, 15891564, 1130045);          
	  var initial_boundary = new OpenLayers.Bounds(11800000, -900000, 13500000,  400000);	  
            
          // Show coordinates (as lat and lon in WGS84) under mouse pointer	  
          mp = new OpenLayers.Control.MousePosition();
	  mp.displayProjection = new OpenLayers.Projection("EPSG:4326"); // Use datum WGS84
          map.addControl(mp);
	  
	  
          // Zoom to initial view of Indonesia	  
	  map.zoomToExtent(initial_boundary);                     
            

      }
        
    </script>
  </head>
  
"""


######## Local versions

header_template_local = """
<html xmlns="http://www.w3.org/1999/xhtml">
  <head>
  
    <link rel="stylesheet" href="/openlayers/theme/default/style.css" type="text/css" />
    
    <script src="/openlayers/lib/OpenLayers.js"></script>      
    
    
    <style type="text/css">
      body {margin: 1em;}
      #map {
        width: 98%%;
        height: 850px;
        border: 5px solid gray;
      }
      div.olControlMousePosition {
        color: white;
      }
    </style>


    <script type="text/javascript">

      function init(){
      
	  var options = {
	      // the "community" epsg code for spherical mercator
	      projection: "EPSG:900913",
	      // map horizontal units are meters
	      units: "m",
	      // this resolution displays the globe in one 256x256 pixel tile
	      maxResolution: 78271.51695,
	      // these are the bounds of the globe in sperical mercator
	      maxExtent: new OpenLayers.Bounds(-20037508, -20037508,
					       20037508, 20037508)
	  };
	    
	  // construct a map with the above options
	  map = new OpenLayers.Map("map", options);
          
          

"""
