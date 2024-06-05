<template>
  <div>
    <div class="card">
      <h5>Traffic Density</h5>
      <p>Travel predictions for {{ predictionsDate }}</p>
      <div ref="mapContainer" class="map-container"></div>
    </div>
    <div class="card flex items-center space-x-4">
      <Dropdown v-model="selectedRoute" :options="routes" filter @change="loadVehicleCountPredictions" optionLabel="value" placeholder="Select a Route" class="w-full md:w-14rem mr-5">
        <template #value="slotProps">
          <div v-if="slotProps.value" class="flex align-items-center">{{ slotProps.value.value }}</div>
          <span v-else>{{ slotProps.placeholder }}</span>
        </template>
        <template #option="slotProps">
          <div class="flex align-items-center">
            <div>{{ slotProps.option.value }}</div>
          </div>
        </template>
      </Dropdown>
      <InputNumber v-model="hoursToPredict" @input="onHoursToPredictChanged" showButtons buttonLayout="horizontal" class="centered-input-number" style="width: 3rem" :min="0" :max="168">
        <template #incrementbuttonicon>
          <span class="pi pi-plus" />
        </template>
        <template #decrementbuttonicon>
          <span class="pi pi-minus" />
        </template>
      </InputNumber>
    </div>
    <div class="card">
      <div class="chart-wrapper">
        <div class="progress-container" v-if="loading">
          <ProgressSpinner style="width: 3rem; height: 3rem;" />
        </div>
        <DataTable :value="vehicleCountPredictions" scrollable scrollHeight="15rem" style="min-height: 15rem">
          <Column field="datetime" header="Date"></Column>
          <Column field="number_of_vehicles_right_lane" header="Number of Vehicles"></Column>
        </DataTable>
      </div>
    </div>
    <div class="card">
      <div class="chart-wrapper">
        <div class="progress-container" v-if="loading">
          <ProgressSpinner style="width: 4rem; height: 4rem;" />
        </div>
        <Chart type="line" :data="chartData" :options="chartOptions" class="h-30rem" :class="{ 'loading': loading }" />
      </div>
    </div>
  </div>

  <Toast />
</template>
<script setup>
import { onMounted, ref } from "vue";
import axios from "@/axios";
import { useToast } from "primevue/usetoast";
import mapboxgl from "mapbox-gl";
import "mapbox-gl/dist/mapbox-gl.css";
import routeLocations from "@/service/VehicleCounterRouters";

const toast = useToast();

const loading = ref(true);

const routes = ref([]);
const selectedRoute = ref(null);

const vehicleCountPredictions = ref([]);
const predictionsDate = ref('N/A');
const hoursToPredict = ref(7);

const chartData = ref();
const chartOptions = ref();

let map = null;
const mapContainer = ref(null);
const markers = [];

onMounted(() => {
  mapboxgl.accessToken = import.meta.env.VITE_MAPBOX_TOKEN;

  map = new mapboxgl.Map({
    accessToken: import.meta.env.VITE_MAPBOX_TOKEN,
    container: mapContainer.value,
    style: 'mapbox://styles/mapbox/standard',
    center: [15.045314, 46.150356],
    zoom: 10
  });

  redirectToCoordinatesAndZoomOut(15.045314, 46.150356, 7);

  loadRouteMarkers();

  const currentDate = new Date();
  currentDate.setHours(currentDate.getHours() + 1);
  predictionsDate.value = currentDate.toLocaleDateString() + ' ' + currentDate.toLocaleTimeString();

  loadRoutes()
  chartOptions.value = setChartOptions();
})

const redirectToCoordinatesAndZoomOut = (longitude, latitude, zoomLevel) => {
  map.flyTo({
    center: [longitude, latitude],
    zoom: zoomLevel,
    essential: true
  });
}

const getMarkerPopup = (route) => {
  return new mapboxgl.Popup({offset: 25}).setHTML(`<h3>${route.name}</h3><p>${new Date().toLocaleTimeString()}</p>`);
}

const loadRouteMarkers = async () => {
  try {
    routeLocations.forEach(route => {
      const marker = new mapboxgl.Marker({ color: '#45a7e1' })
          .setLngLat([route.longitude, route.latitude])
          .setPopup(getMarkerPopup(route))
          .addTo(map);

      marker.getElement().addEventListener('click', async () => {
        for (const r of routes.value) {
          if (r.value.includes(route.name)) {
            selectedRoute.value = r;
            loadVehicleCountPredictions();
            break;
          }
        }
      });

      markers.push(marker);
    });
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Something went wrong...', life: 3000 });
    console.error(error);
  }
}

const loadRoutes = async () => {
  loading.value = true

  try {
    const response = await axios.get(`${import.meta.env.VITE_API_BASE_URL}/api/v1/vehicle-counter/routes`)
    if (!response.data) {
      toast.add({ severity: 'error', summary: 'Oops', detail: 'Something went wrong...', life: 3000 })
      return
    }

    routes.value = response.data.routes
    selectedRoute.value = routes.value[0]

    loadVehicleCountPredictions();
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Oops', detail: 'Something went wrong...', life: 3000 })
  } finally {
    loading.value = false
  }
}

