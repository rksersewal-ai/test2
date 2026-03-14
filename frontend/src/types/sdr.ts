// =============================================================================
// FILE: frontend/src/types/sdr.ts
// =============================================================================

export const DRAWING_SIZES = ['A0', 'A1', 'A2', 'A3', 'A4'] as const;
export type DrawingSize = typeof DRAWING_SIZES[number];

export const DOC_TYPES = ['DRAWING', 'SPEC'] as const;
export type DocType = typeof DOC_TYPES[number];

export interface DocSearchResult {
  id: number;
  type: DocType;
  number: string;
  title: string;
  current_alteration: string;
}

export interface SDRItem {
  id?: number;
  document_type: DocType;
  drawing?: number | null;
  specification?: number | null;
  document_number: string;
  document_title: string;
  alteration_no: string;
  size: DrawingSize;
  copies: number;
  controlled_copy: boolean;
}

export interface SDRRecord {
  id: number;
  sdr_number: string;
  issue_date: string;
  shop_name: string;
  requesting_official: string;
  issuing_official: string;
  receiving_official: string;
  remarks: string;
  items: SDRItem[];
  total_items: number;
  has_controlled_copy: boolean;
  created_at: string;
}

export type SDRRecordForm = Omit<SDRRecord, 'id' | 'sdr_number' | 'total_items' | 'has_controlled_copy' | 'created_at'>;

export const EMPTY_ITEM: SDRItem = {
  document_type: 'DRAWING',
  drawing: null,
  specification: null,
  document_number: '',
  document_title: '',
  alteration_no: '',
  size: 'A1',
  copies: 1,
  controlled_copy: false,
};

export const EMPTY_FORM: SDRRecordForm = {
  issue_date: new Date().toISOString().slice(0, 10),
  shop_name: '',
  requesting_official: '',
  issuing_official: '',
  receiving_official: '',
  remarks: '',
  items: [{ ...EMPTY_ITEM }],
};
