<template>
  <div class="card">
    <h5>{{ destination }}</h5>
    <p>Napovedi potovalnih časov za naslednjih X ur za relacijo {{ destination }}. Izberite število ur za napoved.</p>
    <br />
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
      <DataTable :value="travelTimes" scrollable scrollHeight="15rem" style="min-height: 15rem">
        <Column field="datetime" header="Datetime"></Column>
        <Column field="minutes" header="Travel Time"></Column>
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
</template>

<script setup>
import { onMounted, ref, toRefs } from 'vue';
import { useRoute } from 'vue-router';
import { useToast } from "primevue/usetoast";
import axios from "axios";

const route = useRoute();
const toast = useToast();
const { locationName } = toRefs(route.params);

const chartData = ref();
const chartOptions = ref();

const destination = ref('');
const loading = ref(false);
const travelTimes = ref([]);
const hoursToPredict = ref(7);

onMounted(() => {
  chartOptions.value = setChartOptions();
  fetchPredictions(locationName.value, hoursToPredict.value);
});

const fetchPredictions = async (locationName, hours) => {
  loading.value = true

  try {
    const response = await axios.get(`${import.meta.env.VITE_API_BASE_URL}/api/v1/travel-times/predict/${locationName}/${hours}`)
    if (!response.data) {
      toast.add({ severity: 'error', summary: 'Oops', detail: 'Something went wrong...', life: 3000 })
      return
    }

    destination.value = response.data.predictions[0].destination;

    const predictions = []
    for (const prediction of response.data.predictions) {
      predictions.push({
        destination: prediction.destination,
        datetime: convertUtcToLocal(prediction.datetime),
        locationName: prediction.location,
        minutes: prediction.minutes,
        trafficStatus: prediction.traffic_status
      })
    }

    travelTimes.value = predictions
    chartData.value = setChartData('Travel Time in Minutes', travelTimes.value.map(prediction => prediction.datetime), travelTimes.value.map(prediction => prediction.minutes))
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Oops', detail: 'Something went wrong...', life: 3000 })
  } finally {
    loading.value = false
  }
}

const onHoursToPredictChanged = async () => {
  fetchPredictions(locationName.value, hoursToPredict.value);
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
