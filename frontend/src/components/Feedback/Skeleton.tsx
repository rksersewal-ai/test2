interface SkeletonProps { type?: 'text' | 'title' | 'row'; width?: string; className?: string; }
export function Skeleton({ type = 'text', width, className = '' }: SkeletonProps) {
  return <div className={`skeleton skeleton-${type} ${className}`} style={width ? { width } : undefined} aria-hidden />;
}

export function SkeletonTable({ rows = 8, cols = 6 }: { rows?: number; cols?: number }) {
  return (
    <div className="data-table-wrapper">
      <table className="data-table">
        <thead>
          <tr>
            {Array.from({ length: cols }).map((_, i) => (
              <th key={i}><Skeleton type="text" /></th>
            ))}
          </tr>
        </thead>
        <tbody>
          {Array.from({ length: rows }).map((_, r) => (
            <tr key={r}>
              {Array.from({ length: cols }).map((_, c) => (
                <td key={c}><Skeleton type="text" width={c === 0 ? '80px' : c === 1 ? '60%' : '50%'} /></td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
