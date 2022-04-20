var module = angular.module('myApp',[]);

function Main($scope,$http, $compile){
// $http.get("/chart/").

$scope.FILTInit = function(){
  $http({
    method:"GET",
    url:"/chart1/",
    params:{
          req_date:1}
       }).then( function(response, status) {
$scope.data = response.data;
var name = $scope.data.y1
var options = {
  series: [{
  name: 'Date: '+$scope.data.dates,
  data: $scope.data.y1,
}],
  chart: {
  type: 'bar',
  height: 350
},
plotOptions: {
  bar: {
    borderRadius: 4,
    endingShape: 'rounded'
  }
},
dataLabels: {
  enabled: false
},
xaxis: {
  categories: $scope.data.xaxis,
  labels: {align: 'left', rotate: -90, rotateAlways: true, offsetY: 0},
},
yaxis: {min: 8.3,},

grid: {show: false},

annotations: {
  yaxis: [{
    y: 10.3,
//    y2: 10.75,
    borderColor: 'blue',
//    fillColor: 'blue',
    label: {
      show: true,
      text: '10.30 AM',
      style: {
        color: "#fff",
        background: '#00E396'
      }
    }
  },
  {
    y: 9,
//    y2: 9.25,
    borderColor: 'green',
//    fillColor: 'green',
    label: {
      show: true,
      text: '9 AM',
      style: {
        color: "#fff",
        background: '#00E396'
      }
    }
  }]},
legend: {
        position: 'top',
        showForSingleSeries: true,
        horizontalAlign: 'left',
        fontFamily: 'ubuntu-medium',
        fontSize: '13px',},
fill: {
    type: "gradient",
    opacity: 1,
    gradient: {
      inverseColors: false,
      shade: 'light',
      type: "vertical",
      opacityFrom: 0.85,
      opacityTo: 0.85,
      stops: 0}},
tooltip: {
    y: {
      formatter: function(value, { series, y1data, seriesIndex, dataPointIndex, w }) {
        console.log("hhh", y1data);
        return  'Time: '+$scope.data.y1[dataPointIndex]},
      title: {
        formatter: function (seriesName) {
          return ''}}
        }
  }
};

var chart = new ApexCharts(document.querySelector("#atndchart"), options);
chart.render();
chart.update();})}

// Work Order Chart Update
$scope.FILT = function(){
  $http({
    method:"GET",
    url:"/chart1/",
    params:{
          req_date:$scope.req_date}
       }).then( function(response, status) {
$scope.data = response.data;
var name = $scope.data.y1
var options = {
  series: [{
    name: '    Date: '+$scope.data.dates,
  data: $scope.data.y2,
}],
  chart: {
  type: 'rangeBar',
  height: 350
},
plotOptions: {
  bar: {
    borderRadius: 4,
    // endingShape: 'rounded',
  }
},
dataLabels: {
  enabled: false
},
xaxis: {
  // categories: $scope.data.xaxis,
  labels: {align: 'left', rotate: -90, rotateAlways: true, offsetY: 0},
},
yaxis: {min: 8.3,},

grid: {show: false},

annotations: {
  yaxis: [{
    y: 10,
//    y2: 10.75,
    borderColor: 'blue',
//    fillColor: 'blue',
    label: {
      show: true,
      text: '10 AM',
      style: {
        color: "#fff",
        background: '#00E396'
      }
    }
  },
  {
    y: 19,
//    y2: 9.25,
    borderColor: 'green',
//    fillColor: 'green',
    label: {
      show: true,
      text: '7 PM',
      style: {
        color: "#fff",
        background: '#00E396'
      }
    }
  }]},
legend: {
        position: 'top',
        showForSingleSeries: true,
        horizontalAlign: 'left',
        fontFamily: 'ubuntu-medium',
        fontSize: '13px',},
fill: {
    type: "gradient",
    opacity: 1,
    gradient: {
      inverseColors: false,
      shade: 'light',
      type: "vertical",
      opacityFrom: 0.85,
      opacityTo: 0.85,
      stops: 0}},
// tooltip: {
//     y: {
//       formatter: function(value, { series, y1data, seriesIndex, dataPointIndex, w }) {
//         console.log("hhh", y1data);
//         return  'Time: '+$scope.data.y1[dataPointIndex]},
//       title: {
//         formatter: function (seriesName) {
//           return ''}}
//         }
//   }
};

var chart = new ApexCharts(document.querySelector("#atndchart"), options);
chart.render();
chart.update();})}
var k=['am', 'pm']
$scope.FILTInit1 = function(){
  $http({
    method:"GET",
    url:"/userchart1/",
    params:{
          req_date:'1'}
       }).then( function(response, status) {
$scope.data = response.data;
var options = {
  series: [{
    name: 'From '+$scope.data.fromdt +' '+ 'to '+$scope.data.todt,
  data: $scope.data.y1,
  
}],
  chart: {
  type: 'rangeBar',
  height: 350
},
plotOptions: {
  bar: {
    borderRadius: 4,
    endingShape: 'rounded',
    horizontal: true,
  }
},
dataLabels: {
  enabled: false
},
xaxis: {
  labels: {show: false, align: 'left', rotate: 0, rotateAlways: true, offsetY: 0},
  // type: 'datetime',
},
yaxis: {min: 830},

grid: {show: false},

annotations: {
  xaxis: [{
    x: 1000,
//    y2: 10.75,
    borderColor: 'blue',
//    fillColor: 'blue',
    label: {
      show: true,
      text: '10 AM',
      style: {
        color: "#fff",
        background: '#00E396'
      }
    }
  },
  {
    x: 1900,
//    y2: 9.25,
    borderColor: 'green',
//    fillColor: 'green',
    label: {
      show: true,
      text: '7 PM',
      style: {
        color: "#fff",
        background: '#00E396'
      }
    }
  }]},
  tooltip: {
    x: {
      formatter: function(val) {
        return  (val/100).toFixed(2)},},
    y: {
      title: {
        formatter: function (seriesName) {
          return ''}}}},
legend: {
        position: 'top',
        showForSingleSeries: true,
        horizontalAlign: 'left',
        fontFamily: 'ubuntu-medium',
        fontSize: '13px',},
fill: {
    type: "gradient",
    opacity: 1,
    gradient: {
      inverseColors: false,
      shade: 'light',
      type: "vertical",
      opacityFrom: 0.85,
      opacityTo: 0.85,
      stops: 0}},
};


var chart = new ApexCharts(document.querySelector("#userchart1"), options);
chart.render();
chart.update();})}

$scope.FILT1 = function(){
  $http({
    method:"GET",
    url:"/userchart1/",
    params:{
          req_date:$scope.req_date}
       }).then( function(response, status) {
$scope.data = response.data;
var options = {
  series: [{
    name: 'From '+$scope.data.fromdt +' '+ 'to '+$scope.data.todt,
  data: $scope.data.y1,
  
}],
  chart: {
  type: 'rangeBar',
  height: 350
},
plotOptions: {
  bar: {
    borderRadius: 4,
    endingShape: 'rounded',
    horizontal: true,
  }
},
dataLabels: {
  enabled: false
},
xaxis: {
  labels: {show: false, align: 'left', rotate: 0, rotateAlways: true, offsetY: 0},
  // type: 'datetime',
},
yaxis: {min: 830},

grid: {show: false},

annotations: {
  xaxis: [{
    x: 1000,
//    y2: 10.75,
    borderColor: 'blue',
//    fillColor: 'blue',
    label: {
      show: true,
      text: '10 AM',
      style: {
        color: "#fff",
        background: '#00E396'
      }
    }
  },
  {
    x: 1900,
//    y2: 9.25,
    borderColor: 'green',
//    fillColor: 'green',
    label: {
      show: true,
      text: '7 PM',
      style: {
        color: "#fff",
        background: '#00E396'
      }
    }
  }]},
  tooltip: {
    x: {
      formatter: function(val) {
        return  (val/100).toFixed(2)},},
    y: {
      title: {
        formatter: function (seriesName) {
          return ''}}}},
legend: {
        position: 'top',
        showForSingleSeries: true,
        horizontalAlign: 'left',
        fontFamily: 'ubuntu-medium',
        fontSize: '13px',},
fill: {
    type: "gradient",
    opacity: 1,
    gradient: {
      inverseColors: false,
      shade: 'light',
      type: "vertical",
      opacityFrom: 0.85,
      opacityTo: 0.85,
      stops: 0}},
};


var chart = new ApexCharts(document.querySelector("#userchart1"), options);
chart.render();
chart.update();})}


}module.controller("MainCtrl",Main); 




