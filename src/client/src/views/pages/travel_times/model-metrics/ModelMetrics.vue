<template>
    <div class="card">
      <h4>Travel Time Predictions</h4>
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

        <!-- MAE, MSE, EV Metric Charts -->
        <div class="col-12">
          <div class="card">
            <div class="flex justify-content-between mb-4">
              <h5>Current Production Model Metrics</h5>
              <div>
                <Button icon="pi pi-ellipsis-v" class="p-button-text p-button-plain p-button-rounded" @click="$refs.menu3.toggle($event)"></Button>
                <Menu ref="menu3" :popup="true" :model="items"></Menu>
              </div>
            </div>
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
    </div>
</template>
<script setup>
import { onMounted, reactive, ref, watch } from 'vue';
import ProductService from '@/service/ProductService';
import { useLayout } from '@/layout/composables/layout';
import HorizontalBarChart from "@/views/components/HorizontalBarChart.vue";
import axios from "axios";
import { useToast } from "primevue/usetoast";

const { isDarkTheme } = useLayout();
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

const products = ref(null);
const lineData = reactive({
  labels: ['January', 'February', 'March', 'April', 'May', 'June', 'July'],
  datasets: [
    {
      label: 'First Dataset',
      data: [65, 59, 80, 81, 56, 55, 40],
      fill: false,
      backgroundColor: '#2f4860',
      borderColor: '#2f4860',
      tension: 0.4
    },
    {
      label: 'Second Dataset',
      data: [28, 48, 40, 19, 86, 27, 90],
      fill: false,
      backgroundColor: '#00bb7e',
      borderColor: '#00bb7e',
      tension: 0.4
    }
  ]
});
const items = ref([
  { label: 'Add New', icon: 'pi pi-fw pi-plus' },
  { label: 'Remove', icon: 'pi pi-fw pi-minus' }
]);
const lineOptions = ref(null);
const productService = new ProductService();

const mae = ref(0.0);
const mse = ref(0.0);
const ev = ref(0.0);

const maeChartData = ref(null);
const maeChartOptions = ref(null);
const mseChartData = ref(null);
const mseChartOptions = ref(null);
const evChartData = ref(null);
const evChartOptions = ref(null);

onMounted(() => {
  maeChartOptions.value = setMetricChartOptions();
  mseChartOptions.value = setMetricChartOptions();
  evChartOptions.value = setMetricChartOptions();
  productService.getProductsSmall().then((data) => (products.value = data));
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

    maeChartData.value = setMetricChartData('MAE', mae.value, '--blue-400');
    mseChartData.value = setMetricChartData('MSE', mse.value, '--orange-400');
    evChartData.value = setMetricChartData('EV', ev.value, '--purple-400');
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Oops', detail: 'Something went wrong...', life: 3000 })
  } finally {
    isLoading.value = false;
  }
}

const applyLightTheme = () => {
  lineOptions.value = {
    plugins: {
      legend: {
        labels: {
          color: '#495057'
        }
      }
    },
    scales: {
      x: {
        ticks: {
          color: '#495057'
        },
        grid: {
          color: '#ebedef'
        }
      },
      y: {
        ticks: {
          color: '#495057'
        },
        grid: {
          color: '#ebedef'
        }
      }
    }
  };
};

const applyDarkTheme = () => {
  lineOptions.value = {
    plugins: {
      legend: {
        labels: {
          color: '#ebedef'
        }
      }
    },
    scales: {
      x: {
        ticks: {
          color: '#ebedef'
        },
        grid: {
          color: 'rgba(160, 167, 181, .3)'
        }
      },
      y: {
        ticks: {
          color: '#ebedef'
        },
        grid: {
          color: 'rgba(160, 167, 181, .3)'
        }
      }
    }
  };
};

watch(
    isDarkTheme,
    (val) => {
      if (val) {
        applyDarkTheme();
      } else {
        applyLightTheme();
      }
    },
    { immediate: true }
);

const setMetricChartData = (label, metricValue, color) => {
  const documentStyle = getComputedStyle(document.documentElement);

  return {
    labels: [label],
    datasets: [
      {
        label: label,
        backgroundColor: documentStyle.getPropertyValue(color),
        borderColor: documentStyle.getPropertyValue(color),
        data: [metricValue || 0.0]
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
