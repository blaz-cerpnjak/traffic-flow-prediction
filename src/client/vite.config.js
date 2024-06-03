import { fileURLToPath, URL } from 'node:url';

import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';

// https://vitejs.dev/config/
export default defineConfig(() => {
    return {
        plugins: [vue()],
        server: {
            proxy: {
                '/api/v1': {
                    target: 'https://traffic-flow-prediction-api-0-1-0.onrender.com',
                    changeOrigin: true,
                    secure: true, // True if your backend uses HTTPS
                    rewrite: (path) => path.replace(/^\/api\/v1/, '/api/v1'),
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
