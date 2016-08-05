app.controller("PageController", function($scope, $routeParams, $compile, $location, PageService, WidgetService, FileService) {

    if (typeof $routeParams.slug == 'undefined')
        $location.path('/page/my-dashboard/');

    var page = PageService.getPage($routeParams.slug);
    $scope.data = [];

    if (page == null)
        return;

    for (var i=0; i < page.widgets.length; i++) {
        var div = document.createElement('div');
        var size = WidgetService.getSize(page.widgets[i].type);
        div.setAttribute('class', 'sortable-item col-md-' + size);
        div.setAttribute(page.widgets[i].type, '');
        div.setAttribute('id', page.widgets[i].id);
        div.setAttribute('params', JSON.stringify(page.widgets[i].params));
        $compile(div)($scope);
        $('#widgets-container').append(div);
    }

    var sort = $('.sortable');
    sort.sortable({ tolerance: 'pointer', placeholder: 'col-md-4 placeholder', items: 'div.sortable-item' });
    sort.on( "sortstart", function (event, ui) {
        var placeholder = $('.placeholder');
        placeholder.css('width', ui.item.width());
        placeholder.css('min-height', ui.item.height());
    });
    sort.on('sortupdate', function (event, ui) {
        var ids = $('.sortable').sortable('toArray');
        PageService.sortWidgets(page.slug, ids);
    });



});