import apiClient from './apiClient';
import type { PaginatedResponse } from '../api/types';

export type OCRStatus = 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled';

export interface OCRQueue {
  id: number;
  document: number;
  status: OCRStatus;
  confidence_score?: number;
  total_pages?: number;
  created_at?: string;
}
export const ocrService = {
  list:  (params: { page?: number; status?: OCRStatus }) =>
    apiClient.get<PaginatedResponse<OCRQueue>>('/ocr/queue/', { params }).then((r) => r.data),
  stats: () =>
    apiClient.get<Record<string, number>>('/ocr/queue/stats/').then((r) => r.data),
  retry: (id: number) =>
    apiClient.post(`/ocr/queue/${id}/retry/`).then((r) => r.data),
};
