var app = angular.module("entrance", ['ngRoute', 'ui.bootstrap']);
app.config(function($interpolateProvider) {
    $interpolateProvider.startSymbol('{_');
    $interpolateProvider.endSymbol('_}');
});