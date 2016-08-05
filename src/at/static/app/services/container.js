app.factory('ContainerService', function($http) {

    return {
        Container: function (name) {
            return {
                id: null,
                name: name,
                path: null,
                status: null,
                files: []
            };
        },
        File: function (path, policy) {
            return {
                id: null,
                type: 'PABE14',
                path: path,
                policy: policy,
                container_id: null,
                filename: path.split('/').pop()
            }
        },
        getContainers: function () {
            return $http.get('/container');
        },
        getContainer: function (id) {
            return $http.get('/container/' + id);
        },
        createContainer: function (params) {
            return $http.post('/container', params);
        },
        updateContainer: function (id, params) {
            return $http.put('/container/' + id, params);
        },
        deleteContainer: function (id) {
            return $http.delete('/container/' + id);
        }
    };

});