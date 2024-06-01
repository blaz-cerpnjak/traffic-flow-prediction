<template>
  <div>
    <div class="card">
      <h5>Traffic Density</h5>
      <p>Travel predictions for {{ predictionsDate }}</p>
      <Dropdown v-model="selectedRoute" :options="routes" filter @change="loadVehicleCountPredictions" optionLabel="value" placeholder="Select a Route" class="w-full md:w-14rem">
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
      <br>
      <br>
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

const toast = useToast();

const loading = ref(true);

const routes = ref([]);
const selectedRoute = ref(null);

const vehicleCountPredictions = ref([]);
const predictionsDate = ref('N/A');
const hoursToPredict = ref(7);

const chartData = ref();
const chartOptions = ref();

onMounted(() => {
  const currentDate = new Date();
  currentDate.setHours(currentDate.getHours() + 1);
  predictionsDate.value = currentDate.toLocaleDateString() + ' ' + currentDate.toLocaleTimeString();

  loadRoutes()
  chartOptions.value = setChartOptions();
})

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

    loadVehicleCountPredictions(hoursToPredict.value ?? 7)
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
    const response = await axios.get(`${import.meta.env.VITE_API_BASE_URL}/api/v1/vehicle-counter/predict/${location}/${direction}/${hoursToPredict.value ?? 7}`)
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
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Oops', detail: 'Something went wrong...', life: 3000 })
  } finally {
    loading.value = false
  }
}

const onHoursToPredictChanged = async () => {
  loadVehicleCountPredictions();
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
</script>
<style>
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
</style>
