// =============================================================================
// FILE: frontend/src/components/edms/UploadProgress.tsx
// SPRINT 3 — Feature #11: Upload progress list
// PURPOSE : Renders the per-file upload queue returned by useFileUpload.
//           Shows animated progress bar, filename, status icon, and cancel button.
// USAGE:
//   const { uploads, cancelUpload, clearCompleted } = useFileUpload(revisionId);
//   <UploadProgress uploads={uploads} onCancel={cancelUpload}
//                   onClearCompleted={clearCompleted} />
// =============================================================================
import React from 'react';
import type { UploadItem } from '../../hooks/useFileUpload';

const STATUS_ICON: Record<string, string> = {
  queued:    '\u23F3',
  uploading: '\u21BA',
  done:      '\u2713',
  error:     '\u26A0\uFE0F',
};

interface Props {
  uploads:          UploadItem[];
  onCancel:         (id: string) => void;
  onClearCompleted: () => void;
}

export const UploadProgress: React.FC<Props> = ({ uploads, onCancel, onClearCompleted }) => {
  if (uploads.length === 0) return null;

  const doneCount = uploads.filter(u => u.status === 'done').length;

  return (
    <div className="upload-progress">
      <div className="upload-progress__header">
        <span className="upload-progress__title">
          Uploading {uploads.length} file{uploads.length !== 1 ? 's' : ''}
          {doneCount > 0 && ` (${doneCount} done)`}
        </span>
        {doneCount > 0 && (
          <button
            className="upload-progress__clear"
            onClick={onClearCompleted}
          >
            Clear completed
          </button>
        )}
      </div>

      <ul className="upload-progress__list">
        {uploads.map(item => (
          <li
            key={item.id}
            className={`upload-progress__item upload-progress__item--${item.status}`}
          >
            <span
              className="upload-progress__status-icon"
              aria-label={item.status}
            >
              {STATUS_ICON[item.status]}
            </span>

            <div className="upload-progress__info">
              <span className="upload-progress__filename" title={item.file.name}>
                {item.file.name}
              </span>
              <span className="upload-progress__size">
                {(item.file.size / 1024 / 1024).toFixed(2)} MB
              </span>

              {item.status === 'uploading' && (
                <div
                  className="upload-progress__bar-track"
                  role="progressbar"
                  aria-valuenow={item.progress}
                  aria-valuemin={0}
                  aria-valuemax={100}
                >
                  <div
                    className="upload-progress__bar-fill"
                    style={{ width: `${item.progress}%` }}
                  />
                </div>
              )}

              {item.status === 'error' && (
                <span className="upload-progress__error">{item.errorMsg}</span>
              )}
            </div>

            {(item.status === 'uploading' || item.status === 'queued') && (
              <button
                className="upload-progress__cancel"
                onClick={() => onCancel(item.id)}
                aria-label={`Cancel upload of ${item.file.name}`}
              >
                &times;
              </button>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
};
