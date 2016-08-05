app.controller("ContainerController", function($scope, $route, ContainerService) {

    $scope.containers = [];
    $scope.indices = [];
    ContainerService.getContainers()
        .success(function (data) {
            $scope.containers = data;
            $scope.index();
        })
        .error(function (data) {

        });

    $scope.deleteContainer = function (id) {
        var index = $scope.indices[id];
        var entry = $scope.containers[index];
        $scope.containers.splice(index, 1);
        ContainerService.deleteContainer(id)
            .success(function (data) {
                // TODO: notify user
                $scope.index();
            })
            .error(function (data) {
                $scope.containers.push(entry);
                $scope.index();
            });
    };

    $scope.index = function () {
        for (var i=0; i < $scope.containers.length; i++)
            $scope.indices[$scope.containers[i].id] = i;
    };

});