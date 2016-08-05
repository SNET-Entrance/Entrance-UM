app.directive("widgetFitness", function() {
    return {
        restrict: 'A',
        templateUrl: baseUrl + '/static/app/views/widgets/fitness.html',
        controller: 'FitnessController',
        scope: {
            id: '=',
            params: '='
        }
    };
});

app.directive("widgetFitnessList", function() {
    return {
        restrict: 'A',
        templateUrl: baseUrl + '/static/app/views/widgets/fitness.list.html',
        controller: 'FitnessListController',
        scope: {
            id: '=',
            params: '='
        }
    };
});

app.directive("widgetFitnessAdd", function() {
    return {
        restrict: 'A',
        templateUrl: baseUrl + '/static/app/views/widgets/fitness.add.html',
        controller: 'FitnessAddController',
        scope: {
            id: '=',
            params: '='
        }
    };
});

app.directive("widgetGallery", function() {
    return {
        restrict: 'A',
        templateUrl: baseUrl + '/static/app/views/widgets/gallery.html',
        controller: 'GalleryController',
        scope: {
            id: '=',
            params: '='
        }
    };
});

app.directive('ngEnter', function() {
    return function(scope, element, attrs) {
        element.bind("keydown keypress", function(event) {
            if(event.which === 13) {
                scope.$apply(function(){
                    scope.$eval(attrs.ngEnter);
                });

                event.preventDefault();
            }
        });
    };
});

app.directive('propertySuggestions', function() {
    var suggestions = [
        'First name',
        'Last name',
        'Title',
        'Birth date',
        'Address',
        'Zip/ Postal Code',
        'City',
        'Phone',
        'Mobile phone',
        'Email',
        'Fax'
    ];
    return function(scope, element, attrs) {
        $(element).autocomplete({
            source: suggestions,
            minLength: 0,
            select: function (e, ui) {
                $(element).first().val(ui.item.value);
                scope.newPropertyKey = ui.item.value;
            }
        });
        $(element).on('click', function () {
            $(element).autocomplete('search', '');
        });
    };
});

app.directive('userSuggestions', ['$compile', 'ContactService', function($compile, ContactService) {
    return function(scope, element, attrs) {
        ContactService.getContacts()
            .success(function (data) {
                var source = [];
                for (var i=0; i < data.length; i++)
                    source.push(data[i].email)

                $(element).autocomplete({
                    source: source,
                    minLength: 0
                });
                $(element).on('click', function () {
                    $(element).autocomplete('search', '');
                });
            })
            .error(function (data) {
                console.log("Error");
            });
    };
}]);

app.directive('attrSuggestions', ['$compile', 'ContactAttributeService', function($compile, ContactAttributeService) {
    return function(scope, element, attrs) {
        var elem = $(element);
        elem.tokenfield({
            autocomplete: {
                source: function (request, response) {
                    ContactAttributeService.filterAttributes(request.term)
                        .success(function (data) {
                            response(data.map(function (a) {
                                return {
                                    label: a.display_name,
                                    value: a.display_name,
                                    id: a.id
                                };
                            }));
                        })
                        .error(function (data) {
                            console.log("error");
                        });
                },
                delay: 100,
                minLength: 1
            },
            showAutocompleteOnFocus: true
        });
        elem.tokenfield('setTokens', scope.contact.attributes.map(function (a) {
            return {
                label: a.display_name,
                value: a.display_name,
                id: a.id
            };
        }));
        elem.on('tokenfield:createtoken', function (e) {
            attrs = elem.tokenfield('getTokens').map(function (a) {
                return a.value;
            });
            if (attrs.indexOf(e.attrs.value) != -1)
                return false;
            var newAttribute = ContactAttributeService.Attribute(scope.contact.id, e.attrs.value);
            ContactAttributeService.createAttribute(scope.contact.id, newAttribute)
                .success(function (data) {
                    e.attrs.id = data.id;
                    // TODO: notify user
                })
                .error(function (data) {
                    // TODO: notify user
                });
        });
        elem.on('tokenfield:removedtoken', function (e) {
            ContactAttributeService.deleteAttribute(scope.contact.id, e.attrs.id)
                .success(function (data) {
                    // TODO: notify user
                })
                .error(function (data) {
                    // TODO: notify user
                });
        });
    };
}]);

