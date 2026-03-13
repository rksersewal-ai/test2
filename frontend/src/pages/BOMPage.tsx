import React, { useState } from 'react';
import { useContextMenu } from '../hooks/useContextMenu';
import ContextMenu from '../components/ContextMenu';
import { usePageData } from '../hooks/usePageData';
import { useDebounce } from '../hooks/useDebounce';

interface BOMItem {
  id: string;
  partNo: string;
  description: string;
  qty: number;
  unit: string;
  locoType: string;
  drawingNo: string;
  status: 'Active' | 'Obsolete' | 'Provisional';
}

const MOCK_BOM: BOMItem[] = [
  { id:'1', partNo:'CLW/WAG9/TM/001', description:'Traction Motor TM615', qty:6, unit:'Nos', locoType:'WAG-9', drawingNo:'CLW/WAG9/TM/0234/A', status:'Active' },
  { id:'2', partNo:'CLW/WAG9/PAN/001', description:'Pantograph Assembly AM-12', qty:2, unit:'Nos', locoType:'WAG-9', drawingNo:'EL-PAN-001', status:'Active' },
  { id:'3', partNo:'CLW/WAP7/MT/001', description:'Main Transformer 5400kW', qty:1, unit:'Nos', locoType:'WAP-7', drawingNo:'EL-MT-001', status:'Active' },
  { id:'4', partNo:'BG-WS-001', description:'Wheelset Assembly BG', qty:6, unit:'Sets', locoType:'WAG-9', drawingNo:'BG-WS-001', status:'Active' },
  { id:'5', partNo:'BR-AIR-006', description:'Distributor Valve C3W', qty:8, unit:'Nos', locoType:'All', drawingNo:'BR-AIR-006', status:'Provisional' },
];

export default function BOMPage() {
  const [search, setSearch] = useState('');
  const dSearch = useDebounce(search, 300);
  const { menu, openMenu, closeMenu } = useContextMenu();

  const { data, loading } = usePageData<BOMItem[]>({
    fetchFn: async () => MOCK_BOM,
    deps: [],
  });

  const items = (data ?? []).filter(item =>
    item.partNo.toLowerCase().includes(dSearch.toLowerCase()) ||
    item.description.toLowerCase().includes(dSearch.toLowerCase()) ||
    item.locoType.toLowerCase().includes(dSearch.toLowerCase())
  );

  const getRowActions = (item: BOMItem) => [
    { label: '📋 View BOM Details', onClick: () => console.log('View', item.id) },
    { label: '✏️ Edit Item', onClick: () => console.log('Edit', item.id) },
    { label: '📄 Open Drawing', onClick: () => console.log('Drawing', item.drawingNo) },
    { divider: true } as const,
    { label: '📤 Export Row', onClick: () => console.log('Export', item.id) },
    { label: '🗑️ Delete', onClick: () => console.log('Delete', item.id), danger: true },
  ];

  return (
    <div style={{ padding: '24px' }}>
      <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:'20px' }}>
        <h1 style={{ color:'#e2e8f0', fontSize:'22px', fontWeight:700, margin:0 }}>📦 Bill of Materials</h1>
        <div style={{ display:'flex', gap:'10px' }}>
          <input
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Search part no, description, loco type…"
            style={{ padding:'8px 14px', borderRadius:'7px', border:'1px solid #2d3555', background:'#1e2332', color:'#d1d5db', width:'280px', fontSize:'13px' }}
          />
          <button style={{ padding:'8px 16px', background:'linear-gradient(135deg,#4b6cb7,#182848)', border:'none', borderRadius:'7px', color:'#fff', fontWeight:600, cursor:'pointer' }}>
            + Add Part
          </button>
        </div>
      </div>

      {loading ? (
        <div style={{ color:'#6b7280', textAlign:'center', padding:'60px' }}>Loading BOM…</div>
      ) : (
        <table style={{ width:'100%', borderCollapse:'collapse', fontSize:'13.5px' }}>
          <thead>
            <tr style={{ background:'#1a2238', color:'#6b7280', textTransform:'uppercase', fontSize:'11px' }}>
              {['Part No', 'Description', 'Qty', 'Unit', 'Loco Type', 'Drawing No', 'Status', ''].map(h => (
                <th key={h} style={{ padding:'10px 14px', textAlign:'left', fontWeight:600, borderBottom:'1px solid #2d3555' }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {items.map(item => (
              <tr
                key={item.id}
                style={{ borderBottom:'1px solid #1e2332', color:'#d1d5db', cursor:'pointer' }}
                onContextMenu={e => openMenu(e, getRowActions(item), item.partNo)}
              >
                <td style={{ padding:'10px 14px', color:'#60a5fa', fontFamily:'monospace' }}>{item.partNo}</td>
                <td style={{ padding:'10px 14px' }}>{item.description}</td>
                <td style={{ padding:'10px 14px', textAlign:'center' }}>{item.qty}</td>
                <td style={{ padding:'10px 14px' }}>{item.unit}</td>
                <td style={{ padding:'10px 14px' }}>
                  <span style={{ background:'#1e3a5f', color:'#60a5fa', padding:'2px 8px', borderRadius:'12px', fontSize:'12px' }}>{item.locoType}</span>
                </td>
                <td style={{ padding:'10px 14px', fontFamily:'monospace', fontSize:'12px', color:'#a78bfa' }}>{item.drawingNo}</td>
                <td style={{ padding:'10px 14px' }}>
                  <span style={{ background: item.status==='Active'?'#052e16': item.status==='Obsolete'?'#3b0a0a':'#2d2000', color: item.status==='Active'?'#4ade80': item.status==='Obsolete'?'#f87171':'#fbbf24', padding:'2px 8px', borderRadius:'12px', fontSize:'12px' }}>
                    {item.status}
                  </span>
                </td>
                <td style={{ padding:'10px 14px' }}>
                  <button
                    onClick={e => openMenu(e, getRowActions(item), item.partNo)}
                    style={{ background:'none', border:'1px solid #2d3555', color:'#6b7280', borderRadius:'5px', padding:'3px 10px', cursor:'pointer', fontSize:'15px' }}
                  >⋯</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      <ContextMenu {...menu} onClose={closeMenu} />
    </div>
  );
}
