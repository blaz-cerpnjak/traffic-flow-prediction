<template>
  <div class="card">
    <h5>Runs</h5>
    <p>Mlflow runs for selected experiment.</p>
  </div>

  <Fieldset v-if="bestRunName" legend="🏅 Current Champion 🏅" class="mb-5">
    <div>
      <Tag :value="'MAE: ' + roundToFiveDecimals(bestRun.data.metrics.MAE)" severity="success" class="mb-1 mr-1" />
      <Tag :value="'MSE: ' + roundToFiveDecimals(bestRun.data.metrics.MSE)" severity="success" class="mb-1 mr-1" />
      <Tag :value="'EV: ' + roundToFiveDecimals(bestRun.data.metrics.EV)" severity="success" class="mb-1 mr-1" />
    </div>
    <br>
    <div>Name: <b>{{ bestRunName }}</b></div>
    <br>
    <div>Model name: <b>{{ getModelName(bestRun) }}</b></div>
    <br>
    <div>User: {{ getMlflowUser(bestRun) }}</div>
  </Fieldset>

  <div class="card">
    <DataTable :value="mlflowRuns" striped-rows scroll-height="40rem">
      <Column field="info.run_name" sortable header="Run Name"></Column>
      <Column field="data.metrics.MAE" header="Metrics" sortable  style="width: 15%">
        <template #body="{ data }">
          <div>
            <Tag :value="'MAE: ' + roundToFiveDecimals(data.data.metrics.MAE)" :severity="getSeverity(data, 'MAE')" class="mb-1 mr-1" />
          </div>
          <div>
            <Tag :value="'MSE: ' + roundToFiveDecimals(data.data.metrics.MSE)" :severity="getSeverity(data, 'MSE')" class="mb-1 mr-1" />
          </div>
          <div>
            <Tag :value="'EV: ' + roundToFiveDecimals(data.data.metrics.EV)" :severity="getSeverity(data, 'EV')" class="mb-1 mr-1" />
          </div>
        </template>
      </Column>
      <Column header="User" sortable style="width: 15%">
        <template #body="{ data }">
          <span>{{ getMlflowUser(data) }}</span>
        </template>
      </Column>
      <Column field="info.start_time" sortable header="Start Time" style="width: 20%">
        <template #body="{ data }">
         {{ new Date(data.info.start_time).toLocaleString() }}
        </template>
      </Column>
      <Column field="info.end_time" sortable header="End Time" style="width: 20%">
        <template #body="{ data }">
          {{ data.info.end_time ? new Date(data.info.end_time).toLocaleString() : 'Not Finished' }}
        </template>
      </Column>
      <Column field="info.status" sortable header="Status" style="width: 15%">
        <template #body="{ data }">
          <Tag :value="data.info.status" :severity="data.info.status === 'FINISHED' ? 'success' : 'warning'" />
        </template>
      </Column>
    </DataTable>
  </div>
</template>

<script setup>
import {onMounted, ref, toRefs} from 'vue';
import {useRoute} from 'vue-router';
import {useToast} from "primevue/usetoast";
import axios from "axios";

const route = useRoute();
const toast = useToast();
const { experimentId } = toRefs(route.params);

const loading = ref(false);
const mlflowRuns = ref([])
const bestRunName = ref();
const bestRun = ref();

onMounted(() => {
  loadRuns(experimentId.value)
})

const loadRuns = async (experimentId) => {
  loading.value = true;

  try {
    const response = await axios.get(`${import.meta.env.VITE_API_BASE_URL}/vehicle-counter/runs/${experimentId}/`)
    if (!response.data) {
      toast.add({ severity: 'error', summary: 'Oops', detail: 'Something went wrong...', life: 3000 })
      return
    }

    mlflowRuns.value = response.data.runs;
    findBestRun(response.data.runs);
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Oops', detail: 'Something went wrong...', life: 3000 });
  } finally {
    loading.value = false;
  }
}

const findBestRun = async (runs) => {
  let currentBestRun = null;
  let bestMAE = null;

  runs.forEach(run => {
    if (run.data.metrics.MAE && (!currentBestRun || run.data.metrics.MAE < bestMAE)) {
      currentBestRun = run;
      bestMAE = run.data.metrics.MAE;
    }
  });

  bestRunName.value = currentBestRun.info.run_name;
  bestRun.value = currentBestRun;
}

const getMlflowUser = (rowData) => {
  return rowData.data.tags["mlflow.user"]
}

const roundToFiveDecimals = (number) => {
  if (!number) {
    return "Unknown"
  }
  return Math.round(number * 1e5) / 1e5;
}

const getModelName = (run) => {
  const history = parseModelHistory(run.data);
  if (!history) {
    return 'Unknown';
  }
  return history[1].artifact_path;
}

const parseModelHistory = (data) => {
  const modelHistoryString = data.tags["mlflow.log-model.history"];
  return JSON.parse(modelHistoryString)
}

const getSeverity = (data, metric) => {
  if (!data.data.metrics) {
    return 'warning'
  }

  if (!data.data.metrics[metric]) {
    return 'warning'
  }

  if (data.info.run_name === bestRunName.value) {
    return 'success'
  }

  return 'info'
}

</script>

<style scoped lang="scss">

</style>
