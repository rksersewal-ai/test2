// =============================================================================
// FILE: frontend/src/hooks/useSettings.ts
// BUG FIX 1: __reset__ magic key was used to trigger reset but updateSetting()
//            only writes to localStorage — the state was NEVER actually reset.
//            Now handles '__reset__' as a special action inside updateSetting.
// BUG FIX 2: 'Save Settings' button in SettingsPage had NO onClick handler —
//            clicking it did nothing. Added persist() fn for explicit save.
// BUG FIX 3: Dark mode toggle called updateSetting but ThemeContext was never
//            notified. Now syncs document.documentElement class on every change.
// =============================================================================
import { useState, useCallback, useEffect } from 'react';

export interface AppSettings {
  darkMode                : boolean;
  compactSidebar          : boolean;
  fontSize                : 'small' | 'medium' | 'large';
  notifyOCR               : boolean;
  notifyUpload            : boolean;
  notifyAudit             : boolean;
  ocrAutoProcess          : boolean;
  ocrLanguage             : string;
  ocrConfidenceThreshold  : number;
  defaultExportFormat     : 'pdf' | 'xlsx' | 'csv' | 'json';
  itemsPerPage            : number;
}

const DEFAULTS: AppSettings = {
  darkMode                : true,
  compactSidebar          : false,
  fontSize                : 'medium',
  notifyOCR               : true,
  notifyUpload            : true,
  notifyAudit             : false,
  ocrAutoProcess          : true,
  ocrLanguage             : 'eng',
  ocrConfidenceThreshold  : 75,
  defaultExportFormat     : 'xlsx',
  itemsPerPage            : 20,
};

const STORAGE_KEY = 'edms_settings';

function load(): AppSettings {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? { ...DEFAULTS, ...JSON.parse(raw) } : { ...DEFAULTS };
  } catch { return { ...DEFAULTS }; }
}

function applyDarkMode(dark: boolean) {
  document.documentElement.classList.toggle('dark', dark);
}

export function useSettings() {
  const [settings, setSettings] = useState<AppSettings>(load);

  // Apply dark mode on mount and whenever setting changes
  useEffect(() => { applyDarkMode(settings.darkMode); }, [settings.darkMode]);

  const updateSetting = useCallback(
    <K extends keyof AppSettings | '__reset__'>(
      key: K,
      value: K extends keyof AppSettings ? AppSettings[K] : boolean
    ) => {
      if (key === '__reset__') {
        // BUG FIX: actually reset state to DEFAULTS, not just write to storage
        setSettings({ ...DEFAULTS });
        localStorage.setItem(STORAGE_KEY, JSON.stringify(DEFAULTS));
        applyDarkMode(DEFAULTS.darkMode);
        return;
      }
      setSettings(prev => {
        const next = { ...prev, [key as keyof AppSettings]: value };
        // Auto-persist on every change (live settings)
        localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
        return next;
      });
    },
    []
  );

  // Explicit save (for the Save Settings button)
  const persist = useCallback(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(settings));
    return true;
  }, [settings]);

  return { settings, updateSetting, persist };
}
