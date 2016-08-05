app.controller("FitnessListController", function($scope, $controller, FitnessService) {
    $controller('WidgetController', { $scope: $scope });

    $scope.records = [];
    $scope.records.indices = [];
    FitnessService.getRecords()
        .success(function (data) {
            $scope.records = data;
            $scope.index();
        })
        .error(function (data) {
            console.log("An error occurred while trying to retrieve data.");
        });

    $scope.deleteRecord = function (id) {
        var record = $scope.records[$scope.records.indices[id]];
        $scope.records.splice($scope.records.indices[id], 1);
        $scope.index();
        FitnessService.deleteRecord(id)
            .success(function (data) {
                // TODO: notify user
            })
            .error(function (record) {
                return function (data) {
                    $scope.records.push(record);
                    $scope.index();
                };
            }(record));
    };

    $scope.index = function () {
        $scope.records.indices = [];
        for (var i=0; i < $scope.records.length; i++)
            $scope.records.indices[$scope.records[i].id] = i;
    };

});