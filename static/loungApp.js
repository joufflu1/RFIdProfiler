'use strict';
var loungApp = angular.module ('loungApp', ['ngSocket']);


loungApp.config(["$socketProvider", function ($socketProvider) {
  $socketProvider.setUrl("http://192.168.42.1:5000");
}]);

 
loungApp.controller('LoungController', ['$scope', '$socket', function($scope, $socket) {
  $scope.selectRow = function(x) {
    $scope.selectedIdentifier=x.tagId;
    $scope.selectedCustomer=x;
  };

  $scope.sendTagId = function() {
    console.log($scope.tagId);
    $socket.emit('sendTagId', {data:$scope.tagId});

    $scope.tagId = "";
  };

  $scope.addCustomerInLoung = function(customer) {
    $scope.customerListInLoung.push(customer);
    $scope.tagId = "";
  };

  $socket.on ('connect', $scope, function (data) { 
    console.log ('connected'); 
    $socket.emit('getCustomerListInLoung');
    $socket.emit('sendTagId', {data:2});

  });

  $socket.on ('customerListInLoung', $scope, function (json) {
    console.log ('customerListInLoung' + json.length);
    $scope.customerListInLoung = [];
    for(var index = 0; index < json.length;index++ ) {
      $scope.addCustomerInLoung(json[index]);
    }
  });

  $socket.on ('selectedCustomer', $scope, function (json) {
    console.log ('selectedCustomer' + json.length);
    $scope.customerListInLoung = [];
    for(var index = 0; index < json.length;index++ ) {
      if($scope.selectedIdentifier == json[index].tagId) {
        $scope.selectedCustomer = json[index];
      }
    }
  });
}]);
