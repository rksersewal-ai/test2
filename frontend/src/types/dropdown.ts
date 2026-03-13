// =============================================================================
// FILE: frontend/src/types/dropdown.ts
// PURPOSE: TypeScript types for admin-managed dropdown system
// =============================================================================

export interface DropdownItem {
  id: number;
  code: string;
  label: string;
  sort_override: number | null;
  is_system: boolean;
  is_active?: boolean;  // present in admin responses only
}

export interface DropdownGroup {
  group_key: string;
  items: DropdownItem[];
}

// All known group keys - single source of truth
export const DROPDOWN_GROUPS = {
  SECTION:           'section',
  WORK_STATUS:       'work_status',
  WORK_CATEGORY:     'work_category',
  INSPECTION_RESULT: 'inspection_result',
  CONCERNED_OFFICER: 'concerned_officer',
  ENGINEER_STAFF:    'engineer_staff',
  PL_NUMBER_PREFIX:  'pl_number_prefix',
  LOCO_TYPE:         'loco_type',
} as const;

export type DropdownGroupKey = typeof DROPDOWN_GROUPS[keyof typeof DROPDOWN_GROUPS];

export const DROPDOWN_GROUP_LABELS: Record<DropdownGroupKey, string> = {
  section:            'Section',
  work_status:        'Work Status',
  work_category:      'Work Category',
  inspection_result:  'Inspection Result',
  concerned_officer:  'Concerned Officer',
  engineer_staff:     'Engineer / Staff',
  pl_number_prefix:   'PL Number Prefix',
  loco_type:          'Loco Type',
};

export interface DropdownCreatePayload {
  code: string;
  label: string;
  sort_override?: number | null;
}

export interface DropdownUpdatePayload {
  label?: string;
  sort_override?: number | null;
  is_active?: boolean;
}
