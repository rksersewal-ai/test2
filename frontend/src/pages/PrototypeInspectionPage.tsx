import React, { useState } from 'react';
import { useContextMenu } from '../hooks/useContextMenu';
import ContextMenu from '../components/ContextMenu';
import { usePageData } from '../hooks/usePageData';

interface InspectionRecord {
  id: string;
  locoClass: string;
  serialNo: string;
  inspectionType: string;
  inspector: string;
  date: string;
  result: 'Pass' | 'Fail' | 'Conditional' | 'Pending';
  remarks: string;
}

const MOCK_INSPECTIONS: InspectionRecord[] = [
  { id:'1', locoClass:'WAG-9', serialNo:'31001', inspectionType:'Prototype Inspection', inspector:'RDSO Inspector', date:'2024-02-10', result:'Pass', remarks:'All parameters within spec.' },
  { id:'2', locoClass:'WAG-12B', serialNo:'60001', inspectionType:'IGBT Module Test', inspector:'CLW QC', date:'2024-06-05', result:'Conditional', remarks:'Thermal margin borderline.' },
  { id:'3', locoClass:'WAP-7', serialNo:'30200', inspectionType:'FAT (Factory Acceptance)', inspector:'Third Party (BV)', date:'2024-04-22', result:'Pass', remarks:'Full FAT completed.' },
  { id:'4', locoClass:'DETC', serialNo:'DETC-045', inspectionType:'Platform Hydraulic Test', inspector:'DMW QA', date:'2024-09-01', result:'Pending', remarks:'Awaiting hydraulic pressure certification.' },
  { id:'5', locoClass:'WAG-9', serialNo:'31090', inspectionType:'Bogie Overhaul Inspection', inspector:'CLW QC', date:'2025-01-15', result:'Fail', remarks:'Primary spring wear beyond limits.' },
];

const STATUS_COLOR: Record<string, { bg: string; text: string }> = {
  Pass:        { bg:'#052e16', text:'#4ade80' },
  Fail:        { bg:'#3b0a0a', text:'#f87171' },
  Conditional: { bg:'#2d2000', text:'#fbbf24' },
  Pending:     { bg:'#1e1e2e', text:'#818cf8' },
};

export default function PrototypeInspectionPage() {
  const [filter, setFilter] = useState('');
  const { menu, openMenu, closeMenu } = useContextMenu();

  const { data, loading } = usePageData<InspectionRecord[]>({
    fetchFn: async () => MOCK_INSPECTIONS,
  });

  const items = (data ?? []).filter(r =>
    r.locoClass.toLowerCase().includes(filter.toLowerCase()) ||
    r.serialNo.includes(filter) ||
    r.inspectionType.toLowerCase().includes(filter.toLowerCase())
  );

  const getActions = (item: InspectionRecord) => [
    { label: '📋 View Full Report', onClick: () => console.log('view', item.id) },
    { label: '📎 Attach Documents', onClick: () => console.log('attach', item.id) },
    { label: '✏️ Edit Record', onClick: () => console.log('edit', item.id) },
    { divider: true } as const,
    { label: '📤 Export Report', onClick: () => console.log('export', item.id) },
    { label: '🗑️ Delete', onClick: () => console.log('delete', item.id), danger: true, disabled: item.result === 'Pass' },
  ];

  return (
    <div style={{ padding:'24px' }}>
      <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:'20px' }}>
        <h1 style={{ color:'#e2e8f0', fontSize:'22px', fontWeight:700, margin:0 }}>🔬 Prototype Inspection</h1>
        <div style={{ display:'flex', gap:'10px' }}>
          <input
            value={filter}
            onChange={e => setFilter(e.target.value)}
            placeholder="Search loco, serial, inspection type…"
            style={{ padding:'8px 14px', borderRadius:'7px', border:'1px solid #2d3555', background:'#1e2332', color:'#d1d5db', width:'280px', fontSize:'13px' }}
          />
          <button style={{ padding:'8px 16px', background:'linear-gradient(135deg,#4b6cb7,#182848)', border:'none', borderRadius:'7px', color:'#fff', fontWeight:600, cursor:'pointer' }}>
            + New Inspection
          </button>
        </div>
      </div>

      {loading ? (
        <div style={{ color:'#6b7280', textAlign:'center', padding:'60px' }}>Loading inspections…</div>
      ) : (
        <table style={{ width:'100%', borderCollapse:'collapse', fontSize:'13.5px' }}>
          <thead>
            <tr style={{ background:'#1a2238', color:'#6b7280', textTransform:'uppercase', fontSize:'11px' }}>
              {['Loco Class', 'Serial No', 'Inspection Type', 'Inspector', 'Date', 'Result', 'Remarks', ''].map(h => (
                <th key={h} style={{ padding:'10px 14px', textAlign:'left', fontWeight:600, borderBottom:'1px solid #2d3555' }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {items.map(item => (
              <tr
                key={item.id}
                onContextMenu={e => openMenu(e, getActions(item), `${item.locoClass} #${item.serialNo}`)}
                style={{ borderBottom:'1px solid #1e2332', color:'#d1d5db', cursor:'pointer' }}
              >
                <td style={{ padding:'10px 14px' }}><span style={{ background:'#1e3a5f', color:'#60a5fa', padding:'2px 8px', borderRadius:'12px', fontSize:'12px' }}>{item.locoClass}</span></td>
                <td style={{ padding:'10px 14px', fontFamily:'monospace' }}>{item.serialNo}</td>
                <td style={{ padding:'10px 14px' }}>{item.inspectionType}</td>
                <td style={{ padding:'10px 14px' }}>{item.inspector}</td>
                <td style={{ padding:'10px 14px' }}>{item.date}</td>
                <td style={{ padding:'10px 14px' }}>
                  <span style={{ background: STATUS_COLOR[item.result].bg, color: STATUS_COLOR[item.result].text, padding:'2px 8px', borderRadius:'12px', fontSize:'12px' }}>
                    {item.result}
                  </span>
                </td>
                <td style={{ padding:'10px 14px', color:'#9ca3af', fontSize:'12px', maxWidth:'200px', overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{item.remarks}</td>
                <td style={{ padding:'10px 14px' }}>
                  <button onClick={e => openMenu(e, getActions(item), item.inspectionType)} style={{ background:'none', border:'1px solid #2d3555', color:'#6b7280', borderRadius:'5px', padding:'3px 10px', cursor:'pointer', fontSize:'15px' }}>⋯</button>
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
