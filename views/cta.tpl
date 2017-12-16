<!doctype html>
<html>
<head>
    <style type="text/css">
        html { height: 100% }
        body { height: 100%; margin: 0; padding: 0 }
        #map_canvas { width: 800px; height: 100%; float: left; position: fixed !important; left: 320px;}
        #nav { width: 300px; float: left; margin-right: 20px;}
    </style>
</head>
<body>
<div id="nav">
    <form id="stop-search">
        <input id="stop" type="text" value="">
        <input id="submit" type="submit" value="Search">
    </form>
    <div id="stops"></div>
    <div id="routes">
    <ul>
    %for route in routes:
        <li><a href="#" class="route" data-route="{{route['id']}}" data-direction="{{route['direction']}}">{{route['id']}}: {{route['name']}} ({{route['direction']}})</a></li>
    %end
    <ul>
    </div>
</div>
<div id="map_canvas"></div>

</body>
<script src="//ajax.googleapis.com/ajax/libs/jquery/1.8.3/jquery.min.js"></script>
<script type="text/javascript"
  src="https://maps.googleapis.com/maps/api/js?key=AIzaSyB79jK3E993RsyAm5By3rwJEo82U9omAx0&sensor=false">
</script>
<script type="text/javascript">
    var map = {},
        polylines = [],
        colors = ['black','magenta','green','white'],
        weights = [4,2,1];

    function initialize() {
        var mapOptions = {
              center: new google.maps.LatLng(41.850, -87.650),
              zoom: 13,
              mapTypeId: google.maps.MapTypeId.ROADMAP
        };

        map = new google.maps.Map(document.getElementById("map_canvas"), mapOptions);
    }

    function generatePath(coords) {
        var path = [];

        for (var i = 0; i < coords.length; i++) {
            path[i] = new google.maps.LatLng(coords[i].latitude, coords[i].longitude);
        }

        return path;
    }
</script>
<script>
$(document).ready(function() {
    initialize();
    $('#stop-search').on('submit', function() {
        var stopId = $('#stop').val();

        $.ajax({
            url: '/routes/stop/' + stopId,
            cache: false,
            type: 'GET',
            success: function(results) {
                var $stops = $('#stops');

                $stops.empty();

                if (results) {
                    if (results.routes.length === 0) {
                        $stops.append('No routes available for this stop.');
                    } else {
                        var routesHtml = '<ul>';
                        $stops.append('<h2>' + results.stopId + ': ' + results.stopName + '</h2>');

                        for (var i = 0; i < results.routes.length; i++) {
                            var routeId = results.routes[i].id,
                                direction = results.routes[i].direction;

                            routesHtml += '<li><a href="#" class="route" data-route="' + routeId + '" data-direction="' + direction + '">' + results.routes[i].id + ': ' + results.routes[i].name + ' - ' + results.routes[i].direction + '</a></li>';
                        }

                        routesHtml += '</ul>';

                        $stops.append(routesHtml);
                    }
                }
            }
        });

        return false;
    });


    var $route = $();
    $('#stops, #routes').on('click', 'a.route', function() {
        var routeId = $(this).data('route'),
            direction = $(this).data('direction');

        $route.css('font-weight', 'normal');
        $route = $(this);

        $.ajax({
            url: '/patterns/route/' + routeId + '/direction/' + direction,
            cache: false,
            type: 'GET',
            success: function(results) {
                $route.css('font-weight', 'bold');
                var centerPoint = results.patterns[0].pattern[Math.floor(results.patterns[0].pattern.length / 2)];
                map.panTo(new google.maps.LatLng(centerPoint.latitude, centerPoint.longitude));
                
                // clear all polylines
                for (var i = 0; i < polylines.length; i++) {
                    polylines[i].setPath([]);
                }
                polylines = [];

                for (var i = 0; i < results.patterns.length; i++) {
                    var path = generatePath(results.patterns[i].pattern);
                    var poly = new google.maps.Polyline({ map: map, path: path, strokeColor: colors[i], strokeWeight: weights[i] });

                    polylines.push(poly);
                }
            }
        });

        return false;
    });
});
</script>
</html>