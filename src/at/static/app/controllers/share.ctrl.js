app.controller("ShareController", function($scope, FileService) {

    $scope.files = [];
    $('#share-modal').on('show.bs.modal', function () {
        $scope.files = FileService.getFiles();
        $scope.$apply();
    });

    $scope.toggle = function () {
        if ($('#share-advanced').is(':checked')) {
            $('#share-advanced-fields').show();
            $('#share-policy').attr('disabled', true);
        }
        else {
            $('#share-advanced-fields').hide();
            $('#share-policy').attr('disabled', false);
        }
    }

});