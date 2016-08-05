app.factory('ContactAttributeService', function($http) {

    return {
        Attribute: function (userId, name) {
            return {
                id: null,
                name: name,
                user_id: userId
            };
        },
        getAllAttributes: function () {
            return $http.get('/contacts/attributes');
        },
        filterAttributes: function (query) {
            return $http.post('/contacts/filter/attributes', query);
        },
        getAttributes: function (userId) {
            return $http.get('/contacts/' + userId + '/attributes');
        },
        getAttribute: function (userId, attrId) {
            return $http.get('/contacts/' + userId + '/attributes/' + attrId);
        },
        createAttribute: function (userId, params) {
            return $http.post('/contacts/' + userId + '/attributes', params);
        },
        updateAttribute: function (userId, attrId, params) {
            return $http.put('/contacts/' + userId + '/attributes/' + attrId, params);
        },
        deleteAttribute: function (userId, attrId) {
            return $http.delete('/contacts/' + userId + '/attributes/' + attrId);
        }
    };

});