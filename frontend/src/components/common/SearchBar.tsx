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
}

export default function SearchBar({ value, onChange, placeholder = 'Search…', width = 320 }: Props) {
  return (
    <div className="search-bar" style={{ width }}>
      <span className="search-icon" aria-hidden="true">🔍</span>
      <input
        type="text"
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
