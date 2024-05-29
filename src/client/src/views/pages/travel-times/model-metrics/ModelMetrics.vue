<template>
    <div class="card">
      <h4>Travel Time Model Metrics</h4>
      <Dropdown v-model="selectedLocation" :options="locations" :loading="isLoading" @change="onLocationSelected" filter optionLabel="name" placeholder="Select a location" class="w-full md:w-20rem">
        <template #value="slotProps">
          <div v-if="slotProps.value" class="flex align-items-center">{{ slotProps.value.name }}</div>
          <span v-else>{{ slotProps.placeholder }}</span>
        </template>
        <template #option="slotProps">
          <div class="flex align-items-center">
            <div>{{ slotProps.option.name }}</div>
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
                        <span class="block text-500 font-medium mb-3">MAE</span>
                        <div class="text-900 font-medium text-xl">{{ mae }}</div>
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
                        <span class="block text-500 font-medium mb-3">MSE</span>
                        <div class="text-900 font-medium text-xl">{{ mse }}</div>
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
                        <span class="block text-500 font-medium mb-3">EV</span>
                        <div class="text-900 font-medium text-xl">{{ ev }}</div>
                    </div>
                    <div class="flex align-items-center justify-content-center bg-cyan-100 border-round" style="width: 2.5rem; height: 2.5rem">
                        <i class="pi pi-chart-line text-cyan-500 text-xl"></i>
                    </div>
                </div>
                <span class="text-green-500 font-medium">+ 1% </span>
                <span class="text-500">since last</span>
            </div>
        </div>

      <!-- Validation Loss, Loss, Stopped Epoch, Restored Epoch cards -->
      <div class="col-12 lg:col-6 xl:col-3">
        <div class="card mb-0">
          <div class="flex justify-content-between mb-3">
            <div>
              <span class="block text-500 font-medium mb-3">Validation Loss</span>
              <div class="text-900 font-medium text-xl">{{ valLoss }}</div>
            </div>
            <div class="flex align-items-center justify-content-center bg-blue-100 border-round" style="width: 2.5rem; height: 2.5rem">
              <i class="pi pi-chart-line text-blue-500 text-xl"></i>
            </div>
          </div>
          <span class="text-green-500 font-medium">+ 1% </span>
          <span class="text-500">since last</span>
        </div>
      </div>
      <div class="col-12 lg:col-6 xl:col-3">
        <div class="card mb-0">
          <div class="flex justify-content-between mb-3">
            <div>
              <span class="block text-500 font-medium mb-3">Loss</span>
              <div class="text-900 font-medium text-xl">{{ loss }}</div>
            </div>
            <div class="flex align-items-center justify-content-center bg-orange-100 border-round" style="width: 2.5rem; height: 2.5rem">
              <i class="pi pi-chart-line text-orange-500 text-xl"></i>
            </div>
          </div>
          <span class="text-green-500 font-medium">+ 1% </span>
          <span class="text-500">since last</span>
        </div>
      </div>
      <div class="col-12 lg:col-6 xl:col-3">
        <div class="card mb-0">
          <div class="flex justify-content-between mb-3">
            <div>
              <span class="block text-500 font-medium mb-3">Stopped Epoch</span>
              <div class="text-900 font-medium text-xl">{{ stoppedEpoch }}</div>
            </div>
            <div class="flex align-items-center justify-content-center bg-cyan-100 border-round" style="width: 2.5rem; height: 2.5rem">
              <i class="pi pi-chart-line text-cyan-500 text-xl"></i>
            </div>
          </div>
          <span class="text-green-500 font-medium">+ 1% </span>
          <span class="text-500">since last</span>
        </div>
      </div>
      <div class="col-12 lg:col-6 xl:col-3">
        <div class="card mb-0">
          <div class="flex justify-content-between mb-3">
            <div>
              <span class="block text-500 font-medium mb-3">Restored Epoch</span>
              <div class="text-900 font-medium text-xl">{{ restoredEpoch }}</div>
            </div>
            <div class="flex align-items-center justify-content-center bg-cyan-100 border-round" style="width: 2.5rem; height: 2.5rem">
              <i class="pi pi-chart-line text-cyan-500 text-xl"></i>
            </div>
          </div>
          <span class="text-green-500 font-medium">+ 1% </span>
          <span class="text-500">since last</span>
        </div>
      </div>

        <!-- MAE, MSE, EV Metric Charts -->
        <div class="col-12">
          <div class="card">
            <div class="flex">
              <div class="flex-1 p-2">
                <HorizontalBarChart :chart-data="maeChartData" :chart-options="maeChartOptions" height-class="h-15rem" width-class="w-20rem"/>
              </div>
              <div class="flex-1 p-2">
                <HorizontalBarChart :chart-data="mseChartData" :chart-options="mseChartOptions" height-class="h-15rem" width-class="w-20rem" />
              </div>
              <div class="flex-1 p-2">
                <HorizontalBarChart :chart-data="evChartData" :chart-options="evChartOptions" height-class="h-15rem" width-class="w-20rem" />
              </div>
            </div>
          </div>
        </div>

        <!-- Validation Loss, Loss, Stopped Epoch, Restored Epoch Charts -->
        <div class="col-12">
          <div class="card">
            <div class="flex">
              <div class="flex-1 p-2">
                <HorizontalBarChart :chart-data="valLossChartData" :chart-options="valLossChartOptions" height-class="h-15rem" width-class="w-50rem"/>
              </div>
              <div class="flex-1 p-2">
                <HorizontalBarChart :chart-data="stoppedEpochChartData" :chart-options="stoppedEpochChartOptions" height-class="h-15rem" width-class="w-50rem" />
              </div>
            </div>
          </div>
        </div>
    </div>
    <Toast />
