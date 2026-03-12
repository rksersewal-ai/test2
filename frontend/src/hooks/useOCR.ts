import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { ocrService } from '../services/ocr';
import type { OCRStatus } from '../api/types';

export function useOCRQueue(params: { page?: number; status?: OCRStatus }) {
  return useQuery({
    queryKey: ['ocr-queue', params],
    queryFn: () => ocrService.list(params),
    refetchInterval: 10_000,
  });
}
export function useOCRQueueStats() {
  return useQuery({ queryKey: ['ocr-stats'], queryFn: ocrService.stats, refetchInterval: 15_000 });
}
export function useRetryOCR() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ocrService.retry,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['ocr-queue'] }),
  });
}
