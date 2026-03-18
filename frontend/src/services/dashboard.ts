import apiClient from './apiClient';

export const dashboardService = {
  stats: () => apiClient.get('/dashboard/stats/').then((r) => r.data),
};
