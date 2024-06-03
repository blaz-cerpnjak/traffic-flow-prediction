<template>
  <div class="card">
    <h5>Latest Evidently Data Test Report</h5>
    <br>
    <Dropdown v-model="selectedReportType" :options="reportTypes" @change="loadLatestReport" optionLabel="name" placeholder="Select a City" class="w-full md:w-14rem mb-6" />
    <div v-if="tests">
      <div v-for="(test, index) in tests" :key="index" class="mb-4" :class="test.status.toLowerCase()">
        <Card :style="{ background: test.status === 'SUCCESS' ? '#edfaf4' : '#fff3f2' }">
          <template #title>
            <div class="flex items-center">
              <i v-if="test.status === 'SUCCESS'" class="pi pi-check-circle mr-3" style="color: #1caa7c"></i>
              <i v-else class="pi pi-times-circle mr-3" style="color: #ff4961"></i>
              <div>
                <h6 :style="{ color: test.status === 'SUCCESS' ? '#1caa7c' : '#dc2625' }"><b>{{ test.name }}</b></h6>
              </div>
            </div>
          </template>
          <template #content>
            <p class="m-0" style="color: #4a4f53">{{ test.description }}</p>
          </template>
        </Card>
      </div>
    </div>
    <div v-else>
      Loading...
    </div>
  </div>
  <Toast />
</template>
<script setup>
import { onMounted, ref } from "vue";
import axios from "@/axios";
import { useToast } from "primevue/usetoast";

const toast = useToast();
const tests = ref([]);
const loading = ref(false);

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

  loading.value = true

  console.log(selectedReportType.value.value)

  try {
    const response = await axios.get(`${import.meta.env.VITE_API_BASE_URL}/api/v1/${selectedReportType.value.value}/data-test-report/`)
    if (!response.data) {
      toast.add({ severity: 'error', summary: 'Oops', detail: 'Something went wrong...', life: 3000 })
      return
    }

    tests.value = response.data.tests
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Oops', detail: 'Something went wrong...', life: 3000 })
  } finally {
    loading.value = false
  }
};
</script>
<style scoped lang="scss">

</style>
