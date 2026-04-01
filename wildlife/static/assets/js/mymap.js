let myLayer;
let map; 

var parks;
var parkIcon ;
var overlays ;
var layerControl ;
//get country codes from countryBorders.geo.json
//getCountryNamesAndCodes();

//get country codes and names from getCountryCode.json and add to drop down selector
function getCountryNamesAndCodes() {
  $.ajax({
    url: "assets/php/getCountry.php?",
    type: "GET",
    success: function (countries) {
      let option = "";
      for (let country of countries) {
        option += '<option value="' + country[1] + '">' + country[0] + "</option>";
      }
      $("#countrySelect").append(option);
    },
  });
}

getCurrentMapLocation();
//get user's coordinates using geolocation
function getCurrentMapLocation() {
  if (navigator.geolocation) {
    // Geolocation is available in this browser

    // Define a success callback function
    function successCallback(position) {
      const latitude = position.coords.latitude;
      const longitude = position.coords.longitude;

      // Do something with the latitude and longitude values
      console.log(`Latitude: ${latitude}, Longitude: ${longitude}`);
      //get more information about current location
     //getCurrentLocationDetails(latitude, longitude);

      initializeMap(latitude,longitude,"ZA");
    }

    // Define an error callback function
    function errorCallback(error) {
      switch (error.code) {
        case error.PERMISSION_DENIED:
          console.error("User denied the request for geolocation.");
          break;
        case error.POSITION_UNAVAILABLE:
          console.error("Location information is unavailable.");
          break;
        case error.TIMEOUT:
          console.error("The request to get user location timed out.");
          break;
        case error.UNKNOWN_ERROR:
          console.error("An unknown error occurred.");
          break;
      }
    }

    // Request the user's current location
    navigator.geolocation.getCurrentPosition(successCallback, errorCallback);
  } else {
    // Geolocation is not available in this browser
    console.error("Geolocation is not supported in this browser.");
  }
};
//get country code from from lat lon and intialise map
// function getCurrentLocationDetails(latitude, longitude) {
//   userLatitude = latitude;
//   userLongitude = longitude;

//   $.ajax({
//     url: "assets/php/getCountryPositionCodeFromLatlon.php",
//     data: {
//       lat: userLatitude,
//       lng: userLongitude,
//       username: "skwembeproff",
//     },
//     type: "GET",
//     success: function (jsonObject) {
//       console.log("Current Geo Location :", jsonObject);
//       countryCode = jsonObject.countryCode;
//       console.log(countryCode);
      
//       initializeMap(userLatitude,userLongitude,countryCode);
      
//     },
//   });
// };

//initialize map , layers and markers 
function initializeMap(userLatitude,userLongitude,countryCode) {
  var streets = L.tileLayer(
    "https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}",
    {
      attribution:
        "Tiles &copy; Esri &mdash; Source: Esri, DeLorme, NAVTEQ, USGS, Intermap, iPC, NRCAN, Esri Japan, METI, Esri China (Hong Kong), Esri (Thailand), TomTom, 2012"
    }
  );
  var satellite = L.tileLayer(
    "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    {
      attribution:
        "Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community"
    }
  );

  //declare base maps with the tile variables 
  var basemaps = {
    "Streets": streets,
    "Satellite": satellite
  };

  
//initialise map
  map= L.map("map", {
    layers: [streets]
  }).setView([userLatitude, userLongitude], 6);

  myLayer = new L.geoJson().addTo(map);

  //add border polygon
  getBorder(countryCode);

  //add easy buttons
  L.easyButton("fa-info", function (btn, map) {
    $("#exampleModal").modal("show");
  }).addTo(map);

parks = L.markerClusterGroup({
    polygonOptions: {
      fillColor: '#fff',
      color: '#000',
      weight: 2,
      opacity: 1,
      fillOpacity: 0.5
    }}).addTo(map);

safari = L.markerClusterGroup({
      polygonOptions: {
        fillColor: '#fff',
        color: '#000',
        weight: 2,
        opacity: 1,
        fillOpacity: 0.5
      }}).addTo(map);
  
    
 overlays = {
"Parks": parks,
"Safari":safari
};

layerControl = L.control.layers(basemaps, overlays).addTo(map);

const customParkIconUrl = 'parks_logo.PNG';  // Replace with the actual path or URL of your custom image

 parkIcon = L.icon({
  iconUrl: "/static/assets/js/parks_logo.PNG",
  iconSize: [32, 32], // size of the icon
});


/* safariIcon = L.ExtraMarkers.icon({
  prefix: 'fa',
  icon: 'fa-heart',
  iconColor: 'black',
  markerColor: 'white',
  shape: 'square'
}); */

safariIcon = L.ExtraMarkers.icon({
  prefix: 'fa',
  icon: 'fa-exclamation-circle',  // Use the FontAwesome icon for an exclamation mark inside a circle
  iconColor: 'red',  // Set the icon color to red for warning
  markerColor: 'white',  // Set the marker color to white
  shape: 'circle',  // Use a circle shape
  extraClasses: 'fas',  // Use 'fas' class for solid FontAwesome icons
  number: '',  // Remove any number overlay
});
                   
getNationalParks();
getSafari();

}


//handle onchange event
$('#countrySelect').change(function () {

  var countryCode = $(this).val(); // Get the selected value
  console.log('Selected country code: ' + countryCode);
  
  // Use the country code to select the corresponding option and retrieve its text
  var countryName = $("#countrySelect option[value='" + countryCode + "']").text();
  console.log("Selected country name is:", countryName);

  //get coordinates using open cage and full country name
  getSelectedCountryCoords(countryName, countryCode);

  

});

