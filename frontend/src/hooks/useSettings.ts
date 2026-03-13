import { useState, useCallback } from 'react';

export interface AppSettings {
  darkMode: boolean;
  compactSidebar: boolean;
  fontSize: 'small' | 'medium' | 'large';
  notifyOCR: boolean;
  notifyUpload: boolean;
  notifyAudit: boolean;
  ocrAutoProcess: boolean;
  ocrLanguage: string;
  ocrConfidenceThreshold: number;
  defaultExportFormat: string;
  itemsPerPage: number;
}

const DEFAULTS: AppSettings = {
  darkMode: true,
  compactSidebar: false,
  fontSize: 'medium',
  notifyOCR: true,
  notifyUpload: true,
  notifyAudit: false,
  ocrAutoProcess: false,
  ocrLanguage: 'eng',
  ocrConfidenceThreshold: 75,
  defaultExportFormat: 'pdf',
  itemsPerPage: 20,
};

const STORAGE_KEY = 'edms_settings';

function loadSettings(): AppSettings {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) return { ...DEFAULTS, ...JSON.parse(stored) };
  } catch {}
  return DEFAULTS;
}

export function useSettings() {
  const [settings, setSettings] = useState<AppSettings>(loadSettings);

  const updateSetting = useCallback((key: string, value: unknown) => {
    if (key === '__reset__') {
      setSettings(DEFAULTS);
      localStorage.setItem(STORAGE_KEY, JSON.stringify(DEFAULTS));
      return;
    }
    setSettings(prev => {
      const next = { ...prev, [key]: value };
      localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
      return next;
    });
  }, []);

  return { settings, updateSetting };
}
