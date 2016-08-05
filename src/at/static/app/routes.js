app.config(['$routeProvider', function($routeProvider) {
    $routeProvider
        .when('/', {
            templateUrl: baseUrl + '/static/app/views/welcome.html',
            controller: 'PageController'
        })
        .when('/page/:slug/', {
            templateUrl: baseUrl + '/static/app/views/page.html',
            controller: 'PageController'
        })
        .when('/contacts/', {
            templateUrl: baseUrl + '/static/app/views/contacts.html',
            controller: 'ContactController'
        })
        .when('/container/', {
            templateUrl: baseUrl + '/static/app/views/container.html',
            controller: 'ContainerController'
        })
        .when('/kex/', {
            templateUrl: baseUrl + '/static/app/views/kex.html',
            controller: 'KexController'
        });
}]);