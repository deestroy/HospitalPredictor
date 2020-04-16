var map;
var hospital_marker_icon;
var heatmap;

// callback function to google maps api call
function init_map() {

    map = create_map();
    heatmap = create_heatmap_layer(map);

    // hospital marker icon
    hospital_marker_icon = {
        url: "../static/img/hospital_marker.png",
        scaledSize: new google.maps.Size(50, 50)
    };

    // bundle hospital data with markers and info bubbles
    // currently it is not necessary to store this data, but it may be useful later
    var hospital_data_and_markers = []; // array of dicts
    var locations = [];

    $.get("/get-hospital-data", function(response) {
        var data = JSON.parse(response);   

        for (i = 0; i < data.length; i++) {

            let hospital = data[i];

            // make Geocoding API call
            var geocoder = new google.maps.Geocoder();
            geocoder.geocode({'address': hospital.address + ' ' + hospital.city, 'region': 'CA'}, function(results, status) {
                if (status == 'OK') {
                    
                    // marker and info_bubble
                    let marker = generate_marker(results[0].geometry.location);
                    let info_bubble = generate_info_bubble(hospital);

                    // marker event listeners
                    marker.addListener('mouseover', function() {
                        info_bubble.open(map, marker);
                    });
                    marker.addListener('mouseout', function() {
                        info_bubble.close();
                    });

                    // put everything in a dict
                    let dict = {
                        'hospital': hospital,
                        'marker': marker,
                        'infobubble': info_bubble
                    };
                    hospital_data_and_markers.push(dict);

                    // update heatmap data
                    locations.push({location: results[0].geometry.location, weight: hospital.occupancy * hospital.num_beds});
                    heatmap.setData(locations);
                }
                else 
                    alert('Geocoding failed due to the following reason: ' + status);
            });
        }
    });
}

// heatmap layer
function create_heatmap_layer(map) {
    return new google.maps.visualization.HeatmapLayer({
        data: [],
        map: map,
        radius: 20,
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

function toggleHeatmap() {
    heatmap.setMap(heatmap.getMap() ? null : map);
}

// create map
function create_map() {

    // arbitrary location for map center
    var map_center = {lat: 45.401056, lng: -75.651306};

    // create map
    var map = new google.maps.Map(document.getElementById('map'), {
        center: map_center,
        zoom: 15,
        mapTypeControlOptions: {
            mapTypeIds: ['map_type_2', 'hospital_data_map']
        },
        disableDefaultUI: true
    });

    // set up styled map types
    map.mapTypes.set('hospital_data_map', get_hospital_data_map_type());
    map.setMapTypeId('hospital_data_map');
    
    // init controls
    init_zoom_control(map);
    init_map_type_control(map);

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

// initialize map type controls
function init_map_type_control(map) {
    var map_type_control_div = document.querySelector('.maptype-control');
    document.querySelector('.maptype-control-hospital-data').onclick = function() {
        map_type_control_div.classList.add('maptype-control-is-hospital-data');
        map_type_control_div.classList.remove('maptype-control-is-map-type-2');
        map.setMapTypeId('hospital_data_map');
    };
    document.querySelector('.maptype-control-map-type-2').onclick = function() {
        map_type_control_div.classList.remove('maptype-control-is-hospital-data');
        map_type_control_div.classList.add('maptype-control-is-map-type-2');
        map.setMapTypeId('map_type_2');
    };
    map.controls[google.maps.ControlPosition.LEFT_TOP].push(map_type_control_div);
    map.controls[google.maps.ControlPosition.TOP_CENTER].push(document.querySelector('#btn-heatmap-toggle'));
}

// generate info box
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
        maxHeight: 500,
        maxWidth: 250
    });
}

// generate content string for infobox
function generate_content_string(hospital) {
    return '<div class="ib-container">' +
                '<div class="ib-title">' + hospital.name + '</div>' +
                '<hr style="border:1px dashed #ec3716">' +
                '<table class="ib-content" cellpadding="5">' +
                    '<tr>' +
                        '<td valign="middle"><img width="20" height="20" src="../static/img/location.png"/></td>' +
                        '<td valign="middle">' + hospital.address + '</td>' +
                    '</tr>' +
                    '<tr>' +
                        '<td valign="middle"><img width="30" height="30" src="../static/img/hospital_bed.png"/></td>' +
                        '<td valign="middle">' + hospital.num_beds + ' beds</td>' +
                    '</tr>' +
                    '<tr>' +
                        '<td valign="middle"><img width="30" height="30" src="../static/img/percentage_pie.png"/></td>' +
                        '<td valign="middle">' + hospital.occupancy + '% occupancy</td>' +
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