//       var options = {
//         series: [
//           {
            
//             name: 'Joe',
//             data: [
//               {
//                 x: 'Design',
//                 y: [
//                   845337900000,
//                   845337959000
//                 ]
//               }
//             ]
//           },
//         ],
//         chart: {
//           height: 450,
//           type: 'rangeBar'
//         },
//         plotOptions: {
//           bar: {
//             horizontal: true,
//             barHeight: '80%'
//           }
//         },
//         xaxis: {
//           type: 'datetime',
//           labels: {format: 'HH:mm'}
//         },
//         fill: {
//           type: 'gradient',
//           gradient: {
//             shade: 'light',
//             type: 'vertical',
//             shadeIntensity: 0.25,
//             gradientToColors: undefined,
//             inverseColors: true,
//             opacityFrom: 1,
//             opacityTo: 1,
//             stops: [50, 0, 100, 100]
//           }
//         },
//         legend: {
//           position: 'top',
//           horizontalAlign: 'left'
//         },
//         tooltip: {
//           y: {
//             enabled: true,
//             show: true,
//             formatter: function(value, { series, seriesIndex, dataPointIndex, w }) {
//               return dataPointIndex;
//             }
//           },
//           x: {
//                   format: 'HH:mm'
//                 },
//         },
//       };

// var chart = new ApexCharts(document.querySelector("#chart"), options);

// chart.render();

