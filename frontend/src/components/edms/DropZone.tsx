// =============================================================================
// FILE: frontend/src/components/edms/DropZone.tsx
// SPRINT 3 — Feature #11: Drag-and-Drop File Upload
// PURPOSE : Reusable file drop zone for uploading revision attachments.
//           Accepts PDF / CAD / Office files, enforces 50 MB limit per file.
//           Calls onFilesAccepted with valid File[] so the parent page can
//           initiate the actual upload via useFileUpload hook.
//
// USAGE:
//   <DropZone
//     onFilesAccepted={files => startUpload(files)}
//     accept={['.pdf', '.dwg', '.dxf', '.doc', '.docx', '.xlsx']}
//     maxFileSizeMB={50}
//     multiple
//   />
// =============================================================================
import React, { useCallback, useRef, useState, DragEvent, ChangeEvent } from 'react';

const ACCEPT_DEFAULT  = ['.pdf', '.dwg', '.dxf', '.doc', '.docx', '.xls', '.xlsx', '.tiff', '.tif', '.jpg', '.png'];
const MAX_SIZE_MB_DEF = 50;

interface Props {
  onFilesAccepted:  (files: File[]) => void;
  onFilesRejected?: (files: File[], reason: string) => void;
  accept?:          string[];
  maxFileSizeMB?:   number;
  multiple?:        boolean;
  disabled?:        boolean;
  label?:           string;
}

export const DropZone: React.FC<Props> = ({
  onFilesAccepted,
  onFilesRejected,
  accept        = ACCEPT_DEFAULT,
  maxFileSizeMB = MAX_SIZE_MB_DEF,
  multiple      = true,
  disabled      = false,
  label         = 'Drag & drop files here, or click to browse',
}) => {
  const [isDragOver, setIsDragOver] = useState(false);
  const [errors,     setErrors]     = useState<string[]>([]);
  const inputRef = useRef<HTMLInputElement>(null);

  const validate = useCallback((rawFiles: File[]): [File[], File[]] => {
    const maxBytes   = maxFileSizeMB * 1024 * 1024;
    const acceptExts = accept.map(e => e.toLowerCase());

    const valid:    File[] = [];
    const rejected: File[] = [];

    rawFiles.forEach(file => {
      const ext = '.' + file.name.split('.').pop()?.toLowerCase();
      const sizeOk = file.size <= maxBytes;
      const typeOk = acceptExts.includes(ext);
      if (sizeOk && typeOk) valid.push(file);
      else rejected.push(file);
    });
    return [valid, rejected];
  }, [accept, maxFileSizeMB]);

  const handle = useCallback((rawFiles: FileList | null) => {
    if (!rawFiles || disabled) return;
    const arr = Array.from(rawFiles);
    const [valid, rejected] = validate(arr);

    const newErrors: string[] = [];
    if (rejected.length > 0) {
      rejected.forEach(f => {
        const ext = '.' + f.name.split('.').pop()?.toLowerCase();
        const acceptExts = accept.map(e => e.toLowerCase());
        if (!acceptExts.includes(ext)) {
          newErrors.push(`"${f.name}" — unsupported format (${ext})`);
        } else {
          newErrors.push(`"${f.name}" — exceeds ${maxFileSizeMB} MB limit`);
        }
      });
    }
    setErrors(newErrors);
    if (valid.length > 0) onFilesAccepted(valid);
    if (rejected.length > 0) onFilesRejected?.(rejected, newErrors.join('; '));
  }, [accept, disabled, maxFileSizeMB, onFilesAccepted, onFilesRejected, validate]);

  const onDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault(); e.stopPropagation();
    if (!disabled) setIsDragOver(true);
  };
  const onDragLeave = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault(); e.stopPropagation();
    setIsDragOver(false);
  };
  const onDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault(); e.stopPropagation();
    setIsDragOver(false);
    handle(e.dataTransfer.files);
  };
  const onChange = (e: ChangeEvent<HTMLInputElement>) => {
    handle(e.target.files);
    e.target.value = ''; // allow re-selecting the same file
  };
  const onKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ' ') inputRef.current?.click();
  };

  const cls = [
    'dropzone',
    isDragOver ? 'dropzone--active' : '',
    disabled   ? 'dropzone--disabled' : '',
  ].filter(Boolean).join(' ');

  return (
    <div
      className={cls}
      onDragOver={onDragOver}
      onDragEnter={onDragOver}
      onDragLeave={onDragLeave}
      onDrop={onDrop}
      onClick={() => !disabled && inputRef.current?.click()}
      onKeyDown={onKeyDown}
      role="button"
      tabIndex={disabled ? -1 : 0}
      aria-label={label}
      aria-disabled={disabled}
    >
      <input
        ref={inputRef}
        type="file"
        multiple={multiple}
        accept={accept.join(',')}
        className="dropzone__input"
        onChange={onChange}
        tabIndex={-1}
        aria-hidden
      />

      <span className="dropzone__icon" aria-hidden>
        {isDragOver ? '\uD83D\uDCC2' : '\uD83D\uDCC1'}
      </span>
      <p className="dropzone__label">{label}</p>
      <p className="dropzone__hint">
        Accepted: {accept.join(', ')} &nbsp;&bull;&nbsp; Max {maxFileSizeMB} MB per file
      </p>

      {errors.length > 0 && (
        <ul className="dropzone__errors" role="alert">
          {errors.map((err, i) => (
            <li key={i} className="dropzone__error-item">{err}</li>
          ))}
        </ul>
      )}
    </div>
  );
};
