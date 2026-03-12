import apiClient from './apiClient';
import type { DashboardStats } from '../api/types';

export const dashboardService = {
  stats: () => apiClient.get<DashboardStats>('/dashboard/stats/').then((r) => r.data),
};