</template>
<script setup>
import { onMounted, ref } from 'vue';
import HorizontalBarChart from "@/views/components/HorizontalBarChart.vue";
import axios from "axios";
import { useToast } from "primevue/usetoast";

const toast = useToast();

const isLoading = ref(false);
const locations = ref([
  { name: 'Ljubljana - Koper', value: 'LJ_KP' },
  { name: 'Koper - Ljubljana', value: 'KP_LJ' },
  { name: 'Maribor - Ljubljana', value: 'MB_LJ' },
  { name: 'Ljubljana - Maribor', value: 'LJ_MB' },
  { name: 'Ljubljana - Karavanke', value: 'LJ_Karavanke' },
  { name: 'Karavanke - Ljubljana', value: 'Karavanke_LJ' },
  { name: 'LJ obv. zunanji krog', value: 'LJ_obv_zunanji_krog' },
  { name: 'LJ obv. notranji krog', value: 'LJ_obv_notranji_krog' },
  { name: 'Ljubljana MP Obrežje', value: 'LJ_MP_Obrezje' },
  { name: 'MP Obrežje - Ljubljana', value: 'MP_Obrezje_LJ' }
]);
const selectedLocation = ref(null);

const mae = ref('N/A');
const mse = ref('N/A');
const ev = ref('N/A');
const valLoss = ref('N/A');
const loss = ref('N/A');
const stoppedEpoch = ref('N/A');
const restoredEpoch = ref('N/A');

const maeChartData = ref(null);
const maeChartOptions = ref(null);
const mseChartData = ref(null);
const mseChartOptions = ref(null);
const evChartData = ref(null);
const evChartOptions = ref(null);

const valLossChartData = ref(null);
const valLossChartOptions = ref(null);
const stoppedEpochChartData = ref(null);
const stoppedEpochChartOptions = ref(null);

