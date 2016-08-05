app.factory('ContactService', function($http) {

    return {
        Contact: function (name, email) {
            return {
                id: null,
                name: name,
                email: email,
                properties: [],
                attributes: []
            };
        },
        getContacts: function () {
            return $http.get('/contacts');
        },
        getContact: function (id) {
            return $http.get('/contacts/' + id);
        },
        createContact: function (params) {
            return $http.post('/contacts', params);
        },
        updateContact: function (id, params) {
            return $http.put('/contacts/' + id, params);
        },
        deleteContact: function (id) {
            return $http.delete('/contacts/' + id);
        }
    };

});