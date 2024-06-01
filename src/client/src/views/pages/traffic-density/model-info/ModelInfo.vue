<template>
  <div class="card">
    <h4>Vehicle Count Models Info</h4>
    <Dropdown v-model="selectedRoute" :options="routes" :loading="loading" @change="onRouteSelected" filter optionLabel="name" placeholder="Select a route" class="w-full md:w-20rem">
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
  </div>
  <div class="grid">
    <!-- MAE, MSE, EV Metric Cards -->
    <div class="col-12 lg:col-6 xl:col-4">
      <div class="card mb-0">
        <div class="flex justify-content-between mb-3">
          <div>
            <span class="block text-500 font-medium mb-3">Epochs</span>
            <div class="text-900 font-medium text-xl">{{ epochs }}</div>
          </div>
          <div class="flex align-items-center justify-content-center bg-blue-100 border-round" style="width: 2.5rem; height: 2.5rem">
            <i class="pi pi-chart-line text-blue-500 text-xl"></i>
          </div>
        </div>
        <span class="text-green-500 font-medium">+ 1% </span>
        <span class="text-500">since last</span>
      </div>
    </div>
    <div class="col-12 lg:col-6 xl:col-4">
      <div class="card mb-0">
        <div class="flex justify-content-between mb-3">
          <div>
            <span class="block text-500 font-medium mb-3">Validation Split</span>
            <div class="text-900 font-medium text-xl">{{ validationSplit }}</div>
          </div>
          <div class="flex align-items-center justify-content-center bg-orange-100 border-round" style="width: 2.5rem; height: 2.5rem">
            <i class="pi pi-chart-line text-orange-500 text-xl"></i>
          </div>
        </div>
        <span class="text-green-500 font-medium">+ 1% </span>
        <span class="text-500">since last</span>
      </div>
    </div>
    <div class="col-12 lg:col-6 xl:col-4">
      <div class="card mb-0">
        <div class="flex justify-content-between mb-3">
          <div>
            <span class="block text-500 font-medium mb-3">Monitor</span>
            <div class="text-900 font-medium text-xl">{{ monitor }}</div>
          </div>
          <div class="flex align-items-center justify-content-center bg-cyan-100 border-round" style="width: 2.5rem; height: 2.5rem">
            <i class="pi pi-chart-line text-cyan-500 text-xl"></i>
          </div>
        </div>
        <span class="text-green-500 font-medium">+ 1% </span>
        <span class="text-500">since last</span>
      </div>
    </div>
    <div class="col-12 lg:col-6 xl:col-4">
      <div class="card mb-0">
        <div class="flex justify-content-between mb-3">
          <div>
            <span class="block text-500 font-medium mb-3">Patience</span>
            <div class="text-900 font-medium text-xl">{{ patience }}</div>
          </div>
          <div class="flex align-items-center justify-content-center bg-cyan-100 border-round" style="width: 2.5rem; height: 2.5rem">
            <i class="pi pi-chart-line text-cyan-500 text-xl"></i>
          </div>
        </div>
        <span class="text-green-500 font-medium">+ 1% </span>
        <span class="text-500">since last</span>
      </div>
    </div>
    <div class="col-12 lg:col-6 xl:col-4">
      <div class="card mb-0">
        <div class="flex justify-content-between mb-3">
          <div>
            <span class="block text-500 font-medium mb-3">Optimizer</span>
            <div class="text-900 font-medium text-xl">{{ optimizerName }}</div>
          </div>
          <div class="flex align-items-center justify-content-center bg-cyan-100 border-round" style="width: 2.5rem; height: 2.5rem">
            <i class="pi pi-chart-line text-cyan-500 text-xl"></i>
          </div>
        </div>
        <span class="text-green-500 font-medium">+ 1% </span>
        <span class="text-500">since last</span>
      </div>
    </div>
    <div class="col-12 lg:col-6 xl:col-4">
      <div class="card mb-0">
        <div class="flex justify-content-between mb-3">
          <div>
            <span class="block text-500 font-medium mb-3">Optimizer Learning Rate</span>
            <div class="text-900 font-medium text-xl">{{ optimizerLearningRate }}</div>
          </div>
          <div class="flex align-items-center justify-content-center bg-cyan-100 border-round" style="width: 2.5rem; height: 2.5rem">
            <i class="pi pi-chart-line text-cyan-500 text-xl"></i>
          </div>
        </div>
        <span class="text-green-500 font-medium">+ 1% </span>
        <span class="text-500">since last</span>
      </div>
    </div>
    <div class="col-12 lg:col-6 xl:col-4">
      <div class="card mb-0">
        <div class="flex justify-content-between mb-3">
          <div>
            <span class="block text-500 font-medium mb-3">Restore Best Weights</span>
            <div class="text-900 font-medium text-xl">{{ restoreBestWeights }}</div>
          </div>
          <div class="flex align-items-center justify-content-center bg-cyan-100 border-round" style="width: 2.5rem; height: 2.5rem">
            <i class="pi pi-chart-line text-cyan-500 text-xl"></i>
          </div>
        </div>
        <span class="text-green-500 font-medium">+ 1% </span>
        <span class="text-500">since last</span>
      </div>
    </div>
  </div>
</template>
<script setup>
import { onMounted, ref } from 'vue';
import axios from "axios";
import { useToast } from "primevue/usetoast";

const toast = useToast();

const loading = ref(false);
const routes = ref([]);
const selectedRoute = ref();

const epochs = ref('N/A');
const validationSplit = ref('N/A');
const monitor = ref('N/A');
const patience = ref('N/A');
const optimizerName = ref('N/A');
const optimizerLearningRate = ref('N/A');
const restoreBestWeights = ref('N/A');

onMounted(() => {
  loadRoutes();
});

const onRouteSelected = () => {
  fetchVehicleCounterModelInfo();
};

const loadRoutes = async () => {
  loading.value = true

  try {
    const response = await axios.get(`${import.meta.env.VITE_API_BASE_URL}/vehicle-counter/routes`)
    if (!response.data) {
      toast.add({ severity: 'error', summary: 'Oops', detail: 'Something went wrong...', life: 3000 })
      return
    }

    routes.value = response.data.routes
    selectedRoute.value = routes.value[0]

    fetchVehicleCounterModelInfo();
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Oops', detail: 'Something went wrong...', life: 3000 })
  } finally {
    loading.value = false
  }
}

const fetchVehicleCounterModelInfo = async () => {
  if (!selectedRoute.value) {
    return;
  }

  const locationName = selectedRoute.value.location;
  const direction = selectedRoute.value.direction;

  try {
    loading.value = true;

    const response = await axios.get(`${import.meta.env.VITE_API_BASE_URL}/api/v1/vehicle-counter/model-data/${locationName}/${direction}`)
    if (!response.data) {
      loading.value = false;
      toast.add({ severity: 'error', summary: 'Oops', detail: 'Something went wrong...', life: 3000 })
      return
    }

    epochs.value = response.data.data.params.epochs;
    validationSplit.value = response.data.data.params.validation_split;
    monitor.value = response.data.data.params.monitor;
    patience.value = response.data.data.params.patience;
    optimizerName.value = response.data.data.params.opt_name;
    optimizerLearningRate.value = parseFloat(response.data.data.params.opt_learning_rate).toFixed(4);
    restoreBestWeights.value = response.data.data.params.restore_best_weights;
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Oops', detail: 'Something went wrong...', life: 3000 })
  } finally {
    loading.value = false;
  }
};
</script>
