import axios from 'axios'
import router from '@/router'

const axiosInstance = axios.create({});

axiosInstance.interceptors.request.use(
    config => {
        const token = import.meta.env.VITE_API_KEY;

        if (token && token !== '') {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    error => {
        return Promise.reject(error);
    }
);

axiosInstance.interceptors.response.use(
    response => {
        return response;
    },
    error => {
        if (error.response && error.response.status === 401) {
            router.push('/auth/login');
        }
        return Promise.reject(error);
    }
);

export default axiosInstance;
