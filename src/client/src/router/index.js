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
                    component: () => import('@/views/pages/travel_times/TravelTimes.vue')
                },
                {
                    path: '/travelTimes/:locationName',
                    name: 'travelTimeDetails',
                    component: () => import('@/views/pages/travel_times/TravelTimeDetails.vue'),
                    props: true
                },
                {
                    path: '/modelMetrics',
                    name: 'modelMetrics',
                    component: () => import('@/views/pages/travel_times/model-metrics/ModelMetrics.vue')
                },
                {
                    path: '/modelInfo',
                    name: 'modelInfo',
                    component: () => import('@/views/pages/travel_times/model-info/ModelInfo.vue')
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
