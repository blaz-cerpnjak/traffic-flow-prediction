<template>
  <div class="card" style="height: 100rem;">
    <iframe
        :srcdoc="htmlContent"
        frameborder="0"
        allowfullscreen
        style="width: 100%; height: 100%;"
    ></iframe>
  </div>
  <Toast />
</template>
<script setup>
import { onMounted, ref } from "vue";
import axios from "@/axios";
import { useToast } from "primevue/usetoast";

const toast = useToast();
const loading = ref(false);
const htmlContent = ref();

const reportTypes = ref([
  { name: 'Travel Times', value: 'travel-times' },
  { name: 'Vehicle Counters', value: 'vehicle-counters' },
])
const selectedReportType = ref(reportTypes.value[0])

onMounted(() => {
  loadLatestReport();
})

const loadLatestReport = async () => {
  if (!selectedReportType.value) {
    return;
  }

  console.log(selectedReportType.value.value)

  try {
    const response = await axios.get(`${import.meta.env.VITE_API_BASE_URL}/api/v1/${selectedReportType.value.value}/data-drift-report/`)
    if (!response.data) {
      toast.add({ severity: 'error', summary: 'Oops', detail: 'Something went wrong...', life: 3000 })
      return
    }

    htmlContent.value = response.data.html;
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Oops', detail: 'Something went wrong...', life: 3000 })
  } finally {
    loading.value = false
  }
};
</script>
<style scoped lang="scss">

</style>
