<script setup>
import { ref } from 'vue';

import AppMenuItem from './AppMenuItem.vue';

const model = ref([
    {
        label: 'Travel Times',
        items: [
            { label: 'Predictions', icon: 'pi pi-fw pi-car', to: '/' },
            { label: 'Model Metrics', icon: 'pi pi-fw pi-chart-bar', to: '/modelMetrics' },
            { label: 'Other Model Info', icon: 'pi pi-fw pi-info-circle', to: '/modelInfo' }
        ]
    },
    {
      label: 'Traffic Density',
      items: [
        { label: 'Predictions', icon: 'pi pi-fw pi-car', to: '/traffic-density' },
        { label: 'Model Metrics', icon: 'pi pi-fw pi-chart-bar', to: '/traffic-density-model-metrics' },
        { label: 'Other Model Info', icon: 'pi pi-fw pi-info-circle', to: '/traffic-density-model-info' },
      ]
    },
  {
    label: 'Experiments',
    items: [
        { label: 'Experiments', icon: 'pi pi-fw pi-chart-bar', to: '/model-experiments' }
    ]
  }
]);
</script>

<template>
    <ul class="layout-menu">
        <template v-for="(item, i) in model" :key="item">
            <app-menu-item v-if="!item.separator" :item="item" :index="i"></app-menu-item>
            <li v-if="item.separator" class="menu-separator"></li>
        </template>
    </ul>
</template>

<style lang="scss" scoped></style>
