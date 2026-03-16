import React, { memo, useState, useRef, useEffect } from 'react';
import { Handle, Position } from '@xyflow/react';

const TYPE_ICON: Record<string, string> = {
  ASSEMBLY:    '🏗️',
  SUBASSEMBLY: '⚙️',
  COMPONENT:   '🔧',
  PART:        '🔩',
};

const TYPE_LABEL: Record<string, string> = {
  ASSEMBLY:    'Assembly',
  SUBASSEMBLY: 'Sub-Assembly',
  COMPONENT:   'Component',
  PART:        'Part',
};

export interface BOMNodeData {
  id: number;
  pl_number: string;
  description: string;
  node_type: string;
  inspection_category: string;
  safety_item: boolean;
  quantity: string;
  unit: string;
  level: number;
  children_count: number;
  cat_color: string;
  remarks: string;
  isAdmin?: boolean;
  onOpenPL?: (pl: string) => void;
  onAddChild?: (id: number) => void;
  onEdit?: (id: number) => void;
  onDelete?: (id: number) => void;
  onMove?: (id: number) => void;
}

const BOMNodeCard = memo(({ data, selected }: { data: BOMNodeData; selected?: boolean }) => {
  const [menuOpen, setMenuOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) setMenuOpen(false);
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  const cc = data.cat_color || '#6b7280';
  const border = selected ? '2px solid #60a5fa' : `2px solid ${cc}`;

  return (
    <div style={{
      background: '#1a2035',
      border,
      borderRadius: 10,
      minWidth: 220,
      maxWidth: 260,
      boxShadow: selected ? `0 0 0 3px #60a5fa44` : `0 4px 16px #0006`,
      fontFamily: 'Inter, sans-serif',
      position: 'relative',
      overflow: 'visible',
    }}>
      {/* top color bar */}
      <div style={{ height: 4, background: cc, borderRadius: '8px 8px 0 0' }} />

      <Handle type="target" position={Position.Top}
        style={{ background: cc, width: 10, height: 10, border: '2px solid #1a2035' }} />
      <Handle type="source" position={Position.Bottom}
        style={{ background: cc, width: 10, height: 10, border: '2px solid #1a2035' }} />

      <div style={{ padding: '8px 10px 6px' }}>
        {/* Header row */}
        <div style={{ display: 'flex', alignItems: 'flex-start', gap: 6 }}>
          <span style={{ fontSize: 16, lineHeight: 1.3 }}>{TYPE_ICON[data.node_type] || '📦'}</span>
          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{
              fontFamily: 'monospace', fontSize: 12, fontWeight: 700,
              color: '#60a5fa', letterSpacing: 0.3, whiteSpace: 'nowrap',
              overflow: 'hidden', textOverflow: 'ellipsis',
            }}>{data.pl_number}</div>
            <div style={{
              fontSize: 11, color: '#d1d5db', marginTop: 1,
              overflow: 'hidden', textOverflow: 'ellipsis',
              display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical' as const,
            }}>{data.description || <span style={{ color: '#6b7280', fontStyle: 'italic' }}>No description</span>}</div>
          </div>
          {/* 3-dot menu */}
          {data.isAdmin && (
            <div ref={menuRef} style={{ position: 'relative', flexShrink: 0 }}>
              <button onClick={() => setMenuOpen(v => !v)} style={{
                background: 'none', border: 'none', color: '#9ca3af', cursor: 'pointer',
                fontSize: 16, lineHeight: 1, padding: '0 2px', borderRadius: 4,
              }}>⋮</button>
              {menuOpen && (
                <div style={{
                  position: 'absolute', top: 22, right: 0, background: '#1e2a3e',
                  border: '1px solid #2d3555', borderRadius: 6, zIndex: 9999,
                  minWidth: 150, boxShadow: '0 8px 24px #0008',
                }}>
                  {[['✏️ Edit node', () => data.onEdit?.(data.id)],
                    ['➕ Add child', () => data.onAddChild?.(data.id)],
                    ['↕️ Move / reparent', () => data.onMove?.(data.id)],
                    ['🗑️ Remove node', () => data.onDelete?.(data.id)],
                  ].map(([label, fn]) => (
                    <button key={label as string} onClick={() => { (fn as () => void)(); setMenuOpen(false); }} style={{
                      display: 'block', width: '100%', textAlign: 'left',
                      background: 'none', border: 'none', color: '#e2e8f0',
                      fontSize: 12, padding: '7px 12px', cursor: 'pointer',
                    }}
                    onMouseEnter={e => (e.currentTarget.style.background = '#2d3555')}
                    onMouseLeave={e => (e.currentTarget.style.background = 'none')}>
                      {label as string}
                    </button>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Meta row */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 4, marginTop: 6, flexWrap: 'wrap' }}>
          {data.inspection_category && (
            <span style={{
              background: cc + '33', color: cc, border: `1px solid ${cc}`,
              borderRadius: 4, fontSize: 10, fontWeight: 700, padding: '1px 5px',
            }}>CAT {data.inspection_category}</span>
          )}
          {data.safety_item && (
            <span style={{
              background: '#ef444433', color: '#ef4444', border: '1px solid #ef4444',
              borderRadius: 4, fontSize: 10, fontWeight: 700, padding: '1px 5px',
            }}>SAFETY</span>
          )}
          <span style={{ marginLeft: 'auto', fontSize: 10, color: '#9ca3af' }}>
            {data.quantity} {data.unit}
          </span>
        </div>

        {/* Type label */}
        <div style={{ fontSize: 10, color: '#6b7280', marginTop: 3 }}>
          {TYPE_LABEL[data.node_type] || data.node_type}
          {data.children_count > 0 && (
            <span style={{ marginLeft: 6, color: '#60a5fa' }}>▼ {data.children_count} children</span>
          )}
        </div>

        {/* Action buttons */}
        <div style={{ display: 'flex', gap: 4, marginTop: 7, flexWrap: 'wrap' }}>
          <button onClick={() => data.onOpenPL?.(data.pl_number)} style={{
            flex: 1, fontSize: 10, padding: '4px 0', borderRadius: 4, cursor: 'pointer',
            background: 'linear-gradient(135deg,#4b6cb7,#182848)', color: '#fff', border: 'none',
          }}>PL</button>
          
          <button onClick={() => data.onWhereUsed?.(data.pl_number)} style={{
            flex: 1, fontSize: 10, padding: '4px 0', borderRadius: 4, cursor: 'pointer',
            background: 'linear-gradient(135deg,#6366f1,#4338ca)', color: '#fff', border: 'none',
          }} title="Where Used Impact Analysis">
            Where Used
          </button>

          {data.isAdmin && (
            <>
              <button onClick={() => data.onAddChild?.(data.id)} style={{
                flex: 1, fontSize: 10, padding: '4px 0', borderRadius: 4, cursor: 'pointer',
                background: 'linear-gradient(135deg,#14532d,#052e16)', color: '#86efac', border: 'none',
              }}>+ Child</button>
              <button onClick={() => data.onDelete?.(data.id)} style={{
                fontSize: 10, padding: '4px 7px', borderRadius: 4, cursor: 'pointer',
                background: '#3f1010', color: '#fca5a5', border: '1px solid #7f1d1d',
              }}>✕</button>
            </>
          )}
        </div>
      </div>
    </div>
  );
});

BOMNodeCard.displayName = 'BOMNodeCard';
export default BOMNodeCard;
