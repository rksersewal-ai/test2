import React from 'react';
import { useSettings, type AppSettings } from '../hooks/useSettings';
import styles from './SettingsPanel.module.css';

interface SettingsPanelProps {
  open: boolean;
  onClose: () => void;
}

export default function SettingsPanel({ open, onClose }: SettingsPanelProps) {
  const { settings, updateSetting } = useSettings();

  return (
    <>
      {open && <div className={styles.overlay} onClick={onClose} />}
      <div className={`${styles.panel} ${open ? styles.open : ''}`}>
        <div className={styles.header}>
          <span className={styles.title}>⚙️ Settings</span>
          <button className={styles.closeBtn} onClick={onClose} aria-label="Close settings">✕</button>
        </div>

        <div className={styles.body}>
          {/* APPEARANCE */}
          <section className={styles.section}>
            <h3 className={styles.sectionTitle}>Appearance</h3>
            <label className={styles.row}>
              <span>Dark Mode</span>
              <input
                type="checkbox"
                checked={settings.darkMode}
                onChange={e => updateSetting('darkMode', e.target.checked)}
              />
            </label>
            <label className={styles.row}>
              <span>Compact Sidebar</span>
              <input
                type="checkbox"
                checked={settings.compactSidebar}
                onChange={e => updateSetting('compactSidebar', e.target.checked)}
              />
            </label>
            <label className={styles.row}>
              <span>Font Size</span>
              <select
                className={styles.select}
                value={settings.fontSize}
                onChange={e => updateSetting('fontSize', e.target.value as AppSettings['fontSize'])}
              >
                <option value="small">Small</option>
                <option value="medium">Medium</option>
                <option value="large">Large</option>
              </select>
            </label>
          </section>

          {/* NOTIFICATIONS */}
          <section className={styles.section}>
            <h3 className={styles.sectionTitle}>Notifications</h3>
            <label className={styles.row}>
              <span>OCR Completion Alerts</span>
              <input
                type="checkbox"
                checked={settings.notifyOCR}
                onChange={e => updateSetting('notifyOCR', e.target.checked)}
              />
            </label>
            <label className={styles.row}>
              <span>Document Upload Alerts</span>
              <input
                type="checkbox"
                checked={settings.notifyUpload}
                onChange={e => updateSetting('notifyUpload', e.target.checked)}
              />
            </label>
            <label className={styles.row}>
              <span>Audit Log Alerts</span>
              <input
                type="checkbox"
                checked={settings.notifyAudit}
                onChange={e => updateSetting('notifyAudit', e.target.checked)}
              />
            </label>
          </section>

          {/* OCR PIPELINE */}
          <section className={styles.section}>
            <h3 className={styles.sectionTitle}>OCR Pipeline</h3>
            <label className={styles.row}>
              <span>Auto-process on Upload</span>
              <input
                type="checkbox"
                checked={settings.ocrAutoProcess}
                onChange={e => updateSetting('ocrAutoProcess', e.target.checked)}
              />
            </label>
            <label className={styles.row}>
              <span>OCR Language</span>
              <select
                className={styles.select}
                value={settings.ocrLanguage}
                onChange={e => updateSetting('ocrLanguage', e.target.value)}
              >
                <option value="eng">English</option>
                <option value="hin">Hindi</option>
                <option value="eng+hin">English + Hindi</option>
              </select>
            </label>
            <label className={styles.row}>
              <span>Confidence Threshold (%)</span>
              <input
                type="number"
                className={styles.numberInput}
                min={50}
                max={100}
                value={settings.ocrConfidenceThreshold}
                onChange={e => updateSetting('ocrConfidenceThreshold', Number(e.target.value))}
              />
            </label>
          </section>

          {/* DATA */}
          <section className={styles.section}>
            <h3 className={styles.sectionTitle}>Data & Export</h3>
            <label className={styles.row}>
              <span>Default Export Format</span>
              <select
                className={styles.select}
                value={settings.defaultExportFormat}
                onChange={e => updateSetting('defaultExportFormat', e.target.value as AppSettings['defaultExportFormat'])}
              >
                <option value="pdf">PDF</option>
                <option value="xlsx">Excel (XLSX)</option>
                <option value="csv">CSV</option>
                <option value="json">JSON</option>
              </select>
            </label>
            <label className={styles.row}>
              <span>Items per Page</span>
              <select
                className={styles.select}
                value={settings.itemsPerPage}
                onChange={e => updateSetting('itemsPerPage', Number(e.target.value))}
              >
                <option value={20}>20</option>
                <option value={50}>50</option>
                <option value={100}>100</option>
              </select>
            </label>
          </section>
        </div>

        <div className={styles.footer}>
          <button className={styles.resetBtn} onClick={() => updateSetting('__reset__', true)}>Reset to Defaults</button>
          <button className={styles.saveBtn} onClick={onClose}>Save & Close</button>
        </div>
      </div>
    </>
  );
}
