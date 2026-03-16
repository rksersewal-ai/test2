// =============================================================================
// SearchBar — reusable search input with clear button
// =============================================================================
import React from 'react';
import './SearchBar.css';

interface Props {
  value:       string;
  onChange:    (v: string) => void;
  placeholder?: string;
  width?:       number | string;
  id?:          string;
  'aria-label'?: string;
}

export default function SearchBar({ value, onChange, placeholder = 'Search…', width = 320, id, 'aria-label': ariaLabel }: Props) {
  const defaultLabel = 'Search';
  return (
    <div className="search-bar" style={{ width }}>
      <span className="search-icon" aria-hidden="true">🔍</span>
      <input
        id={id}
        type="search"
        value={value}
        onChange={e => onChange(e.target.value)}
        placeholder={placeholder}
        aria-label={placeholder}
      />
      {value && (
        <button
          className="search-clear"
          onClick={() => onChange('')}
          title="Clear"
          aria-label="Clear search"
        >
          ✕
        </button>
      )}
    </div>
  );
}
