import apiClient from './apiClient';
import type { PaginatedResponse, OCRQueue, OCRStatus } from '../api/types';

export const ocrService = {
  list:  (params: { page?: number; status?: OCRStatus }) =>
    apiClient.get<PaginatedResponse<OCRQueue>>('/ocr-queue/', { params }).then((r) => r.data),
  stats: () =>
    apiClient.get<Record<string, number>>('/ocr-queue/stats/').then((r) => r.data),
  retry: (id: number) =>
    apiClient.post(`/ocr-queue/${id}/retry/`).then((r) => r.data),
};
