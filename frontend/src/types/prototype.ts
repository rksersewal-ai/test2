// =============================================================================
// FILE: frontend/src/types/prototype.ts
// TypeScript interfaces matching backend prototype models
// =============================================================================

export type InspectionType =
  | 'Prototype' | 'Periodic' | 'Special'
  | 'PDI' | 'ReturnToService';

export type InspectionStatus =
  | 'Open' | 'In Progress' | 'Pass' | 'Fail' | 'Closed';

export type PunchStatus = 'Open' | 'Closed';

export interface PunchItem {
  id:             number;
  inspection:     number;
  description:    string;
  status:         PunchStatus;
  raised_by:      string;
  closed_by:      number | null;
  closed_by_name: string | null;
  closed_at:      string | null;
  remarks:        string;
  created_at:     string;
  updated_at:     string;
}

export interface Inspection {
  id:               number;
  loco_number:      string;
  loco_class:       string;
  inspection_type:  InspectionType;
  inspection_date:  string;         // YYYY-MM-DD
  inspector:        string;
  status:           InspectionStatus;
  remarks:          string;
  created_by:       number | null;
  created_by_name:  string | null;
  created_at:       string;
  updated_at:       string;
  punch_items:      PunchItem[];    // present on detail only
  open_punch_count: number;
}
