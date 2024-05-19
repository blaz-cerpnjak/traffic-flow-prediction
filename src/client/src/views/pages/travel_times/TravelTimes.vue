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
</template>
<script setup>
import {onMounted, ref} from "vue";

const loading = ref(true)
const travelTimes = ref([])

const loadTravelTimes = async () => {
    loading.value = true

    // Simulate a delay
    await new Promise(resolve => setTimeout(resolve, 2000))

  travelTimes.value = [
      {
        destination: "Ljubljana - KP",
        minutes: 155,
        status: 'HIGH TRAFFIC'
      },
      {
        destination: "Ljubljana - MB",
        minutes: 120,
        status: 'MEDIUM TRAFFIC',
      },
      {
        destination: "Ljubljana - NM",
        minutes: 90,
        status: 'LOW TRAFFIC',
      },
      {
        destination: "Ljubljana - CE",
        minutes: 60,
        status: 'LOW TRAFFIC',
      },
      {
        destination: "Ljubljana - MS",
        minutes: 30
      },
      {
        destination: "Ljubljana - GO",
        minutes: 15
      },
      {
        destination: "Ljubljana - KP",
        minutes: 155
      },
      {
        destination: "Ljubljana - MB",
        minutes: 120
      },
      {
        destination: "Ljubljana - NM",
        minutes: 90
      },
      {
        destination: "Ljubljana - CE",
        minutes: 60
      },
      {
        destination: "Ljubljana - MS",
        minutes: 30
      },
      {
        destination: "Ljubljana - GO",
        minutes: 15
      },
      {
        destination: "Ljubljana - KP",
        minutes: 155
      },
      {
        destination: "Ljubljana - MB",
        minutes: 120
      },
      {
        destination: "Ljubljana - NM",
        minutes: 90
      },
      {
        destination: "Ljubljana - CE",
        minutes: 60
      },
      {
        destination: "Ljubljana - MS",
        minutes: 30
      },
      {
        destination: "Ljubljana - GO",
        minutes: 15
      },
      {
        destination: "Ljubljana - KP",
        minutes: 155
      },
      {
        destination: "Ljubljana - MB",
        minutes: 120
      },
      {
        destination: "Ljubljana - NM",
        minutes: 90
      },
      {
        destination: "Ljubljana - CE",
        minutes: 60
      },
      {
        destination: "Ljubljana - MS",
        minutes: 30
      },
    ]
    loading.value = false
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
