angular.module('simpleShare', ['ngRoute', 'ngResource'])
    .config(['$routeProvider', '$locationProvider', '$interpolateProvider',
             function($routeProvider, $locationProvider, $interpolateProvider) {
                 $routeProvider
                     .when('/files', {
                         templateUrl: 'files.html',
                         controller: 'FilesController',
                     })
                     .when('/files/:path*', {
                         templateUrl: 'files.html',
                         controller: 'FilesController',
                     })
                     .when('/', {
                         templateUrl: 'home.html',
                         controller: 'HomeController',
                     });
                 //$locationProvider.html5Mode(true);
                 $interpolateProvider.startSymbol('[[');
                 $interpolateProvider.endSymbol(']]');
             }
            ])
    .factory('Files', ['$resource', function($resource) {
        return $resource('/files/:f_user/:path', {user: 'test'});
    }])
    .controller('HomeController', function() {
        console.log('aha');
    })
    .controller('FilesController',
                ['$scope', '$routeParams', 'Files',
                 function($scope, $routeParams, Files) {
                     $scope.files = Files.get(
                         {
                             f_user:'test',
                             path:$routeParams.path }
                     );
                 }]);
