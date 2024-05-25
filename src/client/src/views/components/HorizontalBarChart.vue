<template>
  <div class="card">
    <Chart type="bar" :data="chartData" :options="chartOptions" :class="[heightClass, widthClass]"  />
  </div>
</template>
<script setup>
defineProps({
  chartData: {
    type: Object,
    required: true
  },
  chartOptions: {
    type: Object,
    required: true
  },
  heightClass: {
    type: String,
    default: 'h-30rem'
  },
  widthClass: {
    type: String,
    default: ''
  }
});
</script>
