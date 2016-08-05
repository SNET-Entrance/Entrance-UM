app.factory('FileService', function($http, ContainerService) {

    return {
        listFiles: function (params) {
            return $http.post('/files/list', params);
        },
        getFile: function (params) {
            return $http.post('/files/get', params);
        },
        openFexplorer: function (onlyFolders, callback) {
            $('#fexplorer-modal').modal('show');
            var treeAll = $('#folders-files');
            var treeFolders = $('#only-folders');
            var btnChoose = $('#fexplorer-btn-choose');
            btnChoose.show();
            if (!onlyFolders) {
                treeFolders.hide();
                treeAll.show();
                btnChoose.unbind();
                btnChoose.on('click', function (service, tree) {
                    return function () {
                        callback(service.files);
                        service.files = [];
                        tree.find('li').removeClass('selected');
                    };
                }(this, treeAll));
            } else {
                treeAll.hide();
                treeFolders.show();
                btnChoose.unbind();
                btnChoose.on('click', function (service, tree) {
                    return function () {
                        callback(service.dir);
                        service.dir = [];
                        tree.find('li').removeClass('selected');
                    };
                }(this, treeFolders));
            }
        },
        files: [],
        getFiles: function () {
            var array = [];
            for (var i=0; i < this.files.length; i++) {
                var file = ContainerService.File(this.files[i], '');
                file.id = i;
                array.push(file);
            }
            return array;
        },
        pushFile: function (file) {
            if (this.files.indexOf(file) > -1)
                this.files.splice(this.files.indexOf(file), 1);
            else
                this.files.push(file);
        },
        putFile: function (file) {
            this.files = [];
            this.files.push(file);
        },
        fileSelected: function (file) {
            return this.files.indexOf(file) != -1;
        },
        dir: [],
        putFolder: function (folder) {
            this.dir = [];
            this.dir.push(folder);
        },
        shareData: function (files) {
            if (files.length == 0)
                return;

            var shareModal = $('#share-modal');
            var shareName = $('#share-name');
            var sharePolicy = $('#share-policy');
            var btnShare = $('#btn-share');

            var tmp = files[0].split('/');
            shareName.val(tmp[tmp.length-1]);
            sharePolicy.val('All');

            shareModal.modal('show');
            shareModal.on('hidden.bs.modal', function () {
                shareName.val('');
                sharePolicy.val('');
            });

            btnShare.unbind();
            btnShare.on('click', function () {
                var containerName = shareName.val();
                var policy = sharePolicy.val();

                if (containerName == '')
                    return;
                var container = ContainerService.Container(containerName);
                
                if ($('#share-advanced').is(':checked')) {
                    var fields = $('#share-advanced-fields').find('input[type=text]');
                    fields = fields.map(function (i, x) { return x.value; });
                    for (var i=0; i < files.length; i++) {
                        var file = ContainerService.File(files[i], encode(fields[i]));
                        container.files.push(file);
                    }
                }
                else {
                    if (policy == '')
                        return;
                    for (var i=0; i < files.length; i++) {
                        var file = ContainerService.File(files[i], encode(policy));
                        container.files.push(file);
                    }
                }

                var shareBtn = $('#share-btn-icon');
                var oldClass = shareBtn.attr('class');
                shareBtn.attr('class', 'fa fa-circle-o-notch fa-spin');
                shareBtn.parent().attr('disabled', true);
                ContainerService.createContainer(container)
                    .success(function (data) {
                        shareBtn.attr('class', oldClass);
                        shareBtn.parent().attr('disabled', false);
                        shareModal.modal('hide');
                    })
                    .error(function (data) {
                    });
            });
        }
    }

    function encode(policy) {
        return policy.replace(', :, ', ' : ').replace('NOT,', 'NOT');
    }

});