onMounted(() => {
  maeChartOptions.value = setMetricChartOptions();
  mseChartOptions.value = setMetricChartOptions();
  evChartOptions.value = setMetricChartOptions();
  valLossChartOptions.value = setMetricChartOptions();
  stoppedEpochChartOptions.value = setMetricChartOptions();
  selectedLocation.value = locations.value[0];
  fetchTravelTimeModelMetrics(selectedLocation.value.value);
});

const onLocationSelected = () => {
  fetchTravelTimeModelMetrics(selectedLocation.value.value);
};

const fetchTravelTimeModelMetrics = async (locationName) => {
  try {
    isLoading.value = true;

    const response = await axios.get(`${import.meta.env.VITE_API_BASE_URL}/travel-times/model-data/${locationName}`)
    if (!response.data) {
      isLoading.value = false;
      toast.add({ severity: 'error', summary: 'Oops', detail: 'Something went wrong...', life: 3000 })
      return
    }

    mae.value = parseFloat(response.data.data.metrics.MAE.toFixed(10));
    mse.value = parseFloat(response.data.data.metrics.MSE.toFixed(10));
    ev.value = parseFloat(response.data.data.metrics.EV.toFixed(10));
    valLoss.value = parseFloat(response.data.data.metrics.validation_loss.toFixed(10));
    loss.value = parseFloat(response.data.data.metrics.loss.toFixed(10));
    stoppedEpoch.value = parseFloat(response.data.data.metrics.stopped_epoch.toFixed(10));
    restoredEpoch.value = parseFloat(response.data.data.metrics.restored_epoch.toFixed(10));

    maeChartData.value = setMetricChartData('MAE', mae.value, '--blue-400');
    mseChartData.value = setMetricChartData('MSE', mse.value, '--orange-400');
    evChartData.value = setMetricChartData('EV', ev.value, '--purple-400');
    valLossChartData.value = setTwoMetricsChartData('Loss', 'Validation Loss', 'Loss', [valLoss.value, loss.value], ['--blue-400', '--orange-400']);
    stoppedEpochChartData.value = setTwoMetricsChartData('Epoch', 'Stopped Epoch', 'Restored Epoch', [stoppedEpoch.value, restoredEpoch.value], ['--blue-400', '--orange-400']);
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Oops', detail: 'Something went wrong...', life: 3000 })
  } finally {
    isLoading.value = false;
  }
}

const setMetricChartData = (label, metricValue, color) => {
  const documentStyle = getComputedStyle(document.documentElement);

  return {
    labels: [label],
    datasets: [
      {
        label: label,
        backgroundColor: documentStyle.getPropertyValue(color),
        borderColor: documentStyle.getPropertyValue(color),
        data: [metricValue]
      }
    ]
  };
};

const setTwoMetricsChartData = (title, label1, label2, values, colors) => {
  const documentStyle = getComputedStyle(document.documentElement);

  return {
    labels: [title],
    datasets: [
      {
        label: label1,
        backgroundColor: documentStyle.getPropertyValue(colors[0]),
        borderColor: documentStyle.getPropertyValue(colors[0]),
        data: [values[0]]
      },
      {
        label: label2,
        backgroundColor: documentStyle.getPropertyValue(colors[1]),
        borderColor: documentStyle.getPropertyValue(colors[1]),
        data: [values[1]]
      }
    ]
  };
};

const setMetricChartOptions = () => {
  const documentStyle = getComputedStyle(document.documentElement);
  const textColor = documentStyle.getPropertyValue('--text-color');
  const textColorSecondary = documentStyle.getPropertyValue('--text-color-secondary');
  const surfaceBorder = documentStyle.getPropertyValue('--surface-border');

  return {
    indexAxis: 'y',
    maintainAspectRatio: false,
    aspectRatio: 0.8,
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
          color: textColorSecondary,
          font: {
            weight: 500
          }
        },
        grid: {
          display: false,
          drawBorder: false
        }
      },
      y: {
        ticks: {
          color: textColorSecondary
        },
        grid: {
          color: surfaceBorder,
          drawBorder: false
        }
      }
    }
  };
}
</script>
