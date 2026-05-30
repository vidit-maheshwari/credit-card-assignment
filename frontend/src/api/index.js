import axios from 'axios';

const API_BASE = 'http://localhost:8009/api';

const api = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
});

// Statements
export const savePassword = (password) => api.post('/statements/password', { password });
export const getPassword = () => api.get('/statements/password');
export const ingestStatements = (password) => api.post('/statements/ingest', { password });
export const uploadStatement = (file, password) => {
  const formData = new FormData();
  formData.append('file', file);
  if (password) formData.append('password', password);
  return api.post('/statements/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};
export const getStatements = () => api.get('/statements/');
export const deleteStatement = (id) => api.delete(`/statements/${id}`);

// Transactions
export const getTransactions = (params) => api.get('/transactions/', { params });

// Analytics
export const getAvailableMonths = () => api.get('/analytics/months');
export const getMonthlyAnalytics = (month, bank) =>
  api.get('/analytics/monthly', { params: { month, bank } });
export const getTrends = (months, bank) =>
  api.get('/analytics/trends', { params: { months, bank } });

// Chat
export const sendChatMessage = (message) => api.post('/chat/', { message });

export default api;
