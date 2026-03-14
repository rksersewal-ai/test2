// =============================================================================
// FILE: frontend/src/components/common/DropdownSelect.tsx
// PURPOSE: Reusable <select> component backed by admin-managed dropdown groups.
//          Alphabetically sorted by default. Shows loading state.
// Usage:
//   <DropdownSelect groupKey="section" value={form.section}
//     onChange={(code) => setField('section', code)} />
// =============================================================================
import React from 'react';
import { useDropdown } from '../../hooks/useDropdown';

interface Props {
  groupKey: string;
  value: string;
  onChange: (code: string) => void;
  placeholder?: string;
  disabled?: boolean;
  className?: string;
  id?: string;
  required?: boolean;
}

export const DropdownSelect: React.FC<Props> = ({
  groupKey, value, onChange, placeholder = '-- Select --',
  disabled, className, id, required,
}) => {
  const { items, loading, error } = useDropdown(groupKey);

  if (error) return <span className="wl-error">Failed to load options</span>;

  return (
    <select
      id={id}
      className={`wl-select ${className ?? ''}`}
      value={value}
      onChange={(e) => onChange(e.target.value)}
      disabled={disabled || loading}
      required={required}
    >
      <option value="">{loading ? 'Loading...' : placeholder}</option>
      {items.map((item) => (
        <option key={item.code} value={item.code}>
          {item.label}
        </option>
      ))}
    </select>
  );
};
