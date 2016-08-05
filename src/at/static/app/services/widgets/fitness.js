app.factory('FitnessService', function($http) {

    return {
        getRecords: function () {
            return $http.get('/fitness/');
        },
        getRecord: function (id) {
            return $http.get('/fitness/' + id);
        },
        deleteRecord: function (id) {
            return $http.delete('/fitness/' + id);
        },
        processActivity: function (record) {
            var activity = {
                id: record.id,
                path: record.path,
                name: record.name,
                date: record.created,
                sport: 0,
                coords: [],
                heartRate: [],
                temperature: [],
                distance: 0,
                time: 0,
                avgSpeed: 0,
                calories: 0
            };

            for (j = 0; j < record.records.length; j++) {
                var item = jQuery.parseJSON(record.records[j]);

                // console.log(item);

                if (item.sport_sport == null)
                    continue;

                if (activity.sport == 0)
                    activity.sport = item.sport_sport;

                if (item.record_heart_rate_bpm == null ||
                    item.record_temperature_C == null)
                    continue;

                // if (activity.sport == 2) {
                    if (item.record_position_lat_semicircles == null ||
                        item.record_position_long_semicircles == null)
                        continue;

                    var lat = item.record_position_lat_semicircles * (180 / Math.pow(2, 31));
                    var lng = item.record_position_long_semicircles * (180 / Math.pow(2, 31));
                    activity.coords.push({lat: lat, lng: lng});
                // }

                activity.heartRate.push(item.record_heart_rate_bpm);
                activity.temperature.push(item.record_temperature_C);

                if (item.record_distance_m == null ||
                    item.session_total_elapsed_time_s == null ||
                    item.session_avg_speed_m_s == null ||
                    item.session_total_calories_kcal == null)
                    continue;

                if (activity.distance == 0)
                    activity.distance = parseFloat(item.record_distance_m / 1000).toFixed(2);

                if (activity.time == 0) {
                    var mm = item.session_total_elapsed_time_s / 60;
                    var ss = pad(((60 * (mm % 1)) + '').split('.')[0]);
                    mm = (mm + '').split('.')[0];
                    activity.time = mm + ':' + ss;
                }

                if (activity.avgSpeed == 0)
                    activity.avgSpeed = parseFloat(item.session_avg_speed_m_s * 3.6).toFixed(2);

                if (activity.calories == 0)
                    activity.calories = item.session_total_calories_kcal;
            }

            return activity;
        }
    };

    function pad(n) {
        return (n < 10) ? ("0" + n) : n;
    }
});