/**
 * Pagination component — page-window style
 * Shows: first, prev, window of pages, next, last
 */
import { useMemo } from 'react';

interface PaginationProps {
  total:       number;
  page:        number;
  pageSize:    number;
  onChange:    (page: number) => void;
  pageSizes?:  number[];
  onPageSizeChange?: (size: number) => void;
}

export function Pagination({
  total, page, pageSize, onChange,
  pageSizes, onPageSizeChange,
}: PaginationProps) {
  const totalPages = Math.max(1, Math.ceil(total / pageSize));

  const pages = useMemo(() => {
    const WINDOW = 3;
    const start = Math.max(1, page - Math.floor(WINDOW / 2));
    const end   = Math.min(totalPages, start + WINDOW - 1);
    return Array.from({ length: end - start + 1 }, (_, i) => start + i);
  }, [page, totalPages]);

  const from = Math.min((page - 1) * pageSize + 1, total);
  const to   = Math.min(page * pageSize, total);

  return (
    <div className="pagination" role="navigation" aria-label="Pagination">
      <span className="pagination-info">
        {total === 0 ? 'No records' : `${from}\u2013${to} of ${total.toLocaleString('en-IN')}`}
      </span>

      {pageSizes && onPageSizeChange && (
        <select
          className="form-control form-control-sm"
          style={{ width: 'auto', marginRight: 'var(--sp-2)' }}
          value={pageSize}
          onChange={(e) => onPageSizeChange(Number(e.target.value))}
          aria-label="Rows per page"
        >
          {pageSizes.map((s) => (
            <option key={s} value={s}>{s} / page</option>
          ))}
        </select>
      )}

      <button className="page-btn" onClick={() => onChange(1)}       disabled={page <= 1} aria-label="First page">\u00AB</button>
      <button className="page-btn" onClick={() => onChange(page - 1)} disabled={page <= 1} aria-label="Previous page">\u2039</button>
      {pages[0] > 1 && <span style={{ fontSize: 'var(--fs-helper)', color: 'var(--c-text-disabled)' }}>...</span>}
      {pages.map((p) => (
        <button
          key={p}
          className={`page-btn${p === page ? ' active' : ''}`}
          onClick={() => onChange(p)}
          aria-current={p === page ? 'page' : undefined}
        >{p}</button>
      ))}
      {pages[pages.length - 1] < totalPages && <span style={{ fontSize: 'var(--fs-helper)', color: 'var(--c-text-disabled)' }}>...</span>}
      <button className="page-btn" onClick={() => onChange(page + 1)} disabled={page >= totalPages} aria-label="Next page">\u203A</button>
      <button className="page-btn" onClick={() => onChange(totalPages)} disabled={page >= totalPages} aria-label="Last page">\u00BB</button>
    </div>
  );
}
