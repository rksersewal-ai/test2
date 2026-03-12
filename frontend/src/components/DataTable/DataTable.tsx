/**
 * DataTable — Enterprise-grade data table
 * Features: sticky headers, sortable columns, row selection,
 *           loading state, empty state, dense mode, pagination
 */
import { useState, useCallback, ReactNode } from 'react';
import type { CSSProperties } from 'react';

export type SortDirection = 'asc' | 'desc' | null;

export interface ColumnDef<T> {
  key:         string;
  header:      ReactNode;
  render?:     (row: T, idx: number) => ReactNode;
  sortable?:   boolean;
  width?:      number | string;
  minWidth?:   number | string;
  className?:  string;
  headerClassName?: string;
  align?:      'left' | 'center' | 'right';
}

export interface DataTableProps<T> {
  columns:         ColumnDef<T>[];
  data:            T[];
  rowKey:          (row: T) => string | number;
  isLoading?:      boolean;
  emptyText?:      string;
  dense?:          boolean;
  selectable?:     boolean;
  selectedKeys?:   Set<string | number>;
  onSelectRow?:    (key: string | number) => void;
  onSelectAll?:    (keys: (string | number)[]) => void;
  sortKey?:        string;
  sortDir?:        SortDirection;
  onSort?:         (key: string) => void;
  className?:      string;
  maxHeight?:      string;
  stickyHeader?:   boolean;
}

export function DataTable<T>({
  columns, data, rowKey, isLoading = false, emptyText = 'No records found.',
  dense = false, selectable = false,
  selectedKeys = new Set(), onSelectRow, onSelectAll,
  sortKey, sortDir, onSort,
  className = '', maxHeight,
}: DataTableProps<T>) {

  const allSelected = data.length > 0 && data.every((r) => selectedKeys.has(rowKey(r)));
  const someSelected = !allSelected && data.some((r) => selectedKeys.has(rowKey(r)));

  const handleSelectAll = useCallback(() => {
    if (onSelectAll) onSelectAll(allSelected ? [] : data.map(rowKey));
  }, [allSelected, data, onSelectAll, rowKey]);

  const getThStyle = (col: ColumnDef<T>): CSSProperties => ({
    width: col.width,
    minWidth: col.minWidth,
    textAlign: col.align ?? 'left',
  });
  const getTdStyle = (col: ColumnDef<T>): CSSProperties => ({
    width: col.width,
    minWidth: col.minWidth,
    maxWidth: col.width ?? 280,
    textAlign: col.align ?? 'left',
  });

  return (
    <div className="data-table-wrapper" style={maxHeight ? { maxHeight, overflow: 'auto' } : undefined}>
      <div className="table-loading" style={{ display: isLoading ? 'flex' : 'none' }}>
        <div className="spinner spinner-md" />
      </div>
      <table className={`data-table${dense ? ' dense' : ''} ${className}`}>
        <thead>
          <tr>
            {selectable && (
              <th className="col-check">
                <input
                  type="checkbox"
                  className="form-check-input"
                  checked={allSelected}
                  ref={(el) => { if (el) el.indeterminate = someSelected; }}
                  onChange={handleSelectAll}
                  aria-label="Select all rows"
                />
              </th>
            )}
            {columns.map((col) => (
              <th
                key={col.key}
                className={[
                  col.sortable ? 'sortable' : '',
                  sortKey === col.key && sortDir === 'asc'  ? 'sort-asc'  : '',
                  sortKey === col.key && sortDir === 'desc' ? 'sort-desc' : '',
                  col.headerClassName ?? '',
                ].join(' ').trim()}
                style={getThStyle(col)}
                onClick={col.sortable && onSort ? () => onSort(col.key) : undefined}
                aria-sort={sortKey === col.key ? (sortDir === 'asc' ? 'ascending' : 'descending') : undefined}
              >
                {col.sortable ? (
                  <span>{col.header}<span className="sort-icon" /></span>
                ) : col.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {!isLoading && data.length === 0 && (
            <tr>
              <td colSpan={columns.length + (selectable ? 1 : 0)}>
                <div className="table-empty">
                  <div className="table-empty-icon">\uD83D\uDCED</div>
                  <p>{emptyText}</p>
                </div>
              </td>
            </tr>
          )}
          {data.map((row, idx) => {
            const key = rowKey(row);
            const isSelected = selectedKeys.has(key);
            return (
              <tr
                key={key}
                className={isSelected ? 'selected' : ''}
                onClick={selectable && onSelectRow ? () => onSelectRow(key) : undefined}
                style={selectable ? { cursor: 'pointer' } : undefined}
              >
                {selectable && (
                  <td className="col-check" onClick={(e) => e.stopPropagation()}>
                    <input
                      type="checkbox"
                      className="form-check-input"
                      checked={isSelected}
                      onChange={() => onSelectRow?.(key)}
                      aria-label={`Select row ${idx + 1}`}
                    />
                  </td>
                )}
                {columns.map((col) => (
                  <td key={col.key} className={col.className ?? ''} style={getTdStyle(col)}>
                    {col.render ? col.render(row, idx) : String((row as Record<string, unknown>)[col.key] ?? '')}
                  </td>
                ))}
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
