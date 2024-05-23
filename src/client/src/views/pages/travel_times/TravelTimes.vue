<template>
  <div>
    <div v-if="loading || !travelTimes" class="card">
      <h5>Travel Times</h5>
      <p>Use this page to start from scratch and place your custom content.</p>
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
      <p>Use this page to start from scratch and place your custom content.</p>
      <DataTable :value="travelTimes" tableStyle="min-width: 50rem">
        <Column field="destination" header="Destination" sortable style="width: 50%"></Column>
        <Column field="minutes" header="Minutes" sortable style="width: 25%"></Column>
        <Column field="status" header="Status" style="min-width: 12rem">
          <template #body="{ data }">
            <Tag :value="data.status" :severity="getSeverity(data.status)" />
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

const toast = useToast();
const loading = ref(true)
const travelTimes = ref([])

const loadTravelTimes = async () => {
  loading.value = true

  try {
    const response = await axios.get(`${import.meta.env.VITE_API_BASE_URL}/travel-times/predict/`)
    if (!response.data) {
      toast.add({ severity: 'error', summary: 'Oops', detail: 'Something went wrong...', life: 3000 })
      return
    }

    travelTimes.value = response.data.predictions
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Oops', detail: 'Something went wrong...', life: 3000 })
  } finally {
    loading.value = false
  }
};

onMounted(() => {
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
