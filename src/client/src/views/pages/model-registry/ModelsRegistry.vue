<template>
  <div class="card">
    <h5>Models Registry</h5>
    <p>Search for registered models.</p>
  </div>

  <div class="card">
    <InputText v-model="modelName" type="text" @update:model-value="searchModels" placeholder="Search by name" class="w-25rem" />
    <br>
    <br>
    <div class="chart-wrapper">
      <div class="progress-container" v-if="loading">
        <ProgressSpinner style="width: 3rem; height: 3rem;" />
      </div>
      <DataTable :value="models" scrollable scrollHeight="34rem" style="min-height: 15rem">
        <Column field="name" header="Name" sortable style="width: 30%"></Column>
        <Column field="latest_versions" header="Latest Version" sortable style="min-width: 10rem">
          <template #body="{ data }">
            <Tag :value="getLatestVersion(data)" style="background-color: #a1a1a1"/>
          </template>
        </Column>
        <Column field="creation_timestamp" sortable header="Created At">
          <template #body="{ data }">
            <span>{{ formatCreationTime(data) }}</span>
          </template>
        </Column>
        <Column field="last_update_timestamp" sortable header="Updated At">
          <template #body="{ data }">
            <span>{{ formatLastUpdated(data) }}</span>
          </template>
        </Column>
        <Column headerStyle="width: 5rem">
          <template #body="{ data }">
            <div class="flex flex-wrap gap-2">
              <Button @click="goToModelDetails(data)" type="button" icon="pi pi-search" rounded/>
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
const modelName = ref('');
const models = ref([]);

onMounted(() => {
  searchModels()
})

const searchModels = async () => {
  loading.value = true

  try {
    const response = await axios.post(`${import.meta.env.VITE_API_BASE_URL}/api/v1/models`, {
      name: modelName.value,
    })

    if (!response.data) {
      toast.add({ severity: 'error', summary: 'Oops', detail: 'Something went wrong...', life: 3000 })
      return
    }

    models.value = response.data.models
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Oops', detail: 'Something went wrong...', life: 3000 })
  } finally {
    loading.value = false
  }
}

const goToModelDetails = (data) => {
  const modelName = data.name
  router.push({ name: 'modelDetails', params: { modelName } });
}

const getLatestVersion = (rowData) => {
  if (!rowData.latest_versions) {
    return "?";
  }

  let maxVersion = 0;
  rowData.latest_versions.forEach(version => {
    const versionNumber = parseInt(version.version);
    if (versionNumber > maxVersion) {
      maxVersion = versionNumber;
    }
  });

  return maxVersion;
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
