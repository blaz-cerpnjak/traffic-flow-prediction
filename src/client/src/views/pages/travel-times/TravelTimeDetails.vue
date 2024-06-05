<template>
  <div class="card">
    <h5>{{ destination }}</h5>
    <p>Napovedi potovalnih časov za naslednjih X ur za relacijo {{ destination }}. Izberite število ur za napoved.</p>
    <br />
    <InputNumber v-model="hoursToPredict" @input="onHoursToPredictChanged" showButtons buttonLayout="horizontal" class="centered-input-number" style="width: 3rem" :min="0" :max="168">
      <template #incrementbuttonicon>
        <span class="pi pi-plus" />
      </template>
      <template #decrementbuttonicon>
        <span class="pi pi-minus" />
      </template>
    </InputNumber>
    <br>
    <br>
    <div ref="mapContainer" class="map-container"></div>
  </div>
  <div class="card">
    <div class="chart-wrapper">
      <div class="progress-container" v-if="loading">
        <ProgressSpinner style="width: 3rem; height: 3rem;" />
      </div>
      <DataTable :value="travelTimes" scrollable scrollHeight="15rem" style="min-height: 15rem">
        <Column field="datetime" header="Datetime"></Column>
        <Column field="minutes" header="Travel Time"></Column>
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
</template>

<script setup>
import { onMounted, ref, toRefs } from 'vue';
import { useRoute } from 'vue-router';
import { useToast } from "primevue/usetoast";
import axios from "@/axios";
import mapboxgl from "mapbox-gl";
import "mapbox-gl/dist/mapbox-gl.css";
import routeLocations from "@/service/TravelTimeRoutes";

const route = useRoute();
const toast = useToast();
const { locationName } = toRefs(route.params);

const chartData = ref();
const chartOptions = ref();

const destination = ref('');
const loading = ref(false);
const travelTimes = ref([]);
const hoursToPredict = ref(7);

let map = null;
const mapContainer = ref(null);

onMounted(() => {
  mapboxgl.accessToken = import.meta.env.VITE_MAPBOX_TOKEN;

  map = new mapboxgl.Map({
    accessToken: import.meta.env.VITE_MAPBOX_TOKEN,
    container: mapContainer.value,
    style: 'mapbox://styles/mapbox/standard',
    center: [15.045314, 46.150356],
    zoom: 7
  });

  chartOptions.value = setChartOptions();
  fetchPredictions(locationName.value, hoursToPredict.value);
});

const fetchPredictions = async (locationName, hours) => {
  loading.value = true

  try {
    const response = await axios.get(`${import.meta.env.VITE_API_BASE_URL}/api/v1/travel-times/predict/${locationName}/${hours}`)
    if (!response.data) {
      toast.add({ severity: 'error', summary: 'Oops', detail: 'Something went wrong...', life: 3000 })
      return
    }

    destination.value = response.data.predictions[0].destination;

    const predictions = []
    for (const prediction of response.data.predictions) {
      predictions.push({
        destination: prediction.destination,
        datetime: convertUtcToLocal(prediction.datetime),
        locationName: prediction.location,
        minutes: prediction.minutes,
        trafficStatus: prediction.traffic_status
      })
    }

    travelTimes.value = predictions
    chartData.value = setChartData('Travel Time in Minutes', travelTimes.value.map(prediction => prediction.datetime), travelTimes.value.map(prediction => prediction.minutes))

    const lastPrediction = travelTimes.value[travelTimes.value.length - 1];
    drawRoute(lastPrediction.destination, lastPrediction.minutes);
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Oops', detail: 'Something went wrong...', life: 3000 })
  } finally {
    loading.value = false
  }
}

const onHoursToPredictChanged = async () => {
  fetchPredictions(locationName.value, hoursToPredict.value);
}

const convertUtcToLocal = (datetimeUtc) => {
  const date = new Date(datetimeUtc);
  return date.toLocaleString();
}

const setChartData = (label, labels, data) => {
  const documentStyle = getComputedStyle(document.documentElement);

  return {
    labels: labels,
    datasets: [
      {
        label: label,
        data: data,
        fill: false,
        borderColor: documentStyle.getPropertyValue('--cyan-500'),
        tension: 0.4
      }
    ]
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

const drawRoute = async (routeName, minutes) => {
    const index = routeLocations.findIndex(r => r.name === routeName);
    const r = routeLocations[index];
    const start = [r.start.longitude, r.start.latitude]
    const end = [r.end.longitude, r.end.latitude]

    const query = await fetch(`https://api.mapbox.com/directions/v5/mapbox/driving/${start[0]},${start[1]};${end[0]},${end[1]}?geometries=geojson&access_token=${mapboxgl.accessToken}`, { method: 'GET' });
    const json = await query.json();
    const data = json.routes[0];
    const route = data.geometry.coordinates;

    map.addLayer({
      id: `route-${index}`,
      type: 'line',
      source: {
        type: 'geojson',
        data: {
          type: 'Feature',
          properties: {},
          geometry: {
            type: 'LineString',
            coordinates: route
          }
        }
      },
      layout: {
        'line-join': 'round',
        'line-cap': 'round'
      },
      paint: {
        'line-color': '#40bae6',
        'line-width': 5
      }
    });

    const midpointIndex = Math.floor(route.length / 2);
    const midpoint = route[midpointIndex];

    new mapboxgl.Popup({ closeOnClick: false, closeButton: false })
        .setLngLat(midpoint)
        .setHTML(`<div class="travel-time">${minutes} min</div>`)
        .addTo(map);
}
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
