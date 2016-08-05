app.factory('WidgetService', function(FileService) {

    var widgets = [{
            name: 'Fitness Widget',
            type: 'widget-fitness',
            size: 6
        }, {
            name: 'Gallery Widget',
            type: 'widget-gallery',
            size: 4,
            onAdd: function (callback) {
                FileService.openFexplorer(true, function (dir) {
                    callback({ path: dir[0], galleryName: dir[0].slice(0, -1).split('/').pop() });
                });
            }
        }, {
            name: 'Fitness List Widget',
            type: 'widget-fitness-list',
            size: 6
        }, {
            name: 'Fitness Add Widget',
            type: 'widget-fitness-add',
            size: 4
        }
    ];

    return {
        widgets: widgets,
        getSize: function (type) {
            for (var i=0; i < this.widgets.length; i++)
                if (type == this.widgets[i].type)
                    return this.widgets[i].size;
        }
    };

});