const loadVehicleCountPredictions = async () => {
  if (!selectedRoute.value) {
    return;
  }

  loading.value = true

  const location = selectedRoute.value.location;
  const direction = selectedRoute.value.direction;

  try {
    const response = await axios.post(`${import.meta.env.VITE_API_BASE_URL}/api/v1/vehicle-counter/predict`, {
      location_name: location,
      direction: direction,
      hours: hoursToPredict.value ?? 7,
      stage: "Production"
    })

    if (!response.data) {
      toast.add({ severity: 'error', summary: 'Oops', detail: 'Something went wrong...', life: 3000 })
      return
    }

    const predictions = []
    for (const prediction of response.data.predictions) {
      predictions.push({
        location: prediction.location,
        datetime: convertUtcToLocal(prediction.datetime),
        route: prediction.route,
        number_of_vehicles_right_lane: prediction.number_of_vehicles_right_lane,
      })
    }

    vehicleCountPredictions.value = predictions;
    chartData.value = setChartData('Number of vehicles per hour', vehicleCountPredictions.value.map(prediction => prediction.datetime), vehicleCountPredictions.value.map(prediction => prediction.number_of_vehicles_right_lane))

    loadStagingVehicleCountPredictions();
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Oops', detail: 'Something went wrong...', life: 3000 })
  } finally {
    loading.value = false
  }
}

const loadStagingVehicleCountPredictions = async () => {
  if (!selectedRoute.value) {
    return;
  }

  const location = selectedRoute.value.location;
  const direction = selectedRoute.value.direction;

  try {
    const response = await axios.post(`${import.meta.env.VITE_API_BASE_URL}/api/v1/vehicle-counter/predict`, {
      location_name: location,
      direction: direction,
      hours: hoursToPredict.value ?? 7,
      stage: "Staging"
    })

    if (!response.data) {
      return;
    }

    const predictions = []
    for (const prediction of response.data.predictions) {
      predictions.push({
        location: prediction.location,
        datetime: convertUtcToLocal(prediction.datetime),
        route: prediction.route,
        number_of_vehicles_right_lane: prediction.number_of_vehicles_right_lane,
      })
    }

    vehicleCountPredictions.value = predictions;
    chartData.value = setChartData(
        'Number of vehicles per hour',
        vehicleCountPredictions.value.map(prediction => prediction.datetime),
        vehicleCountPredictions.value.map(prediction => prediction.number_of_vehicles_right_lane),
        predictions.map(prediction => prediction.number_of_vehicles_right_lane + 5)
    )
  } catch (e) {
    console.error(e);
  }
}

const onHoursToPredictChanged = async () => {
  loadVehicleCountPredictions();
}

const convertUtcToLocal = (datetimeUtc) => {
  const date = new Date(datetimeUtc);
  return date.toLocaleString();
}

const setChartData = (label, labels, data, stagingModelData = null) => {
  const documentStyle = getComputedStyle(document.documentElement);

  const mainModelData = {
    label: label,
    data: data,
    fill: false,
    borderColor: documentStyle.getPropertyValue('--cyan-500'),
    tension: 0.4
  };

  if (stagingModelData) {
    return {
      labels: labels,
      datasets: [
        mainModelData,
        {
          label: 'Staging Model',
          data: stagingModelData,
          fill: false,
          borderColor: documentStyle.getPropertyValue('--gray-500'),
          tension: 0.4
        }
      ]
    };
  }

  return {
    labels: labels,
    datasets: [ mainModelData ]
  };
};
const setChartOptions = () => {
  const documentStyle = getComputedStyle(document.documentElement);
  const textColor = documentStyle.getPropertyValue('--text-color');
  const textColorSecondary = documentStyle.getPropertyValue('--text-color-secondary');
  const surfaceBorder = documentStyle.getPropertyValue('--surface-border');

  return {
    maintainAspectRatio: false,
    aspectRatio: 0.6,
    plugins: {
      legend: {
        labels: {
          color: textColor
        }
      }
    },
    scales: {
      x: {
        ticks: {
          color: textColorSecondary
        },
        grid: {
          color: surfaceBorder
        }
      },
      y: {
        ticks: {
          color: textColorSecondary
        },
        grid: {
          color: surfaceBorder
        }
      }
    }
  };
};
</script>
<style scoped>
.chart-wrapper {
  position: relative;
}

.progress-container {
  display: flex;
  justify-content: center;
  align-items: center;
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 10;
}

.chart-wrapper .loading {
  opacity: 0.5;
}

.centered-input-number .p-inputnumber-input {
  text-align: center;
}

.map-container {
 height: 24rem;
 width: 100%;
 border-radius: 24px;
 overflow: hidden;
}

.travel-time {
  background-color: white;
  border-radius: 5px;
  padding: 2px 5px;
  font-size: 12px;
  font-weight: bold;
  text-align: center;
}

</style>
