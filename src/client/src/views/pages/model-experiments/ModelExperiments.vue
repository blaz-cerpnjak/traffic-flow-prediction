<template>
  <div class="card">
    <h5>Model Training Experiments</h5>
    <p>Search for training models experiments.</p>
  </div>

  <div class="card">
    <InputText v-model="experimentName" type="text" @update:model-value="searchExperiments" placeholder="Search by name" class="w-25rem" />
    <Dropdown v-model="selectedType" :options="types" @change="searchExperiments" optionLabel="name" placeholder="Select a Filter" class="w-full ml-3 md:w-14rem">
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
    <br>
    <br>
    <div class="chart-wrapper">
      <div class="progress-container" v-if="loading">
        <ProgressSpinner style="width: 3rem; height: 3rem;" />
      </div>
      <DataTable :value="experiments" scrollable scrollHeight="34rem" style="min-height: 15rem">
        <Column field="experiment_id" sortable header="ID"></Column>
        <Column field="name" header="Name" sortable style="width: 30%"></Column>
        <Column field="lifecycle_stage" header="Status" style="min-width: 10rem">
          <template #body="{ data }">
            <Tag :value="data.lifecycle_stage" :severity="getSeverity(data.lifecycle_stage)" />
          </template>
        </Column>
        <Column field="creation_time" sortable header="Created At">
          <template #body="{ data }">
            <span>{{ formatCreationTime(data) }}</span>
          </template>
        </Column>
        <Column field="last_update_time" sortable header="Updated At">
          <template #body="{ data }">
            <span>{{ formatLastUpdated(data) }}</span>
          </template>
        </Column>
        <Column headerStyle="width: 5rem">
          <template #body="{ data }">
            <div class="flex flex-wrap gap-2">
              <Button @click="goToExperimentDetails(data)" type="button" icon="pi pi-search" rounded/>
            </div>
          </template>
        </Column>
      </DataTable>
    </div>
  </div>

  <Toast />
</template>

<script setup>

import { onMounted, ref } from "vue";
import axios from "@/axios";
import { useToast } from "primevue/usetoast";
import moment from 'moment';
import { useRouter } from "vue-router";

const toast = useToast();
const router = useRouter();

const loading = ref(false);
const experimentName = ref('');
const experiments = ref([]);

const types = [
  { name: 'All', value: '3' },
  { name: 'Active', value: '1' },
  { name: 'Deleted', value: '2' },
];
const selectedType = ref(types[0]);

onMounted(() => {
  searchExperiments()
})

const searchExperiments = async () => {
  loading.value = true

  try {
    const response = await axios.post(`${import.meta.env.VITE_API_BASE_URL}/api/v1/vehicle-counter/search-experiments/`, {
      name: experimentName.value,
      type: selectedType.value.value,
    })

    if (!response.data) {
      toast.add({ severity: 'error', summary: 'Oops', detail: 'Something went wrong...', life: 3000 })
      return
    }

    experiments.value = response.data.experiments
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Oops', detail: 'Something went wrong...', life: 3000 })
  } finally {
    loading.value = false
  }
}

const goToExperimentDetails = (data) => {
  const experimentId = data.experiment_id
  router.push({ name: 'modelExperimentDetails', params: { experimentId } });
}

const getSeverity = (status) => {
  switch (status) {
    case 'active':
      return 'success';

    case 'deleted':
      return 'danger';

    case 'inactive':
      return 'warning';

    default:
      return null;
  }
}

const formatCreationTime = (rowData) => {
  return moment(rowData.creation_time).format('DD.MM.YYYY  HH:mm');
}

const formatLastUpdated = (rowData) => {
  return moment(rowData.last_update_time).format('DD.MM.YYYY HH:mm');
}

</script>

<style scoped lang="scss">
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
</style>