app.directive('policyAuthoring', ['$compile', 'ContactAttributeService', function($compile, ContactAttributeService) {
    return function(scope, element, attrs) {
        var elem = $(element);
        elem.tokenfield({
            autocomplete: {
                source: function (request, response) {
                    ContactAttributeService.filterAttributes(request.term)
                        .success(function (data) {
                            response(data.map(function (a) {
                                return {
                                    label: a.display_name,
                                    value: a.display_name,
                                    id: a.id
                                };
                            }));
                        })
                        .error(function (data) {
                            console.log("error");
                        });
                },
                minLength: 1
            },
            showAutocompleteOnFocus: true
        });
        elem.tokenfield('setTokens', ['All']);
        elem.on('tokenfield:createtoken', function (e) {
            attrs = elem.tokenfield('getTokens').map(function (a) {
                return a.value;
            });
            if (attrs.indexOf(e.attrs.value) != -1 && e.attrs.value != ':')
                return false;
        });
        // TODO: ease policy typing by automatically inserting tokens when keyword is typed
        /*
         // TODO: be aware there are mutliple fields
        var writingField = $('#share-policy-tokenfield');
        writingField.keydown(function (e) {
            if (e.keyCode == 190 && e.shiftKey) {
                var array = elem.tokenfield('getTokens');
                if (array[array.length-1].value == ':')
                    return false;

                array.push({ label: ':', value: ':' });
                elem.tokenfield('setTokens', array);
                return false;
            }
            console.log(elem.data('bs.tokenfield').$input);
        });
        */
    };
}]);

app.directive('dropzone', function() {
    return {
        restrict: 'C',
        link: function(scope, element, attrs) {

            var previewTemplate = $('#previews').clone().attr('id', '');
            var previewNode = previewTemplate.find('#-dropzone-template');
            previewNode.attr('id', scope.id + '-dropzone-template');

            var config = {
                url: '/fitness/',
                method: 'post',
                parallelUploads: 2,
                maxFilesize: 10,
                filesizeBase: 1000,
                paramName: 'file',
                uploadMultiple: false,
                // headers: {},
                addRemoveLinks: false,
                previewTemplate: previewTemplate[0].innerHTML,
                previewsContainer: null,
                clickable: false,
                init: function () {

                },
                acceptedFiles: '.FIT,.fit'
            };

            var eventHandlers = {
                'addedfile': function(file) {
                    $('#' + scope.id + '-dropzone-default').hide();
                },
                'success': function (file, response) {
                    var preview = $(file.previewElement);
                    preview.find('.dropzone-progress').hide();
                    preview.find('.dropzone-success').show();
                },
                'error': function(file, errorMessage, response) {
                    var preview = $(file.previewElement);
                    preview.find('.dropzone-progress').hide();
                    preview.find('.dropzone-error').show();
                },
                'dragover': function (event) {
                    $('#' + scope.id + '-dropzone').attr('class', 'dropzone-over');
                },
                'dragleave': function (event) {
                    $('#' + scope.id + '-dropzone').attr('class', 'dropzone');
                },
                'drop': function (event) {
                    $('#' + scope.id + '-dropzone').attr('class', 'dropzone');
                },
                'queuecomplete': function () {
                }
            };

            dropzone = new Dropzone(element[0], config);

            angular.forEach(eventHandlers, function(handler, event) {
                dropzone.on(event, handler);
            });

            scope.processDropzone = function() {
                dropzone.processQueue();
            };

            scope.resetDropzone = function() {
                dropzone.removeAllFiles();
            }
        }
    }
});

app.directive('adropzone', function() {
    return {
        restrict: 'C',
        link: function(scope, element, attrs) {

            var previewTemplate = $('#previews').clone().attr('id', '');
            var previewNode = previewTemplate.find('#-dropzone-template');
            previewNode.attr('id', 'adropzone-template');

            var config = {
                url: '/files/fexplorer/upload',
                method: 'post',
                parallelUploads: 2,
                maxFilesize: 10,
                filesizeBase: 1000,
                paramName: 'file',
                uploadMultiple: false,
                // headers: {},
                addRemoveLinks: false,
                previewTemplate: previewTemplate[0].innerHTML,
                previewsContainer: null,
                clickable: false,
                init: function () {

                }
            };

            var eventHandlers = {
                'addedfile': function(file) {
                    $('#adropzone-default').hide();
                },
                'success': function (file, response) {
                    var preview = $(file.previewElement);
                    preview.find('.dropzone-progress').hide();
                    preview.find('.dropzone-success').show();
                },
                'error': function(file, errorMessage, response) {
                    var preview = $(file.previewElement);
                    preview.find('.dropzone-progress').hide();
                    preview.find('.dropzone-error').show();
                },
                'dragover': function (event) {
                    $('#adropzone').attr('class', 'dropzone-over');
                },
                'dragleave': function (event) {
                    $('#adropzone').attr('class', 'dropzone');
                },
                'drop': function (event) {
                    $('#adropzone').attr('class', 'dropzone');
                },
                'queuecomplete': function () {
                }
            };

            dropzone = new Dropzone(element[0], config);

            angular.forEach(eventHandlers, function(handler, event) {
                dropzone.on(event, handler);
            });

            scope.processDropzone = function() {
                dropzone.processQueue();
            };

            scope.resetDropzone = function() {
                dropzone.removeAllFiles();
            }
        }
    }
});