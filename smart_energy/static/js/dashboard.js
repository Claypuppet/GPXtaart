$(() => {

  const smartEnergy = {
    storageMeterKey: 'meter_id',

    elements: {
      powerContainer: $('#power-container'),
      gasContainer: $('#gas-container'),
      meterSelector: $('#meter-select')
    },

    events: {},

    init: () => {
      smartEnergy.setInitialMeter();
    },

    setInitialMeter: () => {
      const storageId = smartEnergy.getMeterIdFromStorage();
      if (storageId > 0) {
        console.log('set meter from storage', storageId);
        smartEnergy.setNewMeter(storageId, false, true);
      } else {
        smartEnergy.setNewMeter(smartEnergy.elements.meterSelector.val());
      }
    },

    setNewMeter: (id, save = true, setElement = false) => {
      if (save && typeof (Storage) !== 'undefined') {
        localStorage.setItem(smartEnergy.storageMeterKey, id);
      }
      if (setElement) {
        smartEnergy.elements.meterSelector.val(id);
      }
      // TODO: retrieve meter data
    },

    getMeterIdFromStorage: () => {
      let meterId = Storage && localStorage.getItem(smartEnergy.storageMeterKey);
      if (smartEnergy.elements.meterSelector.children('option[value=' + meterId + ']').length) {
        return meterId;
      }
      return 0;
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

  smartEnergy.init();

});


