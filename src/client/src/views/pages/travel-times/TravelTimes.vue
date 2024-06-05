<template>
  <div class="card">
    <h5>Travel Times</h5>
    <p>Travel predictions for {{ predictionsDate }}</p>
    <div ref="mapContainer" class="map-container"></div>
    <br>
    <br>
    <DataTable :value="loading ? 7 : travelTimes" tableStyle="min-width: 50rem">
      <Column field="destination" header="Destination" sortable style="width: 50%">
        <template #body="{ data }">
          <Skeleton v-if="loading"></Skeleton>
          <span v-else>{{ data.destination }}</span>
        </template>
      </Column>
      <Column field="minutes" header="Minutes" sortable style="width: 25%">
        <template #body="{ data }">
          <Skeleton v-if="loading"></Skeleton>
          <span v-else>{{ data.minutes }}</span>
        </template>
      </Column>
      <Column field="status" header="Status" style="min-width: 12rem">
        <template #body="{ data }">
          <Skeleton v-if="loading"></Skeleton>
          <Tag v-else :value="data.traffic_status" :severity="getSeverity(data.traffic_status)" />
        </template>
      </Column>
      <Column headerStyle="width: 5rem">
        <template #body="{ data }">
          <div class="flex flex-wrap gap-2">
            <Button @click="goToTravelTimeDetails(data)" type="button" icon="pi pi-search" rounded/>
          </div>
        </template>
      </Column>
    </DataTable>
  </div>

  <Toast />
</template>
<script setup>
import { onMounted, ref } from "vue";
import axios from "@/axios";
import { useToast } from "primevue/usetoast";
import { useRouter } from 'vue-router';
import mapboxgl from "mapbox-gl";
import "mapbox-gl/dist/mapbox-gl.css";
import routeLocations from "@/service/TravelTimeRoutes";

const toast = useToast();
const router = useRouter();

const loading = ref(true);
const travelTimes = ref([]);
const predictionsDate = ref('N/A');

let map = null;
const mapContainer = ref(null);

const loadTravelTimes = async () => {
  loading.value = true

  try {
    const response = await axios.get(`${import.meta.env.VITE_API_BASE_URL}/api/v1/travel-times/predict/`)
    if (!response.data) {
      toast.add({ severity: 'error', summary: 'Oops', detail: 'Something went wrong...', life: 3000 })
      return
    }

    const predictions = []
    response.data.predictions.forEach(prediction => {
      if (prediction) {
        predictions.push(prediction[0])
      }
    })

    travelTimes.value = predictions
    drawRoutes(travelTimes.value);
  } catch (error) {
    console.log(error)
    toast.add({ severity: 'error', summary: 'Oops', detail: 'Something went wrong...', life: 3000 })
  } finally {
    loading.value = false
  }
};

const goToTravelTimeDetails = (data) => {
  const locationName = data.location
  router.push({ name: 'travelTimeDetails', params: { locationName } });
}

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

  const currentDate = new Date();
  currentDate.setHours(currentDate.getHours() + 1);
  predictionsDate.value = currentDate.toLocaleDateString() + ' ' + currentDate.toLocaleTimeString();
  loadTravelTimes()
})

const drawRoutes = async (travelTimes) => {
  for (const index in routeLocations) {
    const r = routeLocations[index];
    const start = [r.start.longitude, r.start.latitude]
    const end = [r.end.longitude, r.end.latitude]

    const query = await fetch(`https://api.mapbox.com/directions/v5/mapbox/driving/${start[0]},${start[1]};${end[0]},${end[1]}?geometries=geojson&access_token=${mapboxgl.accessToken}`, { method: 'GET' });
    const json = await query.json();
    const data = json.routes[0];
    const route = data.geometry.coordinates;

    let travelTime = "?"
    if (travelTimes) {
      for (const t of travelTimes) {
        if (t.destination === r.name) {
          travelTime = t.minutes
          break
        }
      }
    }

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
        'line-color': r.color,
        'line-width': 5
      }
    });

    const midpointIndex = Math.floor(route.length / 2);
    const midpoint = route[midpointIndex];

    new mapboxgl.Popup({ closeOnClick: false, closeButton: false })
        .setLngLat(midpoint)
        .setHTML(`<div class="travel-time">${travelTime} min</div>`)
        .addTo(map);
  }
}

const redirectToCoordinatesAndZoomOut = (longitude, latitude, zoomLevel) => {
  map.flyTo({
    center: [longitude, latitude],
    zoom: zoomLevel,
    essential: true
  });
}

const getSeverity = (status) => {
  switch (status) {
    case 'HIGH TRAFFIC':
      return 'danger';

    case 'LOW TRAFFIC':
      return 'success';

    case 'MEDIUM TRAFFIC':
      return 'warning';

    default:
      return null;
  }
}
</script>

<style scoped>
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