//get coordinates using open cage and full country name
function getSelectedCountryCoords(countryName, countryCode){
  $.ajax({
    url: "assets/php/getCountryCoords.php",
    data: {
      countryName:countryName,
    },
    type: "GET",
    success: function (result) {
      console.log("country coordinates")
      console.log(result);

      //make the mai api calls
      //+udating map focus
      updateMapView(result.data.lat, result.data.lng,countryCode)
      //+get country info
      getCountryInfo(countryCode)

    },
  });

};

function getCountryInfo(countryCode){
  //make ajax call to get getcountryInfo.php
		$.ajax({
			url: "assets/php/getCountryInfo.php",
			type: 'POST',
			dataType: 'json',
			data: {
				countryCode: countryCode,
			},
			success: function(result) {

				console.log(JSON.stringify(result));

				if (result.status.name == "ok") {
          //linking the results with , appropriate modal IDs in the HTML File
					$('#continent').html(result['data'][0]['continent']);
					$('#capital').html(result['data'][0]['capital']);
					$('#languages').html(result['data'][0]['languages']);
					$('#geonameId').html(result['data'][0]['geonameId']);
				
				}
			
			},
			error: function(jqXHR, textStatus, errorThrown) {
				// your error code
			}
		}); 

}

// Function to update map view based on new coordinates
function updateMapView(latitude, longitude,countryCode ) {

  map.setView([latitude, longitude], 6);
    //add border polygon
    getBorder(countryCode);

}

//display border
function getBorder(countryCode="ZA") {
 
  $.ajax({
    url: `/get_border/?countryCode=${countryCode}`,
    type: "GET",
    data: {
      
    },
    success: function (polygon) {
      
      console.log(polygon);
      // Clear existing layers if needed (optional)
      myLayer.clearLayers();

      // Add the new polygon data and set its style
      myLayer.addData(polygon).setStyle(polyStyle);

      // Fit the map to the bounds of the polygon
      const bounds = myLayer.getBounds();
      map.fitBounds(bounds);

      // Optionally, you can extract the bounding coordinates
      const north = bounds.getNorth();
      const south = bounds.getSouth();
      const east = bounds.getEast();
      const west = bounds.getWest();
    }
  });
};

function polyStyle() {
  return {
    "color": "green",  // Change the color to green
    "weight": 5,
    "opacity": 1.0,
    "fillColor": "#c2e1c2",  // Change the fillColor to a green shade
    "fillOpacity": 0.45
  };
}
function getNationalParks(){
  
//make ajax call to get getNationalParks.php
$.ajax({
  url: "/get_national_parks/",
  type: 'GET',
  dataType: 'json',
  data: {
   // countryCode: countryCode,
  },
  success: function(result) {
    console.log("---getting national parks----")
    //console.log(JSON.stringify(result));
    result.data.forEach(location => {
      const name = location.name;
      const latitude = location.geometry.location.lat;
      const longitude = location.geometry.location.lng;
      console.log(`Location: ${name}, Coordinates: (${latitude}, ${longitude})`);
      

      L.marker([location.geometry.location.lat, location.geometry.location.lng], {icon: parkIcon})
      .bindTooltip(location.name, {direction: 'top', sticky: true})
      .addTo(parks);

      /*
      const northeast = location.geometry.viewport.northeast;
      const southwest = location.geometry.viewport.southwest;
      // Constructing the polygonCoordinates array
      const polygonCoordinates = [
        [northeast.lat, southwest.lng], // Top right (northeast)
        [northeast.lat, northeast.lng], // Top left (northeast)
        [southwest.lat, northeast.lng], // Bottom left (southwest)
        [southwest.lat, southwest.lng]  // Bottom right (southwest)
      ];
      console.log(polygonCoordinates)
      const polygon = L.polygon(polygonCoordinates, {
        color: 'red',
        fillColor: 'red',
        fillOpacity: 0.4
      }).addTo(map);
      */
    }); 
  
  },
  error: function(jqXHR, textStatus, errorThrown) {
    // your error code
  }
}); 

}
function getSafari(){
  
  //make ajax call to get getNationalParks.php
  $.ajax({
    url: "/get_places/",
    type: 'GET',
    dataType: 'json',
    data: {
     // countryCode: countryCode,
    },
    success: function(result) {
      console.log("---getting safari----")
      console.log(JSON.stringify(result));
      result.data.forEach(location => {
        const name = location.name;
        const latitude = location.geometry.location.lat;
        const longitude = location.geometry.location.lng;
        console.log(`Location: ${name}, Coordinates: (${latitude}, ${longitude})`);
        
  
        L.marker([location.geometry.location.lat+ 0.0001, location.geometry.location.lng-0.0001], {icon: safariIcon})
        .bindTooltip("Incident! "+location.name, {direction: 'top', sticky: true})
        .addTo(safari);
  
        /*
        const northeast = location.geometry.viewport.northeast;
        const southwest = location.geometry.viewport.southwest;
        // Constructing the polygonCoordinates array
        const polygonCoordinates = [
          [northeast.lat, southwest.lng], // Top right (northeast)
          [northeast.lat, northeast.lng], // Top left (northeast)
          [southwest.lat, northeast.lng], // Bottom left (southwest)
          [southwest.lat, southwest.lng]  // Bottom right (southwest)
        ];
        console.log(polygonCoordinates)
        const polygon = L.polygon(polygonCoordinates, {
          color: 'red',
          fillColor: 'red',
          fillOpacity: 0.4
        }).addTo(map);
        */
      }); 
    
    },
    error: function(jqXHR, textStatus, errorThrown) {
      // your error code
    }
  }); 
  
  }
  
