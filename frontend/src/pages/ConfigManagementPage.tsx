import React, { useState } from 'react';
import { useContextMenu } from '../hooks/useContextMenu';
import ContextMenu from '../components/ContextMenu';
import { usePageData } from '../hooks/usePageData';

interface ConfigItem {
  id: string;
  locoClass: string;
  serialNo: string;
  configVersion: string;
  changeRef: string;
  effectiveDate: string;
  changedBy: string;
  status: 'Approved' | 'Pending' | 'Superseded';
}

const MOCK_CONFIG: ConfigItem[] = [
  { id:'1', locoClass:'WAG-9', serialNo:'31001', configVersion:'v3.2', changeRef:'CLW/ECN/2024/0089', effectiveDate:'2024-03-15', changedBy:'CLW Engineering', status:'Approved' },
  { id:'2', locoClass:'WAP-7', serialNo:'30201', configVersion:'v2.8', changeRef:'CLW/ECN/2024/0056', effectiveDate:'2024-01-20', changedBy:'RDSO', status:'Approved' },
  { id:'3', locoClass:'WAG-12B', serialNo:'60001', configVersion:'v1.5', changeRef:'CLW/ECN/2025/0012', effectiveDate:'2025-02-01', changedBy:'CLW Engineering', status:'Pending' },
  { id:'4', locoClass:'WAG-9', serialNo:'31045', configVersion:'v3.0', changeRef:'CLW/ECN/2023/0211', effectiveDate:'2023-08-10', changedBy:'CLW Engineering', status:'Superseded' },
];

export default function ConfigManagementPage() {
  const [filter, setFilter] = useState('');
  const { menu, openMenu, closeMenu } = useContextMenu();

  const { data, loading } = usePageData<ConfigItem[]>({
    fetchFn: async () => MOCK_CONFIG,
  });

  const items = (data ?? []).filter(c =>
    c.locoClass.toLowerCase().includes(filter.toLowerCase()) ||
    c.serialNo.includes(filter) ||
    c.changeRef.toLowerCase().includes(filter.toLowerCase())
  );

  const getActions = (item: ConfigItem) => [
    { label: '📋 View Config Details', onClick: () => console.log('view', item.id) },
    { label: '🔄 Compare Versions', onClick: () => console.log('compare', item.id) },
    { label: '📄 Open ECN Document', onClick: () => console.log('ecn', item.changeRef) },
    { divider: true } as const,
    { label: '✏️ Edit Record', onClick: () => console.log('edit', item.id), disabled: item.status === 'Approved' },
    { label: '🗑️ Delete', onClick: () => console.log('delete', item.id), danger: true },
  ];

  return (
    <div style={{ padding:'24px' }}>
      <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:'20px' }}>
        <h1 style={{ color:'#e2e8f0', fontSize:'22px', fontWeight:700, margin:0 }}>🔧 Configuration Management</h1>
        <div style={{ display:'flex', gap:'10px' }}>
          <input
            value={filter}
            onChange={e => setFilter(e.target.value)}
            placeholder="Search loco class, serial, ECN…"
            style={{ padding:'8px 14px', borderRadius:'7px', border:'1px solid #2d3555', background:'#1e2332', color:'#d1d5db', width:'260px', fontSize:'13px' }}
          />
          <button style={{ padding:'8px 16px', background:'linear-gradient(135deg,#4b6cb7,#182848)', border:'none', borderRadius:'7px', color:'#fff', fontWeight:600, cursor:'pointer' }}>
            + New Config
          </button>
        </div>
      </div>

      {loading ? (
        <div style={{ color:'#6b7280', textAlign:'center', padding:'60px' }}>Loading configurations…</div>
      ) : (
        <table style={{ width:'100%', borderCollapse:'collapse', fontSize:'13.5px' }}>
          <thead>
            <tr style={{ background:'#1a2238', color:'#6b7280', textTransform:'uppercase', fontSize:'11px' }}>
              {['Loco Class', 'Serial No', 'Config Version', 'Change Ref (ECN)', 'Effective Date', 'Changed By', 'Status', ''].map(h => (
                <th key={h} style={{ padding:'10px 14px', textAlign:'left', fontWeight:600, borderBottom:'1px solid #2d3555' }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {items.map(item => (
              <tr
                key={item.id}
                onContextMenu={e => openMenu(e, getActions(item), `Config: ${item.locoClass} ${item.serialNo}`)}
                style={{ borderBottom:'1px solid #1e2332', color:'#d1d5db', cursor:'pointer' }}
              >
                <td style={{ padding:'10px 14px' }}><span style={{ background:'#1e3a5f', color:'#60a5fa', padding:'2px 8px', borderRadius:'12px', fontSize:'12px' }}>{item.locoClass}</span></td>
                <td style={{ padding:'10px 14px', fontFamily:'monospace' }}>{item.serialNo}</td>
                <td style={{ padding:'10px 14px', color:'#a78bfa', fontFamily:'monospace' }}>{item.configVersion}</td>
                <td style={{ padding:'10px 14px', fontFamily:'monospace', fontSize:'12px', color:'#fbbf24' }}>{item.changeRef}</td>
                <td style={{ padding:'10px 14px' }}>{item.effectiveDate}</td>
                <td style={{ padding:'10px 14px' }}>{item.changedBy}</td>
                <td style={{ padding:'10px 14px' }}>
                  <span style={{ background: item.status==='Approved'?'#052e16': item.status==='Pending'?'#2d2000':'#1e1e2e', color: item.status==='Approved'?'#4ade80': item.status==='Pending'?'#fbbf24':'#6b7280', padding:'2px 8px', borderRadius:'12px', fontSize:'12px' }}>
                    {item.status}
                  </span>
                </td>
                <td style={{ padding:'10px 14px' }}>
                  <button onClick={e => openMenu(e, getActions(item), item.changeRef)} style={{ background:'none', border:'1px solid #2d3555', color:'#6b7280', borderRadius:'5px', padding:'3px 10px', cursor:'pointer', fontSize:'15px' }}>⋯</button>
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
