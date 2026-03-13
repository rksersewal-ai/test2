import React from 'react';
import SettingsPanel from '../components/SettingsPanel';

export default function SettingsPage() {
  // Settings page renders the panel always-open (no slide-over; embedded)
  return (
    <div style={{ padding:'24px', maxWidth:'600px' }}>
      <h1 style={{ color:'#e2e8f0', fontSize:'22px', fontWeight:700, marginBottom:'24px' }}>⚙️ Application Settings</h1>
      <div style={{ background:'#151b2e', border:'1.5px solid #2d3555', borderRadius:'12px', overflow:'hidden' }}>
        {/* Re-use SettingsPanel body contents inline */}
        <InlineSettings />
      </div>
    </div>
  );
}

import { useSettings } from '../hooks/useSettings';

function InlineSettings() {
  const { settings, updateSetting } = useSettings();

  const Row = ({ label, children }: { label: string; children: React.ReactNode }) => (
    <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', padding:'12px 20px', borderBottom:'1px solid #2d3555', color:'#cbd5e0', fontSize:'14px' }}>
      <span>{label}</span>
      {children}
    </div>
  );

  const SectionTitle = ({ title }: { title: string }) => (
    <div style={{ padding:'10px 20px 6px', fontSize:'11px', fontWeight:700, textTransform:'uppercase', letterSpacing:'0.08em', color:'#4b6cb7', background:'#1a2238', borderBottom:'1px solid #2d3555' }}>{title}</div>
  );

  const selectStyle = { background:'#1e2332', border:'1px solid #2d3555', color:'#d1d5db', borderRadius:'5px', padding:'4px 8px', fontSize:'13px', cursor:'pointer' as const };

  return (
    <div>
      <SectionTitle title="Appearance" />
      <Row label="Dark Mode"><input type="checkbox" checked={settings.darkMode} onChange={e => updateSetting('darkMode', e.target.checked)} style={{ accentColor:'#4b6cb7', width:'16px', height:'16px', cursor:'pointer' }} /></Row>
      <Row label="Compact Sidebar"><input type="checkbox" checked={settings.compactSidebar} onChange={e => updateSetting('compactSidebar', e.target.checked)} style={{ accentColor:'#4b6cb7', width:'16px', height:'16px', cursor:'pointer' }} /></Row>
      <Row label="Font Size"><select style={selectStyle} value={settings.fontSize} onChange={e => updateSetting('fontSize', e.target.value)}><option value="small">Small</option><option value="medium">Medium</option><option value="large">Large</option></select></Row>

      <SectionTitle title="Notifications" />
      <Row label="OCR Completion Alerts"><input type="checkbox" checked={settings.notifyOCR} onChange={e => updateSetting('notifyOCR', e.target.checked)} style={{ accentColor:'#4b6cb7', width:'16px', height:'16px', cursor:'pointer' }} /></Row>
      <Row label="Document Upload Alerts"><input type="checkbox" checked={settings.notifyUpload} onChange={e => updateSetting('notifyUpload', e.target.checked)} style={{ accentColor:'#4b6cb7', width:'16px', height:'16px', cursor:'pointer' }} /></Row>
      <Row label="Audit Log Alerts"><input type="checkbox" checked={settings.notifyAudit} onChange={e => updateSetting('notifyAudit', e.target.checked)} style={{ accentColor:'#4b6cb7', width:'16px', height:'16px', cursor:'pointer' }} /></Row>

      <SectionTitle title="OCR Pipeline" />
      <Row label="Auto-process on Upload"><input type="checkbox" checked={settings.ocrAutoProcess} onChange={e => updateSetting('ocrAutoProcess', e.target.checked)} style={{ accentColor:'#4b6cb7', width:'16px', height:'16px', cursor:'pointer' }} /></Row>
      <Row label="OCR Language"><select style={selectStyle} value={settings.ocrLanguage} onChange={e => updateSetting('ocrLanguage', e.target.value)}><option value="eng">English</option><option value="hin">Hindi</option><option value="eng+hin">Eng + Hindi</option></select></Row>
      <Row label="Confidence Threshold (%)"><input type="number" min={50} max={100} value={settings.ocrConfidenceThreshold} onChange={e => updateSetting('ocrConfidenceThreshold', Number(e.target.value))} style={{ ...selectStyle, width:'70px', textAlign:'center' }} /></Row>

      <SectionTitle title="Data & Export" />
      <Row label="Default Export Format"><select style={selectStyle} value={settings.defaultExportFormat} onChange={e => updateSetting('defaultExportFormat', e.target.value)}><option value="pdf">PDF</option><option value="xlsx">Excel (XLSX)</option><option value="csv">CSV</option><option value="json">JSON</option></select></Row>
      <Row label="Items Per Page"><select style={selectStyle} value={settings.itemsPerPage} onChange={e => updateSetting('itemsPerPage', Number(e.target.value))}><option value={20}>20</option><option value={50}>50</option><option value={100}>100</option></select></Row>

      <div style={{ padding:'16px 20px', display:'flex', gap:'10px' }}>
        <button onClick={() => updateSetting('__reset__', true)} style={{ flex:1, padding:'9px', background:'none', border:'1px solid #2d3555', color:'#9ca3af', borderRadius:'7px', fontSize:'13px', cursor:'pointer' }}>Reset to Defaults</button>
        <button style={{ flex:1, padding:'9px', background:'linear-gradient(135deg,#4b6cb7,#182848)', border:'none', color:'#fff', borderRadius:'7px', fontSize:'13px', fontWeight:600, cursor:'pointer' }}>Save Settings</button>
      </div>
    </div>
  );
}
