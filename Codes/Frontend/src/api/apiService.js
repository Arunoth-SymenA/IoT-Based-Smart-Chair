import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

// This is your computer's local IP from Phase 3
const BASE_URL = 'http://10.139.105.94:5000';

const api = axios.create({ baseURL: BASE_URL });

// This automatically attaches your login token to every request
api.interceptors.request.use(async (config) => {
  const token = await AsyncStorage.getItem('token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export const signup = (name, email, password) =>
  api.post('/signup', { name, email, password });

export const login = (email, password) =>
  api.post('/login', { email, password });

export const getAnalytics = (date) =>
  api.get(`/analytics/${date}`);

export const getAvailableDates = () =>
  api.get('/available-dates');