app.controller("FitnessController", function($scope, $controller, FitnessService, FileService) {
    $controller('WidgetController', { $scope: $scope });

    $scope.activities = [];
    $scope.resolution = 150;
    $scope.chartHeight = '150';
    $scope.currentRecord = 0;
    $scope.activityDateTime = '';

    FitnessService.getRecords().success(function (data) {
        $scope.recordsLength = data.length;
        for (var i=0; i < data.length; i++)
            FitnessService.getRecord(data[i].id).success(function (data) {
                $scope.activities.push(FitnessService.processActivity(data));
                checkDone();
        });
    });

    function checkDone() {
        if ($scope.activities.length == $scope.recordsLength) {
            if ($scope.activities.length > 0) {
                $scope.visualizeActivity(0);
                $scope.recordName = $scope.activities[0].name;
                $scope.recordDate = $scope.activities[0].date;
                $scope.currentRecord = 0;
                $scope.activityDateTime = $scope.activities[0].activityDateTime;
            }
        }

         //console.log($scope.activities);
    }

    $scope.visualizeActivity = function(i) {
        $scope.body = $('#fitness-widget' + $scope.id + ' .record-details');
        $scope.body.empty();

        if ($scope.activities[i].coords.length > 0)
            initMap(i);

        initChart(i, 'Heart Rate', 'heartrate', 'heartRate', '#ff2653', '#d92145', '#bf1d3d');
        initChart(i, 'Temperature', 'temperature', 'temperature', '#35b6f0', '#2d9acc', '#2a90bf');
    };

    $scope.toogle = function (toogle) {
        if ($scope.currentRecord + toogle == $scope.recordsLength-1)
            $('#' + $scope.id + '-next-btn').prop('disabled', true);
        if ($scope.currentRecord + toogle == 0)
            $('#' + $scope.id + '-prev-btn').prop('disabled', true);
        if ($scope.currentRecord + toogle > 0)
            $('#' + $scope.id + '-prev-btn').prop('disabled', false);
        if ($scope.currentRecord + toogle < $scope.recordsLength-1)
            $('#' + $scope.id + '-next-btn').prop('disabled', false);

        $scope.currentRecord = $scope.currentRecord + toogle;
        $scope.recordName = $scope.activities[$scope.currentRecord].name;
        $scope.recordDate = $scope.activities[$scope.currentRecord].date;
        $scope.visualizeActivity($scope.currentRecord);
        $scope.activityDateTime = $scope.activities[$scope.currentRecord].activityDateTime;

    };

    function initMap(i) {
        var heading = document.createElement('h4');
        heading.innerHTML = 'Map';
        $scope.body.append(heading);

        var mapContainer = document.createElement('div');
        mapContainer.id = 'widget' + $scope.id + '-map' + i;
        mapContainer.style.width = '100%';
        mapContainer.style.height = '250px';
        $scope.body.append(mapContainer);

        var map = L.map('widget' + $scope.id + '-map' + i);
        var osmUrl='http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';
        var osmAttrib='Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors';
        var osm = new L.TileLayer(osmUrl, { minZoom: 2, maxZoom: 22, attribution: osmAttrib });

        var lat = ($scope.activities[i].coords[0].lat + $scope.activities[i].coords[$scope.activities[i].coords.length-1].lat) / 2;
        var lng = ($scope.activities[i].coords[0].lng + $scope.activities[i].coords[$scope.activities[i].coords.length-1].lng) / 2;

        map.setView([lat, lng], 14);
        map.addLayer(osm);

        var polyline = L.polyline($scope.activities[i].coords, { color: 'red' }).addTo(map);
        var start = L.marker($scope.activities[i].coords[0]).addTo(map);
        var end = L.marker($scope.activities[i].coords[$scope.activities[i].coords.length-1]).addTo(map);
    }

    function initChart(i, title, slug, propertyName, fillColor, pointColor, pointHighlightColor) {
        var heading = document.createElement('h4');
        heading.innerHTML = title;
        $scope.body.append(heading);

        var canvasContainer = document.createElement('canvas');
        canvasContainer.id = 'widget' + $scope.id + '-' + slug + '-chart' + i;
        canvasContainer.width = $('.box-body:first').width() - 17;
        canvasContainer.height = $scope.chartHeight;
        $scope.body.append(canvasContainer);

        var labels = [];
        for (var x=0; x < $scope.activities[i][propertyName].length; x++)
            if (x % $scope.resolution == 0)
                labels.push(x);

        var data = [];
        for (var x=0; x < $scope.activities[i][propertyName].length; x++)
            if (x % $scope.resolution == 0)
                data.push($scope.activities[i][propertyName][x]);

        var data = {
            labels: labels,
            datasets: [
                {
                    label: title,
                    fillColor: fillColor,
                    strokeColor: fillColor,

                    pointColor: pointColor,
                    pointStrokeColor: pointColor,

                    pointHighlightFill: pointHighlightColor,
                    pointHighlightStroke: pointHighlightColor,
                    data: data
                }
            ]
        };

        var ctx = document.getElementById('widget' + $scope.id + '-' + slug + '-chart' + i).getContext("2d");
        var line = new Chart(ctx).Line(data, {});
    }

    $scope.share = function () {
        FileService.shareData([$scope.activities[$scope.currentRecord].path]);
    }

});