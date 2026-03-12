import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../api/client';
import type { OCRQueue, OCRResult, PaginatedResponse } from '../api/types';

interface OCRFilters {
  page?: number;
  status?: string;
}

export function useOCRQueue(filters: OCRFilters = {}) {
  return useQuery({
    queryKey: ['ocr-queue', filters],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (filters.status) params.set('status', filters.status);
      if (filters.page) params.set('page', String(filters.page));
      const { data } = await apiClient.get<PaginatedResponse<OCRQueue>>(`/ocr/queue/?${params}`);
      return data;
    },
    refetchInterval: 10_000, // poll every 10s for live status
  });
}

export function useOCRQueueStats() {
  return useQuery({
    queryKey: ['ocr-queue-stats'],
    queryFn: async () => {
      const { data } = await apiClient.get('/ocr/queue/stats/');
      return data as Record<string, number>;
    },
    refetchInterval: 15_000,
  });
}

export function useOCRResult(fileId: number) {
  return useQuery({
    queryKey: ['ocr-result', fileId],
    queryFn: async () => {
      const { data } = await apiClient.get<OCRResult>(`/ocr/results/?file=${fileId}`);
      return data;
    },
    enabled: !!fileId,
  });
}

export function useRetryOCR() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (queueId: number) =>
      apiClient.post(`/ocr/queue/${queueId}/retry/`).then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['ocr-queue'] }),
  });
}
