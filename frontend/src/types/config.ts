// =============================================================================
// FILE: frontend/src/types/config.ts
// TypeScript interfaces matching backend config_mgmt models
// =============================================================================

export type ConfigStatus = 'PENDING' | 'APPROVED' | 'SUPERSEDED' | 'REJECTED';

export type LocoClass =
  | 'WAG-9' | 'WAG-9H' | 'WAG-9HH'
  | 'WAP-7' | 'WAP-5'
  | 'WAG-12B' | 'MEMU' | 'DEMU';

export interface LocoConfig {
  id:             number;
  loco_class:     LocoClass;
  serial_no:      string;
  config_version: string;
  ecn_ref:        string;
  effective_date: string | null;   // YYYY-MM-DD
  changed_by:     string;
  status:         ConfigStatus;
  remarks:        string;
  created_by:     number | null;
  created_by_name:string | null;
  created_at:     string;
  updated_at:     string;
}

export interface ECN {
  id:               number;
  ecn_number:       string;
  subject:          string;
  loco_class:       LocoClass | '';
  description:      string;
  status:           ConfigStatus;
  date:             string | null;  // YYYY-MM-DD
  raised_by:        number | null;
  raised_by_name:   string | null;
  approved_by:      number | null;
  approved_by_name: string | null;
  approved_at:      string | null;
  remarks:          string;
  created_at:       string;
  updated_at:       string;
}
