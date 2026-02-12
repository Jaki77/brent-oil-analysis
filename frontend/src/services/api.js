import axios from 'axios';
import moment from 'moment';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add timestamp to prevent caching
    config.params = {
      ...config.params,
      _t: moment().valueOf(),
    };
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    console.error('API Error:', error.response || error.message);
    
    // Handle specific error codes
    if (error.response) {
      switch (error.response.status) {
        case 401:
          // Handle unauthorized
          break;
        case 404:
          // Handle not found
          break;
        case 500:
          // Handle server error
          break;
        default:
          break;
      }
    }
    
    return Promise.reject(error);
  }
);

// API endpoints
export const priceAPI = {
  getPrices: (startDate, endDate, frequency = 'daily') => 
    api.get('/prices', { params: { start: startDate, end: endDate, frequency } }),
};

export const eventAPI = {
  getEvents: (type = 'all', startDate = null, endDate = null) => 
    api.get('/events', { params: { type, start: startDate, end: endDate } }),
  getEventTypes: () => api.get('/event-types'),
};

export const changePointAPI = {
  getChangePoints: (minProbability = 0.8) => 
    api.get('/change-points', { params: { min_probability: minProbability } }),
};

export const summaryAPI = {
  getSummary: () => api.get('/summary'),
};

export const volatilityAPI = {
  getVolatility: () => api.get('/volatility'),
};

export const healthAPI = {
  check: () => api.get('/health'),
};

export default api;