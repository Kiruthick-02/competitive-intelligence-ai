import axios from 'axios';

const API = axios.create({
    baseURL: 'http://localhost:8000/api', // FastAPI Backend URL
});

export const getDashboardIntelligence = async (asin) => {
    const response = await API.get(`/intelligence/generate/${asin}`);
    return response.data;
};

export const getPriceHistory = async (asin) => {
    const response = await API.get(`/prices/${asin}`);
    return response.data;
};