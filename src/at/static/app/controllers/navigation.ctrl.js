app.controller("NavigationController", function($scope, PageService, WidgetService, $route, FileService) {

    $scope.pages = [];
    PageService.getPages()
        .success(function (data) {
            PageService.pages = data;
            $scope.pages = data;
        })
        .error(function (data) {
            console.log("Error retrieving the user's pages.");
        });
    $scope.widgets = WidgetService.widgets;

    $scope.addPageBtnClick = function(newPageName) {
        PageService.createPage(newPageName);
    };

    $scope.removePageBtnClick = function(slug) {
        PageService.removePage(slug);
    };

    $scope.addWidgetClick = function(widget) {
        if (widget.hasOwnProperty('onAdd') && typeof widget.onAdd == 'function')
            widget.onAdd(function (params) {
                PageService.addWidget($route.current.params.slug, widget.type, params);
                $route.reload();
            });
        else {
            PageService.addWidget($route.current.params.slug, widget.type, {});
            $route.reload();
        }
    };

    $scope.open = function () {
        FileService.openFexplorer(false, function (files) {
            FileService.shareData(files);
        });
    };

});