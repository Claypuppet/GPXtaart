(() => {

  const smartEnergy = {
    defaults: {
      powerContainer: document.querySelector('#power-container')
    },

    events: {

    },

    init: () => {

    },

    generatePowerChart: (consumptionPoints, productionPoints) => {
      Highcharts.chart(smartEnergy.defaults.powerContainer, {
        chart: {
          zoomType: 'x'
        },
        title: {
          text: 'Power'
        },
        subtitle: {
          text: ''
        },
        tooltip: {
          valueDecimals: 3
        },
        xAxis: {
          type: 'datetime'
        },

        series: [{
          data: consumptionPoints,
          lineWidth: 0.5,
          name: 'Power consumption (kWh)',
          color: 'blue'
        }, {
          data: productionPoints,
          lineWidth: 0.5,
          name: 'Power production (kWh)',
          color: 'green'
        }]

      });
    },

    generateGasChart: () => {

    },

  };


})();


