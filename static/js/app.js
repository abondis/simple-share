angular.module('simpleShare', ['ngRoute', 'ngResource', 'ngFileUpload'])
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
                     .when('/shared', {
                         templateUrl: 'files.html',
                         controller: 'FilesController',
                     })
                     .when('/shared/:path*', {
                         templateUrl: 'files.html',
                         controller: 'FilesController',
                     })
                     .when('/', {
                         templateUrl: 'home.html',
                         controller: 'HomeController',
                     });
                 $locationProvider.html5Mode(true);
                 $interpolateProvider.startSymbol('[[');
                 $interpolateProvider.endSymbol(']]');
             }
            ])
    .factory('Files', ['$resource', function($resource) {
        return $resource('/api/:api/:path',
                         {path:'@id'},
                         {
                             share: {
                                 url: '/api/share/:path',
                                 method: 'POST'
                             }
                         }
                        );
    }])
    .factory('Shared', ['$resource', function($resource) {
        return $resource('/api/shared/:path',
                         {path:'@id'});
    }])
    .controller('MainController', function($scope, $location) {
        // console.log('aha');
        $scope.$location = $location;
        $scope.get_path = function(url) {
            var path = $location.path();
            path = path.split('/');
            if( url == '..') {
                path.pop();
            } else {
                path.push(url);
            }
            return path.join('/');
            
        };
        $scope.selected = function(url) {
            var p = $location.path();
            if (p === '/' && p === url) {
                return 'pure-menu-selected';
            }
            if ( p.indexOf(url) === 0) {
                return 'pure-menu-selected';
            }
        };
        // $scope.api = {};
    })
    .controller('HomeController', function() {
        console.log('aha');
    })
    .controller('FilesController',
                ['$scope', '$location', '$routeParams', 'Files', 'Upload',
                 function($scope, $location, $routeParams, Files, Upload) {
                     var p = $location.path();
                     if ( p.indexOf('/files') === 0) {
                         $scope.api = 'files';
                     } else if (p.indexOf('/shared') === 0){
                         $scope.api = 'shared';
                     }
                     console.log($scope.api);
                     $scope.new_folder = '';
                     $scope.shared = {};
                     $scope.get_files = function() {
                         $scope.files = Files.get(
                             {
                                 api: $scope.api,
                                 path:$routeParams.path }
                         );
                     };
                     $scope.delete_path = function(path) {
                         var p = $scope.get_api_file_path(path);
                         var file = new Files();
                         file.$delete(
                             {api: $scope.api,
                              path:p },
                             function(data) {
                                 $scope.files = data;
                             }
                         );
                     };
                     $scope.share_path = function(path) {
                         var p = $scope.get_api_file_path(path);
                         var file = new Files();
                         file.$share(
                             {api: $scope.api,
                              path:p },
                             function(data) {
                                 console.log(path);
                                 $scope.shared[path] = data.msg;
                                 console.log($scope.shared);
                             }
                         );
                     };
                     $scope.get_api_file_path = function(folder) {
                         var path = $location.path();
                         path = path.split('/');
                         path.shift();
                         path.shift();
                         if (folder) {path.push(folder);}
                         path = path.join('/');
                         return path;
                     };
                     $scope.get_files();
                     $scope.create_folder = function() {
                         var path = $scope.get_api_file_path($scope.new_folder);
                         var f = new Files();
                         // console.log(f);
                         f.$save(
                             {
                                 api: $scope.api,
                                 path: path,
                                 type: 'dir'
                             },
                             function() {
                                 // console.log('yeah');
                                 $scope.new_folder = '';
                                 $scope.get_files();
                             },
                             function() {
                                 // console.log('neh');
                             });
                     };
                     $scope.upload_files = {};
                     $scope.$watch('upload_files', function () {
                         $scope.upload($scope.upload_files);
                     });
                     $scope.upload = function (files) {
                         if (files && files.length) {
                             var i, file, path;
                             path = $scope.get_api_file_path();
                             (path != "") ? path = '/' + path : true;
                             // console.log(path);
                             for (i = 0; i < files.length; i++) {
	                         (function(file) {
                                     $scope.singleUpload(file, path);
                                 })(files[i]);
                             }
                         }
                     };
                     $scope.singleUpload = function(file, path) {
                         file.upload = Upload.upload({
                             url: '/api/files' + path,
                             fields: {
                                 'type': 'file',
                                 'overwrite': true
                             },
                             file: file
                         });
                         file.upload.progress(function (evt) {
                             file.up_progress = parseInt(100.0 * evt.loaded / evt.total);
                             // console.log('progress: ' + file.up_progress + '% ' + evt.config.file.name);
                         });
                         file.upload.success(function (data, status, headers, config) {
                             $scope.get_files();
                             // console.log('file ' + config.file.name + 'uploaded. Response: ' + data);
                         });
                     };
                 }]);
