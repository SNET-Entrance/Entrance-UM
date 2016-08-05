app.factory('ContactPropertyService', function($http) {

    return {
        Property: function (key, value, contactId) {
            return {
                id: null,
                key: key,
                value: value,
                user_id: contactId
            };
        },
        getProperties: function (userId) {
            return $http.get('/contacts/' + userId + '/properties');
        },
        getProperty: function (userId, propId) {
            return $http.get('/contacts/' + userId + '/properties/' + propId);
        },
        createProperty: function (userId, params) {
            return $http.post('/contacts/' + userId + '/properties', params);
        },
        updateProperty: function (userId, propId, params) {
            return $http.put('/contacts/' + userId + '/properties/' + propId, params);
        },
        deleteProperty: function (userId, propId) {
            return $http.delete('/contacts/' + userId + '/properties/' + propId);
        }
    };

});