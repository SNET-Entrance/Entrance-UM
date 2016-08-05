app.controller("KexController", function($scope, UserService) {

    $('#kex-success').hide();
    $('#kex-error').hide();

    $scope.signin = function() {
        var param = {
            username: $('#kex-username').val(),
            password: $('#kex-password').val()
        };
        UserService.SignIn(param)
            .success(function(data) {
                $('#kex-success').show().delay(1000).fadeOut();
            })
            .error(function (data) {
                $('#kex-error').show().delay(1000).fadeOut();
            });
    };


});