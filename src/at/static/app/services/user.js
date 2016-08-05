app.factory('UserService', function($http) {

    return {
        SignIn: function(credentials) {
            return $http.post('/kex_auth', credentials);
        }
    };

});