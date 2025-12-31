import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';
import { useAuthStore } from '../stores/authStore';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const { accessToken } = useAuthStore.getState();
    
    if (accessToken && config.headers) {
      config.headers.Authorization = `Bearer ${accessToken}`;
    }
    
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config;
    
    // Handle 401 errors
    if (error.response?.status === 401 && originalRequest) {
      const { refreshToken, logout, setAuth } = useAuthStore.getState();
      
      if (refreshToken) {
        try {
          const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
            refresh_token: refreshToken,
          });
          
          const { access_token, refresh_token, user } = response.data;
          setAuth(user, access_token, refresh_token);
          
          // Retry original request
          if (originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${access_token}`;
          }
          return api(originalRequest);
        } catch {
          logout();
        }
      } else {
        logout();
      }
    }
    
    return Promise.reject(error);
  }
);

// API functions
export const authApi = {
  login: (email: string, password: string) =>
    api.post('/auth/login', new URLSearchParams({ username: email, password }), {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    }),
  
  register: (data: { email: string; password: string; full_name: string }) =>
    api.post('/auth/register', data),
  
  me: () => api.get('/auth/me'),
  
  logout: () => api.post('/auth/logout'),
};

export const productsApi = {
  list: (params?: Record<string, unknown>) => api.get('/products', { params }),
  get: (id: number) => api.get(`/products/${id}`),
  create: (data: unknown) => api.post('/products', data),
  update: (id: number, data: unknown) => api.put(`/products/${id}`, data),
  delete: (id: number) => api.delete(`/products/${id}`),
  featured: () => api.get('/products/featured'),
  trending: () => api.get('/products/trending'),
};

export const ordersApi = {
  list: (params?: Record<string, unknown>) => api.get('/orders', { params }),
  get: (id: number) => api.get(`/orders/${id}`),
  create: (data: unknown) => api.post('/orders', data),
  updateStatus: (id: number, data: unknown) => api.patch(`/orders/${id}/status`, data),
  cancel: (id: number) => api.post(`/orders/${id}/cancel`),
};

export const analyticsApi = {
  sales: (days?: number) => api.get('/analytics/sales', { params: { days } }),
  customers: (days?: number) => api.get('/analytics/customers', { params: { days } }),
  products: (productId: number, days?: number) =>
    api.get(`/analytics/products/${productId}`, { params: { days } }),
  dashboard: () => api.get('/analytics/dashboard'),
};

export const recommendationsApi = {
  forUser: (userId: number, limit?: number) =>
    api.get(`/recommendations/user/${userId}`, { params: { limit } }),
  similar: (productId: number, limit?: number) =>
    api.get(`/recommendations/product/${productId}`, { params: { limit } }),
  trending: (limit?: number) =>
    api.get('/recommendations/trending', { params: { limit } }),
};

export default api;
