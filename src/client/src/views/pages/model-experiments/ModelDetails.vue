<template>
  <div class="card">
    <h5>Model Details</h5>
    <p>Details about selected model <b>{{ modelName }}</b></p>
  </div>

  <div class="card">
    <div class="chart-wrapper">
      <div class="progress-container" v-if="loading">
        <ProgressSpinner style="width: 3rem; height: 3rem;" />
      </div>
      <DataTable :value="modelHistory" v-model:selection="selectedModel" @rowSelect="onModelSelected" selectionMode="single"  scrollable scrollHeight="40rem" >
        <Column field="version" header="Version" sortable></Column>
        <Column field="current_stage" header="Current Stage" sortable>
          <template #body="{ data }">
            <Tag :value="data.current_stage" :style="{ backgroundColor: getModelStageColor(data.current_stage) }" />
          </template>
        </Column>
        <Column field="status" header="Status" sortable>
          <template #body="{ data }">
            <Tag :value="data.status" :style="{ backgroundColor: '#87d068'} " />
          </template>
        </Column>
        <Column field="creation_timestamp" header="Created At">
          <template #body="{ data }">
            {{ new Date(data.creation_timestamp).toLocaleString() }}
          </template>
        </Column>
        <Column field="last_updated_timestamp" header="Updated At">
          <template #body="{ data }">
            {{ new Date(data.last_updated_timestamp).toLocaleString() }}
          </template>
        </Column>
      </DataTable>
    </div>
  </div>

  <Toast />
  <ChangeModelStage ref="changeModelStageDialog" @changed="loadModelHistory"  />
</template>

<script setup>
import { onMounted, ref, toRefs } from "vue";
import { useRoute } from "vue-router";
import { useToast } from "primevue/usetoast";
import axios from "@/axios";
import ChangeModelStage from "@/views/pages/model-experiments/ChangeModelStage.vue";

const route = useRoute();
const toast = useToast();
const { modelName } = toRefs(route.params);

const loading = ref(false);
const modelHistory = ref([]);
const selectedModel = ref(null);
const changeModelStageDialog = ref();

onMounted(() => {
  loadModelHistory()
})

const loadModelHistory = async () => {
  loading.value = true

  try {
    const response = await axios.get(`${import.meta.env.VITE_API_BASE_URL}/api/v1/models/${modelName.value}`)
    if (!response.data) {
      toast.add({ severity: 'error', summary: 'Oops', detail: 'Something went wrong...', life: 3000 })
      return
    }

    modelHistory.value = response.data
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Oops', detail: 'Something went wrong...', life: 3000 })
  } finally {
    loading.value = false;
  }
}

const getModelStageColor = (stage) => {
  if (stage === 'None') return '#a1a1a1'
  if (stage === 'Archived') return '#595959'
  if (stage === 'Staging') return 'rgba(255,204,0,0.84)'
  if (stage === 'Production') return '#87d068'
  return 'info'
}

const onModelSelected = () => {
  changeModelStageDialog.value.showDialog(selectedModel.value)
}

</script>

<style scoped>
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
