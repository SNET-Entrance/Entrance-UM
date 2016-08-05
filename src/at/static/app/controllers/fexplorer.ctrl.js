app.controller("FexplorerController", function($scope, FileService) {

    $('#fexplorer-modal').on('show.bs.modal', function () {
        $scope.refresh();
    });

    $scope.refresh = function() {
        var treeAll = $('#folders-files-container');
        var treeFolders = $('#only-folders-container');
        treeAll.html('');
        treeAll.html('<div id="folders-files" class="filetree-basic"></div>');
        treeFolders.html('');
        treeFolders.html('<div id="only-folders" class="filetree-basic"></div>');
        init();
    };

    function init() {
        var treeAll = $('#folders-files');
        treeAll.fileTree({
            root: '/',
            script: '/files/fexplorer',
            expandSpeed: 100,
            collapseSpeed: 100,
            multiSelect: true,
            onlyFolders: false
        }, function(file) { });
        treeAll.on('filetreeclicked', function (e, data) {
            if (data.type == 'file') {

                if (FileService.fileSelected(data.rel))
                    data.li.removeClass('selected');
                else
                    data.li.addClass('selected');
                FileService.pushFile(data.rel);
            }
        });

        var treeFolders = $('#only-folders');
        treeFolders.fileTree({
            root: '/',
            script: '/files/fexplorer',
            expandSpeed: 100,
            collapseSpeed: 100,
            multiSelect: false,
            onlyFolders: true
        }, function(file) { });
        treeFolders.on('filetreeexpand', function (e, data) {
            treeFolders.find('li').removeClass('selected');
            data.li.addClass('selected');
            FileService.putFolder(data.rel);
        });
        treeFolders.on('filetreecollapse', function (e, data) {
            data.li.removeClass('selected');
            FileService.putFolder(data.rel);
        });
    }

    $scope.toggle = function () {
        if (treeAll.is(':hidden')) {
            treeFolders.hide();
            treeAll.show();
        }
        else {
            treeFolders.show();
            treeAll.hide();
        }
    };

});
