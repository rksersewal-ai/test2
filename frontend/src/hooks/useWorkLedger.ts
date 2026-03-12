import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { workLedgerService, type WorkLedgerFilters } from '../services/workLedger';

export const WL_KEY = 'work-ledger';

export function useWorkLedger(filters: WorkLedgerFilters) {
  return useQuery({ queryKey: [WL_KEY, filters], queryFn: () => workLedgerService.list(filters) });
}
export function useWorkEntry(id: number) {
  return useQuery({ queryKey: [WL_KEY, id], queryFn: () => workLedgerService.get(id), enabled: id > 0 });
}
export function useCreateWorkEntry() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: workLedgerService.create,
    onSuccess: () => qc.invalidateQueries({ queryKey: [WL_KEY] }),
  });
}
