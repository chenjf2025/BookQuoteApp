import axios from 'axios';

const api = axios.create({
    baseURL: import.meta.env.DEV ? 'http://localhost:8000/api/h5' : '/api/h5',
});

api.interceptors.request.use((config) => {
    const token = localStorage.getItem('h5_token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

export default api;
