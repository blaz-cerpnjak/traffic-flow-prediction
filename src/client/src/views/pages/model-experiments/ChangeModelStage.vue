<template>
  <div class="card flex justify-content-center">
    <Dialog v-model:visible="visible" modal header="Change Model Stage" :style="{ width: '45rem' }">
      <div class="flex align-items-center mb-5">
        <span class="p-text-secondary block mr-4">Model Name:</span>
        <span><b>{{ modelData.name ?? 'Unknown' }}</b></span>
      </div>

      <div class="flex align-items-center">
        <span class="p-text-secondary mr-4">Model Stage:</span>
        <Dropdown v-model="selectedStage" :options="stages" optionLabel="name" placeholder="Select a Stage" class="w-full md:w-14rem">
          <template #value="slotProps">
            <div v-if="slotProps.value" class="flex align-items-center">
              <Tag :value="slotProps.value.value" :style="{ backgroundColor: getModelStageColor(slotProps.value.name) }" />
            </div>
            <span v-else>
            {{ slotProps.placeholder }}
          </span>
          </template>
          <template #option="slotProps">
            <div class="flex align-items-center">
              <Tag :value="slotProps.option.value" :style="{ backgroundColor: getModelStageColor(slotProps.option.name) }" />
            </div>
          </template>
        </Dropdown>
      </div>
      
      <div class="flex justify-content-end gap-2">
        <Button type="button" label="Cancel" severity="secondary" @click="visible = false"></Button>
        <Button type="button" label="Apply" @click="changeModelStage"></Button>
      </div>
    </Dialog>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useToast } from "primevue/usetoast";
import axios from "@/axios";

const stages = ref([
  { name: 'Production', value: 'production' },
  { name: 'Staging', value: 'staging' },
  { name: 'Archived', value: 'archived' },
  { name: 'None', value: 'none' }
]);

const toast = useToast();
const emit = defineEmits(['changed']);

const visible = ref(false);
const modelData = ref();
const selectedStage = ref(stages.value[0]);

const changeModelStage = async () => {
  if (!modelData.value) {
    toast.add({ severity: 'error', summary: 'Oops', detail: 'Model data is missing...', life: 3000 })
    return;
  }

  if (!selectedStage.value) {
    toast.add({ severity: 'error', summary: 'Oops', detail: 'Please select a stage...', life: 3000 })
    return;
  }

  try {
    await axios.post(`${import.meta.env.VITE_API_BASE_URL}/api/v1/change-model-stage`, {
      model_name: modelData.value.name,
      version: modelData.value.version,
      stage: selectedStage.value.value
    });

    toast.add({ severity: 'success', summary: 'Success', detail: 'Model stage changed successfully', life: 3000 })
    emit('changed');
    visible.value = false;
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Oops', detail: 'Something went wrong...', life: 3000 })
  }
}

const showDialog = (model) => {
  modelData.value = model;
  selectedStage.value = stages.value.find(stage => stage.name === model.current_stage);
  visible.value = true;
};

const getModelStageColor = (stage) => {
  if (stage === 'None') return '#a1a1a1'
  if (stage === 'Archived') return '#595959'
  if (stage === 'Staging') return 'rgba(255,204,0,0.84)'
  if (stage === 'Production') return '#87d068'
  return 'info'
}

defineExpose({
  showDialog
});
</script>

<style scoped lang="scss">

</style>
