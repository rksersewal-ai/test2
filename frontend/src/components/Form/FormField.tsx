/**
 * FormField — Enterprise form field wrapper
 * label above input + helper text + inline validation
 */
import { ReactNode, forwardRef, InputHTMLAttributes, SelectHTMLAttributes, TextareaHTMLAttributes } from 'react';

interface FieldWrapProps {
  label?:    string;
  required?: boolean;
  error?:    string;
  helper?:   string;
  children:  ReactNode;
  className?: string;
}

export function FormField({ label, required, error, helper, children, className = '' }: FieldWrapProps) {
  return (
    <div className={`form-group ${className}`}>
      {label && (
        <label className="form-label">
          {label}
          {required && <span className="required" aria-hidden>*</span>}
        </label>
      )}
      {children}
      {error  && <span className="form-error"  role="alert">{error}</span>}
      {!error && helper && <span className="form-helper">{helper}</span>}
    </div>
  );
}

/* ─ Input ────────────────────────────────────────────── */
interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  error?: string;
  compact?: boolean;
}
export const Input = forwardRef<HTMLInputElement, InputProps>(function Input(
  { error, compact, className = '', ...props }, ref
) {
  return (
    <input
      ref={ref}
      className={`form-control${compact ? ' form-control-sm' : ''}${error ? ' error' : ''} ${className}`}
      aria-invalid={!!error}
      {...props}
    />
  );
});

/* ─ Select ──────────────────────────────────────────── */
interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  error?:    string;
  compact?:  boolean;
  options:   { value: string | number; label: string }[];
  placeholder?: string;
}
export function Select({ error, compact, options, placeholder, className = '', ...props }: SelectProps) {
  return (
    <select
      className={`form-control${compact ? ' form-control-sm' : ''}${error ? ' error' : ''} ${className}`}
      aria-invalid={!!error}
      {...props}
    >
      {placeholder && <option value="">{placeholder}</option>}
      {options.map((o) => (
        <option key={o.value} value={o.value}>{o.label}</option>
      ))}
    </select>
  );
}

/* ─ Textarea ─────────────────────────────────────────── */
interface TextareaProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  error?:  string;
}
export function Textarea({ error, className = '', ...props }: TextareaProps) {
  return (
    <textarea
      className={`form-control${error ? ' error' : ''} ${className}`}
      aria-invalid={!!error}
      {...props}
    />
  );
}

/* ─ Checkbox ─────────────────────────────────────────── */
interface CheckboxProps extends InputHTMLAttributes<HTMLInputElement> {
  label: string;
}
export function Checkbox({ label, className = '', ...props }: CheckboxProps) {
  return (
    <label className={`form-check ${className}`}>
      <input type="checkbox" className="form-check-input" {...props} />
      <span className="form-check-label">{label}</span>
    </label>
  );
}
