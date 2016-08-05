app.controller("GalleryController", function($scope, $controller, FileService) {
    $controller('WidgetController', {$scope: $scope});

    $scope.images = [];
    FileService.listFiles($scope.params)
        .success(function (data) {
            for (var i=0; i < data.length; i++) {
                FileService.getFile({ path: $scope.params.path + data[i] })
                    .success(function (data) {
                        $scope.images.push(data);
                    })
                    .error(function (data) {
                        console.log("An error occurred while trying to retrieve the data");
                    });
            }
        })
        .error(function (data) {
            console.log("An error occurred while trying to retrieve the data.");
        });

    $scope.selection = [];

    $scope.selectImage = function (e, path) {
        if ($scope.selection.indexOf(path) == -1) {
            $(e.target).css('border', '3px solid #ff2653');
            $scope.selection.push(path);
        }
        else {
            $(e.target).css('border', 'none');
            $scope.selection.splice($scope.selection.indexOf(path), 1);
        }
    };

    $scope.share = function () {
        FileService.shareData($scope.selection);
    }

});