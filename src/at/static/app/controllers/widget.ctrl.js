app.controller("WidgetController", function($scope, PageService, $route) {

    $scope.removeWidget = function(id) {
        PageService.removeWidget($route.current.params.slug, id);
        $route.reload();
    };
});