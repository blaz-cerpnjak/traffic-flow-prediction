<template>
  <div>
    <div v-if="loading || !travelTimes" class="card">
      <h5>Travel Times</h5>
      <p>Travel time predictions for {{ predictionsDate }}</p>
      <div class="card flex justify-content-center">
        <Slider v-model="sliderValue" :step="20" class="w-14rem" />
      </div>
      <DataTable :value="loading ? 7 : travelTimes" tableStyle="min-width: 50rem">
        <Column field="destination" header="Destination" sortable style="width: 50%">
          <template #body>
            <Skeleton v-if="loading"></Skeleton>
            <span v-else>{{ data.destination }}</span>
          </template>
        </Column>
        <Column field="minutes" header="Minutes" sortable style="width: 25%">
          <template #body>
            <Skeleton v-if="loading"></Skeleton>
            <span v-else>{{ data.minutes }}</span>
          </template>
        </Column>
        <Column field="status" header="Status" style="min-width: 12rem">
          <template #body="{ data }">
            <Tag :value="loading ? data.status : getSeverity(data.status)" />
          </template>
        </Column>
      </DataTable>
    </div>
    <div v-else class="card">
      <h5>Travel Times</h5>
      <p>Travel predictions for {{ predictionsDate }}</p>
      <DataTable :value="travelTimes">
        <Column field="destination" header="Destination" sortable style="width: 40%"></Column>
        <Column field="minutes" header="Minutes" sortable style="width: 25%"></Column>
        <Column field="status" header="Status" style="min-width: 10rem">
          <template #body="{ data }">
            <Tag :value="data.traffic_status" :severity="getSeverity(data.traffic_status)" />
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
  </div>

  <Toast />
</template>
<script setup>
import { onMounted, ref } from "vue";
import axios from "axios";
import { useToast } from "primevue/usetoast";
import { useRouter } from 'vue-router';

const toast = useToast();
const router = useRouter();

const loading = ref(true);
const travelTimes = ref([]);
const predictionsDate = ref('N/A');
const sliderValue = ref(0);

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
  const currentDate = new Date();
  currentDate.setHours(currentDate.getHours() + 1);
  predictionsDate.value = currentDate.toLocaleDateString() + ' ' + currentDate.toLocaleTimeString();
  loadTravelTimes()
})

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
