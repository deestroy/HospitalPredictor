// // convert address into latitude / longitude using Geocoding API
// function get_latlng(address) {
//     var geocoder = new google.maps.Geocoder();
//     geocoder.geocode({'address': address, 'region': 'CA'}, function(results, status) {
//         if (status == 'OK') {
//             return results[0].geometry.location;
//         }
//         alert('Geocoding failed due to the following reason: ' + status);
//     });
//     return null;
// }

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
        map_type_control_div.classList.remove('maptype-control-is-heat-map');
        map.setMapTypeId('hospital_data_map');
    };
    document.querySelector('.maptype-control-heat-map').onclick = function() {
        map_type_control_div.classList.remove('maptype-control-is-hospital-data');
        map_type_control_div.classList.add('maptype-control-is-heat-map');
        map.setMapTypeId('heat_map');
    };
    map.controls[google.maps.ControlPosition.LEFT_TOP].push(map_type_control_div);
}

// generate info box
function generate_info_bubble(hospital) {
        var info_bubble = new InfoBubble({
            content: generate_content_string(hospital.name, hospital.address, hospital.num_beds, hospital.occupancy),
            shadowStyle: 1,
            padding: 0,
            backgroundColor: 'white',
            borderRadius: 4,
            arrowSize: 10,
            borderWidth: 1,
            shadowStyle: 1,
            disableAutoPan: false,
            hideCloseButton: true,
            arrowPosition: 30,
            backgroundClassName: 'ib',
            arrowStyle: 0,
            arrowPosition: 20,
            maxHeight: 500,
            maxWidth: 250
    });
    return info_bubble;
}

// generate content string for infobox
function generate_content_string(name, address, num_beds, occupancy) {
    return '<div class="ib-container">' +
            '<div class="ib-title">' + name + '</div>' +
            '<hr style="border:1px dashed #ec3716">' +
            '<table class="ib-content" cellpadding="5">' +
                '<tr>' +
                    '<td valign="middle"><img width="20" height="20" src="../static/img/location.png"/></td>' +
                    '<td valign="middle">' + address + '</td>' +
                '</tr>' +
                '<tr>' +
                    '<td valign="middle"><img width="30" height="30" src="../static/img/hospital_bed.png"/></td>' +
                    '<td valign="middle">' + num_beds + ' beds</td>' +
                '</tr>' +
                '<tr>' +
                    '<td valign="middle"><img width="30" height="30" src="../static/img/percentage_pie.png"/></td>' +
                    '<td valign="middle">' + occupancy + '% occupancy</td>' +
                '</tr>' +
            '</table>' +
        '</div>'
}    