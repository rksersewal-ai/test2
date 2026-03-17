import React, { useState } from 'react';
import { useSettings, type AppSettings } from '../hooks/useSettings';

type ToastState = { type: 'success' | 'error'; text: string } | null;

interface RowProps {
  label: string;
  children: React.ReactNode;
}

interface SectionTitleProps {
  title: string;
}

const rowStyle: React.CSSProperties = {
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  padding: '12px 20px',
  borderBottom: '1px solid #2d3555',
  color: '#cbd5e0',
  fontSize: '14px',
};

const sectionTitleStyle: React.CSSProperties = {
  padding: '10px 20px 6px',
  fontSize: '11px',
  fontWeight: 700,
  textTransform: 'uppercase',
  letterSpacing: '0.08em',
  color: '#4b6cb7',
  background: '#1a2238',
  borderBottom: '1px solid #2d3555',
};

function Row({ label, children }: RowProps) {
  return (
    <div style={rowStyle}>
      <span>{label}</span>
      {children}
    </div>
  );
}

function SectionTitle({ title }: SectionTitleProps) {
  return <div style={sectionTitleStyle}>{title}</div>;
}

export default function SettingsPage() {
  return (
    <div style={{ padding: '24px', maxWidth: '600px' }}>
      <h1 style={{ color: '#e2e8f0', fontSize: '22px', fontWeight: 700, marginBottom: '24px' }}>
        Application Settings
      </h1>
      <div style={{ background: '#151b2e', border: '1.5px solid #2d3555', borderRadius: '12px', overflow: 'hidden' }}>
        <InlineSettings />
      </div>
    </div>
  );
}

