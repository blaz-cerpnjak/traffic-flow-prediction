import { fileURLToPath, URL } from 'node:url';

import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';

// https://vitejs.dev/config/
export default defineConfig(() => {
    return {
        plugins: [vue()],
        server: {
            proxy: {
                '/api': {
                    target: 'https://traffic-flow-prediction-api-0-1-0.onrender.com/api',
                    changeOrigin: true,
                    secure: true, // Set to true if your backend uses HTTPS
                    rewrite: (path) => path.replace(/^\/api/, ''),
                },
            },
        },
        resolve: {
            alias: {
                '@': fileURLToPath(new URL('./src', import.meta.url))
            }
        }
    };
});
