var map;
var hospital_marker_icon;
var heatmap;
var heatmap2;
var hospital_data_and_markers
var curr_info_bubble;
var curr_marker;

// callback function to google maps api call
function init_map() {

    map = create_map();
    map.setClickableIcons(false);
    heatmap = create_heatmap_layer(map);
    heatmap2 = create_heatmap2_layer(map);
    curr_info_bubble = null;
    curr_marker = null;

    // search box
    var input = document.getElementById('pac-input');
    var search_box = new google.maps.places.SearchBox(input);
    map.controls[google.maps.ControlPosition.TOP_RIGHT].push(document.getElementById('search_box'));

    // bias search box results towards current map's viewport
    map.addListener('bounds_changed', function() {
        search_box.setBounds(map.getBounds());
    });

    search_box.addListener('places_changed', function() {
        var places = search_box.getPlaces();
        if (places.length == 0)
            return;

        var bounds = new google.maps.LatLngBounds();
        places.forEach(function(place) {
            if (!place.geometry) {
                console.log("Returned place contains no geometry");
                return;
            }
            // only geocodes have viewport
            if (place.geometry.viewport)
                bounds.union(place.geometry.viewport);
            else
                bounds.extend(place.geometry.location);
        });
        map.fitBounds(bounds);
    });

    // hospital marker icon
    hospital_marker_icon = {
        url: "../static/img/hospital_marker.png",
        scaledSize: new google.maps.Size(50, 50)
    };

    // bundle hospital data with markers and info bubbles
    // currently it is not necessary to store this data, but it may be useful later
    hospital_data_and_markers = []; // array of dicts
    var locations = [];
    var cases_points = []

    $.get("/get-hospital-data", function(response) {
        var data = JSON.parse(response);   
        var hospitals = data['hospitals']
        var cases = data['canada_cases']
        
        // hospital data
        for (i = 0; i < hospitals.length; ++i) {

            let hospital = hospitals[i];
            let location = new google.maps.LatLng(hospital.lat, hospital.lng);

            // marker and info_bubble
            let marker = generate_marker(location);
            let info_bubble = generate_info_bubble(hospital);

            // marker event listeners
            marker.addListener('click', function() {
                if (info_bubble.isOpen_) {
                    info_bubble.close();
                    curr_info_bubble = null;
                    curr_marker = null;
                }
                else {
                    info_bubble.open(map, marker);
                    if (curr_info_bubble)
                        curr_info_bubble.close();
                    curr_info_bubble = info_bubble;
                    curr_marker = marker;
                }
            });

            // put everything in a dict
            let dict = {
                'hospital': hospital,
                'marker': marker,
                'infobubble': info_bubble
            };
            hospital_data_and_markers.push(dict);

            // update heatmap data
            locations.push({location: location, weight: hospital.percent_occupancy / hospital.num_beds});
        }
        heatmap.setData(locations);

        // cases data
        for (i = 0; i < cases.length; ++i)
            cases_points.push({location: new google.maps.LatLng(cases[i][0], cases[i][1])});
        heatmap2.setData(cases_points);
    });
}

// make Geocoding API call
// var geocoder = new google.maps.Geocoder();
// geocoder.geocode({'address': hospital.address + ' ' + hospital.city, 'region': 'CA'}, function(results, status) {
//     if (status == 'OK') {
//         // latlng = results[0].geometry.location);
//     }
//     else 
//         alert('Geocoding failed due to the following reason: ' + status);
// });

// heatmap layer
function create_heatmap_layer(map) {
    return new google.maps.visualization.HeatmapLayer({
        data: [],
        map: map,
        radius: 30,
        gradient: [
            'rgba(235, 217, 52, 0)',
            'rgba(235, 217, 52, 1)',
            'rgba(235, 189, 52, 1)',
            'rgba(235, 189, 52, 1)',
            'rgba(235, 147, 52, 1)',
            'rgba(235, 147, 52, 1)',
            'rgba(235, 104, 52, 1)',
            'rgba(235, 104, 52, 1)',
            'rgba(235, 104, 52, 1)',
            'rgba(235, 104, 52, 1)',
            'rgba(235, 64, 52, 1)',
            'rgba(235, 64, 52, 1)',
            'rgba(235, 64, 52, 1)',
            'rgba(235, 64, 52, 1)'
          ]
    });
}

// heatmap2 layer
function create_heatmap2_layer(map) {
    return new google.maps.visualization.HeatmapLayer({
        data: [],
        map: map,
        radius: 30,
        gradient: [
            'rgba(252, 174, 174, 0)',
            'rgba(252, 174, 174, 1)',
            'rgba(252, 174, 174, 1)',
            'rgba(250, 145, 145, 1)',
            'rgba(250, 145, 145, 1)',
            'rgba(250, 145, 145, 1)',
            'rgba(247, 116, 116, 1)',
            'rgba(247, 116, 116, 1)',
            'rgba(247, 116, 116, 1)',
            'rgba(247, 116, 116, 1)',
            'rgba(255, 102, 102, 1)',
            'rgba(255, 102, 102, 1)',
            'rgba(255, 102, 102, 1)',
            'rgba(255, 102, 102, 1)'
          ]
    });
}

// button toggle functions

function toggleHeatmap() {
    heatmap.setMap(heatmap.getMap() ? null : map);
}

function toggleHeatmap2() {
    heatmap2.setMap(heatmap2.getMap() ? null : map);
}

