<template>
  <div class="card">
    <h5>Production Evaluations</h5>
    <br/>
    <Dropdown v-model="selectedReportType" :options="reportTypes" @change="loadEvaluations" optionLabel="name"
              placeholder="Select a Model Type" class="w-full md:w-15rem mb-6" />
    <br>
    <DataTable :value="evaluations">
      <Column field="location_name" header="Location" sortable style="width: 40%"></Column>
      <Column v-if="evaluations && evaluations.direction !== undefined" field="direction" header="Direction" sortable style="width: 25%">
        <template #body="{ data }">
          {{ data.direction }}
        </template>
      </Column>
      <Column field="datetime" header="Datetime" sortable style="width: 25%">
        <template #body="{ data }">
          {{ formatDate(data.datetime) }}
        </template>
      </Column>
      <Column field="mae" header="MAE" sortable style="width: 25%">
        <template #body="{ data }">
          <Tag :value="roundToFiveDecimals(data.mae)" severity="info" />
        </template>
      </Column>
      <Column field="mse" header="MSE" sortable style="width: 25%">
        <template #body="{ data }">
          <Tag :value="roundToFiveDecimals(data.mse)" severity="info" />
        </template>
      </Column>
      <Column field="ev" header="EV" sortable style="width: 25%">
        <template #body="{ data }">
          <Tag :value="roundToFiveDecimals(data.ev)" severity="info" />
        </template>
      </Column>
    </DataTable>
  </div>
  <Toast />
</template>

<script setup>
import {onMounted, ref} from "vue";
import axios from "@/axios";
import { useToast } from "primevue/usetoast";

const toast = useToast();

const loading = ref(false);
const reportTypes = ref([
  { name: 'Travel Times', value: 'travel-times' },
  { name: 'Vehicle Counters', value: 'vehicle-counters' },
])
const selectedReportType = ref(reportTypes.value[0])
const evaluations = ref([]);

onMounted(() => {
  loadEvaluations();
});

const loadEvaluations = async () => {
  if (!selectedReportType.value) {
    return;
  }

  try {
    const response = await axios.get(`${import.meta.env.VITE_API_BASE_URL}/api/v1/${selectedReportType.value.value}/evaluations/`)
    if (!response.data) {
      toast.add({ severity: 'error', summary: 'Oops', detail: 'Something went wrong...', life: 3000 })
      return
    }

    evaluations.value = response.data;
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Oops', detail: 'Something went wrong...', life: 3000 })
  } finally {
    loading.value = false
  }
};

const formatDate = (date) => {
  return new Date(date).toLocaleString();
}

const roundToFiveDecimals = (num) => {
  return Math.round((num + Number.EPSILON) * 100000) / 100000;
}

const checkDirectionField = () => {
  return evaluations.value && evaluations.value[0].direction !== undefined;
}

</script>

<style scoped lang="scss">

</style>
