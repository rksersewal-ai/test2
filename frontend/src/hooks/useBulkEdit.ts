// =============================================================================
// FILE: frontend/src/hooks/useBulkEdit.ts
// SPRINT 3 — Feature #6: Bulk Edit UI
// PURPOSE : Manages row selection state for DocumentListPage table.
//           Supports individual toggle, range select (shift-click friendly),
//           select-all (current page), and clear.
// =============================================================================
import { useState, useCallback } from 'react';

interface UseBulkEditResult {
  selectedIds:      number[];
  isSelected:       (id: number) => boolean;
  toggleRow:        (id: number) => void;
  selectAll:        (ids: number[]) => void;
  clearSelection:   () => void;
  toggleSelectAll:  (ids: number[]) => void;
  selectionCount:   number;
}

export function useBulkEdit(): UseBulkEditResult {
  const [selectedIds, setSelectedIds] = useState<number[]>([]);

  const isSelected = useCallback(
    (id: number) => selectedIds.includes(id),
    [selectedIds]
  );

  const toggleRow = useCallback((id: number) => {
    setSelectedIds(prev =>
      prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]
    );
  }, []);

  const selectAll = useCallback((ids: number[]) => {
    setSelectedIds(ids);
  }, []);

  const clearSelection = useCallback(() => {
    setSelectedIds([]);
  }, []);

  const toggleSelectAll = useCallback((ids: number[]) => {
    setSelectedIds(prev => {
      const allSelected = ids.every(id => prev.includes(id));
      if (allSelected) return prev.filter(id => !ids.includes(id));
      const newSet = new Set([...prev, ...ids]);
      return Array.from(newSet);
    });
  }, []);

  return {
    selectedIds,
    isSelected,
    toggleRow,
    selectAll,
    clearSelection,
    toggleSelectAll,
    selectionCount: selectedIds.length,
  };
}