function InlineSettings() {
  const { settings, updateSetting, persist } = useSettings();
  const [toast, setToast] = useState<ToastState>(null);
  const [confirmReset, setConfirmReset] = useState(false);

  const showToast = (type: 'success' | 'error', text: string) => {
    setToast({ type, text });
    setTimeout(() => setToast(null), 3000);
  };

  const handleSave = () => {
    persist();
    showToast('success', 'Settings saved successfully.');
  };

  const handleReset = () => {
    updateSetting('__reset__', true);
    setConfirmReset(false);
    showToast('success', 'Settings reset to defaults.');
  };

  const selectStyle: React.CSSProperties = {
    background: '#1e2332',
    border: '1px solid #2d3555',
    color: '#d1d5db',
    borderRadius: '5px',
    padding: '4px 8px',
    fontSize: '13px',
    cursor: 'pointer',
  };

  const checkboxStyle: React.CSSProperties = {
    accentColor: '#4b6cb7',
    width: '16px',
    height: '16px',
    cursor: 'pointer',
  };

  return (
    <div>
      {toast && (
        <div
          style={{
            position: 'fixed',
            top: 20,
            right: 20,
            zIndex: 9999,
            background: toast.type === 'success' ? '#166534' : '#7f1d1d',
            color: '#fff',
            padding: '10px 18px',
            borderRadius: 8,
            fontSize: 13,
            fontWeight: 500,
            boxShadow: '0 4px 12px rgba(0,0,0,0.4)',
          }}
        >
          {toast.text}
        </div>
      )}

      {confirmReset && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            background: 'rgba(0,0,0,0.6)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 9998,
          }}
        >
          <div
            style={{
              background: '#1e2332',
              border: '1px solid #2d3555',
              borderRadius: 10,
              padding: 24,
              maxWidth: 340,
              textAlign: 'center',
            }}
          >
            <div style={{ color: '#f8fafc', fontSize: 16, fontWeight: 600, marginBottom: 12 }}>
              Reset to Defaults?
            </div>
            <p style={{ color: '#94a3b8', fontSize: 13, marginBottom: 20 }}>
              All your settings will be reset. This cannot be undone.
            </p>
            <div style={{ display: 'flex', gap: 10, justifyContent: 'center' }}>
              <button
                onClick={() => setConfirmReset(false)}
                style={{
                  padding: '8px 20px',
                  background: 'none',
                  border: '1px solid #2d3555',
                  color: '#9ca3af',
                  borderRadius: 7,
                  fontSize: 13,
                  cursor: 'pointer',
                }}
              >
                Cancel
              </button>
              <button
                onClick={handleReset}
                style={{
                  padding: '8px 20px',
                  background: '#dc2626',
                  border: 'none',
                  color: '#fff',
                  borderRadius: 7,
                  fontSize: 13,
                  fontWeight: 600,
                  cursor: 'pointer',
                }}
              >
                Reset
              </button>
            </div>
          </div>
        </div>
      )}

      <SectionTitle title="Appearance" />
      <Row label="Dark Mode">
        <input
          type="checkbox"
          checked={settings.darkMode}
          onChange={event => updateSetting('darkMode', event.target.checked)}
          style={checkboxStyle}
        />
      </Row>
      <Row label="Compact Sidebar">
        <input
          type="checkbox"
          checked={settings.compactSidebar}
          onChange={event => updateSetting('compactSidebar', event.target.checked)}
          style={checkboxStyle}
        />
      </Row>
      <Row label="Font Size">
        <select
          style={selectStyle}
          value={settings.fontSize}
          onChange={event => updateSetting('fontSize', event.target.value as 'small' | 'medium' | 'large')}
        >
          <option value="small">Small</option>
          <option value="medium">Medium</option>
          <option value="large">Large</option>
        </select>
      </Row>

      <SectionTitle title="Notifications" />
      <Row label="OCR Completion Alerts">
        <input
          type="checkbox"
          checked={settings.notifyOCR}
          onChange={event => updateSetting('notifyOCR', event.target.checked)}
          style={checkboxStyle}
        />
      </Row>
      <Row label="Document Upload Alerts">
        <input
          type="checkbox"
          checked={settings.notifyUpload}
          onChange={event => updateSetting('notifyUpload', event.target.checked)}
          style={checkboxStyle}
        />
      </Row>
      <Row label="Audit Log Alerts">
        <input
          type="checkbox"
          checked={settings.notifyAudit}
          onChange={event => updateSetting('notifyAudit', event.target.checked)}
          style={checkboxStyle}
        />
      </Row>

      <SectionTitle title="OCR Pipeline" />
      <Row label="Auto-process on Upload">
        <input
          type="checkbox"
          checked={settings.ocrAutoProcess}
          onChange={event => updateSetting('ocrAutoProcess', event.target.checked)}
          style={checkboxStyle}
        />
      </Row>
      <Row label="OCR Language">
        <select
          style={selectStyle}
          value={settings.ocrLanguage}
          onChange={event => updateSetting('ocrLanguage', event.target.value)}
        >
          <option value="eng">English</option>
          <option value="hin">Hindi</option>
          <option value="eng+hin">Eng + Hindi</option>
        </select>
      </Row>
      <Row label="Confidence Threshold (%)">
        <input
          type="number"
          min={50}
          max={100}
          value={settings.ocrConfidenceThreshold}
          onChange={event => updateSetting('ocrConfidenceThreshold', Number(event.target.value))}
          style={{ ...selectStyle, width: '70px', textAlign: 'center' }}
        />
      </Row>

      <SectionTitle title="Data & Export" />
      <Row label="Default Export Format">
        <select
          style={selectStyle}
          value={settings.defaultExportFormat}
          onChange={event => updateSetting('defaultExportFormat', event.target.value as AppSettings['defaultExportFormat'])}
        >
          <option value="pdf">PDF</option>
          <option value="xlsx">Excel (XLSX)</option>
          <option value="csv">CSV</option>
          <option value="json">JSON</option>
        </select>
      </Row>
      <Row label="Items Per Page">
        <select
          style={selectStyle}
          value={settings.itemsPerPage}
          onChange={event => updateSetting('itemsPerPage', Number(event.target.value))}
        >
          <option value={20}>20</option>
          <option value={50}>50</option>
          <option value={100}>100</option>
        </select>
      </Row>

      <div style={{ padding: '16px 20px', display: 'flex', gap: '10px' }}>
        <button
          onClick={() => setConfirmReset(true)}
          style={{
            flex: 1,
            padding: '9px',
            background: 'none',
            border: '1px solid #2d3555',
            color: '#9ca3af',
            borderRadius: '7px',
            fontSize: '13px',
            cursor: 'pointer',
          }}
        >
          Reset to Defaults
        </button>
        <button
          onClick={handleSave}
          style={{
            flex: 1,
            padding: '9px',
            background: 'linear-gradient(135deg,#4b6cb7,#182848)',
            border: 'none',
            color: '#fff',
            borderRadius: '7px',
            fontSize: '13px',
            fontWeight: 600,
            cursor: 'pointer',
          }}
        >
          Save Settings
        </button>
      </div>
    </div>
  );
}
