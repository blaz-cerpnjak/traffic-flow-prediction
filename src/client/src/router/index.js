import { createRouter, createWebHashHistory } from 'vue-router';
import AppLayout from '@/layout/AppLayout.vue';

const router = createRouter({
    history: createWebHashHistory(),
    routes: [
        {
            path: '/',
            component: AppLayout,
            children: [
                {
                    path: '/',
                    name: 'travelTimes',
                    component: () => import('@/views/pages/travel-times/TravelTimes.vue')
                },
                {
                    path: '/travelTimes/:locationName',
                    name: 'travelTimeDetails',
                    component: () => import('@/views/pages/travel-times/TravelTimeDetails.vue'),
                    props: true
                },
                {
                    path: '/modelMetrics',
                    name: 'modelMetrics',
                    component: () => import('@/views/pages/travel-times/model-metrics/ModelMetrics.vue')
                },
                {
                    path: '/modelInfo',
                    name: 'modelInfo',
                    component: () => import('@/views/pages/travel-times/model-info/ModelInfo.vue')
                },
                {
                    path: '/traffic-density',
                    name: 'trafficDensity',
                    component: () => import('@/views/pages/traffic-density/TrafficDensity.vue')
                },
                {
                    path: '/traffic-density-model-metrics',
                    name: 'trafficDensityModelMetrics',
                    component: () => import('@/views/pages/traffic-density/model-metrics/ModelMetrics.vue')
                },
                {
                    path: '/traffic-density-model-info',
                    name: 'trafficDensityModelInfo',
                    component: () => import('@/views/pages/traffic-density/model-info/ModelInfo.vue')
                },
                {
                    path: '/model-experiments',
                    name: 'modelExperiments',
                    component: () => import('@/views/pages/model-experiments/ModelExperiments.vue')
                },
                {
                    path: '/model-experiments/:experimentId',
                    name: 'modelExperimentDetails',
                    component: () => import('@/views/pages/model-experiments/ModelExperimentDetails.vue'),
                    props: true
                },
                {
                    path: '/model-details/:modelName',
                    name: 'modelDetails',
                    component: () => import('@/views/pages/model-experiments/ModelDetails.vue'),
                    props: true
                },
                {
                    path: '/model-registry',
                    name: 'modelRegistry',
                    component: () => import('@/views/pages/model-registry/ModelsRegistry.vue')
                },
                {
                    path: '/data-quality-report',
                    name: 'evidentlyDataTests',
                    component: () => import('@/views/pages/reports/EvidentlyDataQualityReport.vue')
                },
                {
                    path: '/data-drift-report',
                    name: 'evidentlyDataDriftReport',
                    component: () => import('@/views/pages/reports/EvidentlyDataDriftReport.vue')
                },
                {
                    path: 'model-production-evaluations',
                    name: 'modelProductionEvaluations',
                    component: () => import('@/views/pages/model-production-evaluations/ModelProductionEvaluations.vue')
                }
            ]
        },
        {
            path: '/pages/notfound',
            name: 'notfound',
            component: () => import('@/views/pages/NotFound.vue')
        },

        {
            path: '/auth/login',
            name: 'login',
            component: () => import('@/views/pages/auth/Login.vue')
        },
        {
            path: '/auth/access',
            name: 'accessDenied',
            component: () => import('@/views/pages/auth/Access.vue')
        },
        {
            path: '/auth/error',
            name: 'error',
            component: () => import('@/views/pages/auth/Error.vue')
        }
    ]
});

export default router;