function toggleMarkers() {
    if (curr_info_bubble) {
        if (hospital_data_and_markers[0]['marker'].getVisible())
            curr_info_bubble.close();
        else
            curr_info_bubble.open(map, curr_marker);
    }
    for (i = 0; i < hospital_data_and_markers.length; ++i)
        hospital_data_and_markers[i]['marker'].setVisible(!hospital_data_and_markers[i]['marker'].getVisible());
}

// create map
function create_map() {

    // arbitrary location for map center
    var map_center = {lat: 45.401056, lng: -75.651306};

    // create map
    var map = new google.maps.Map(document.getElementById('map'), {
        center: map_center,
        zoom: 15,
        disableDefaultUI: true
    });

    // set up styled map types
    map.mapTypes.set('hospital_data_map', get_hospital_data_map_type());
    map.setMapTypeId('hospital_data_map');
    
    // init controls
    init_zoom_control(map);
    init_toggle_control(map);

    return map;
}

// get hospital data map type (styled map)
function get_hospital_data_map_type() {
    return new google.maps.StyledMapType(
        [
            {elementType: 'geometry', stylers: [{color: '#e7f0d3'}]},
            {elementType: 'labels.text.stroke', stylers: [{color: '#f2f3f5'}]},
            {elementType: 'labels.text.fill', stylers: [{color: '#f2ae29'}]},
            {
                featureType: 'road',
                elementType: 'geometry',
                stylers: [{color: '#f7f8fa'}]
            },
            {
                featureType: 'road',
                elementType: 'geometry.stroke',
                stylers: [{color: '#ebeef2'}]
            },
            {
                featureType: 'road',
                elementType: 'labels.text.fill',
                stylers: [{color: '#b3b7bd'}]
            },
            {
                featureType: 'road.highway',
                elementType: 'geometry',
                stylers: [{color: '#f0e5a8'}]
            },
            {
                featureType: 'road.highway',
                elementType: 'geometry.stroke',
                stylers: [{color: '#f5da82'}]
            },
            {
                featureType: 'road.highway',
                elementType: 'labels.text.fill',
                stylers: [{color: '#917c5c'}]
            },
            {
                featureType: 'water',
                elementType: 'geometry',
                stylers: [{color: '#afcdfa'}]
            },
            {
                featureType: 'water',
                elementType: 'labels.text.fill',
                stylers: [{color: '#395580'}]
            },
            {
                featureType: 'water',
                elementType: 'labels.text.stroke',
                stylers: [{color: '#22467a'}]
            },

            // hide unecessary features
            {
                featureType: 'poi',
                stylers: [{visibility: 'off'}]
            },
            {
                featureType: 'transit',
                stylers: [{visibility: 'off'}]
            }
        ],
        {name: 'Hospital Data'}
    );
}

// initialize zoom controls
function init_zoom_control(map) {
    document.querySelector('.zoom-control-in').onclick = function() {
        map.setZoom(map.getZoom() + 1);
    };
    document.querySelector('.zoom-control-out').onclick = function() {
        map.setZoom(map.getZoom() - 1);
    };
    map.controls[google.maps.ControlPosition.RIGHT_BOTTOM].push(
        document.querySelector('.zoom-control'));
}

// initialize toggle controls
function init_toggle_control(map) {
    map.controls[google.maps.ControlPosition.LEFT_TOP].push(document.querySelector('.toggle-control'));
}

// generate info bubble
function generate_info_bubble(hospital) {
    return info_bubble = new InfoBubble({
        content: generate_content_string(hospital),
        shadowStyle: 1,
        padding: 0,
        backgroundColor: 'white',
        borderRadius: 4,
        arrowSize: 10,
        borderWidth: 1,
        shadowStyle: 1,
        disableAutoPan: true,
        hideCloseButton: true,
        arrowPosition: 30,
        backgroundClassName: 'ib',
        arrowStyle: 0,
        arrowPosition: 20,
        maxHeight: 200,
        maxWidth: 300,
        minWidth: 300,
        minHeight: 200
    });
}

// generate content string for infobox
function generate_content_string(hospital) {
    return '<div class="ib-container">' +
                '<div class="ib-title">' + hospital.name + '</div>' +
                '<hr style="border:1px dashed #ec3716">' +
                '<table class="ib-content" cellpadding="5">' +
                    '<tr>' +
                        '<td><div align="center"><img width="20" height="20" src="../static/img/location.png"/></div></td>' +
                        '<td style="padding:3px 3px 3px 3px">' + hospital.address + ', ' + hospital.city + '<br/>' + hospital.province + ' ' + hospital.postal_code + '</td>' +
                    '</tr>' +
                    '<tr>' +
                        '<td><div align="center"><img width="30" height="30" src="../static/img/hospital_bed.png"/></div></td>' +
                        '<td style="padding:3px 3px 3px 3px">' + hospital.num_beds + ' beds</td>' +
                    '</tr>' +
                    '<tr>' +
                        '<td><div align="center"><img width="30" height="30" src="../static/img/percentage_pie.png"/></div></td>' +
                        '<td style="padding:3px 3px 3px 3px">' + hospital.percent_occupancy + '% occupancy</td>' +
                    '</tr>' +
                '</table>' +
            '</div>'
}    

// generate map marker
function generate_marker(position) {
    return new google.maps.Marker({
        position: position,
        icon: hospital_marker_icon,
        map: map,
        animation: google.maps.Animation.DROP
    });
}