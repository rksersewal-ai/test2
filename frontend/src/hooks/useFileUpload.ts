// =============================================================================
// FILE: frontend/src/hooks/useFileUpload.ts
// SPRINT 3 — Feature #11: Drag-and-Drop File Upload
// PURPOSE : Manages the upload state for one or more files to a given revision.
//           Sends multipart/form-data POST to /api/edms/revisions/{id}/files/
//           Tracks per-file progress using XMLHttpRequest (XHR) so progress
//           events are available (fetch() doesn't expose upload progress).
//
// USAGE:
//   const { uploads, startUpload, clearCompleted } = useFileUpload(revisionId);
//   // In DropZone.onFilesAccepted:
//   startUpload(files);
// =============================================================================
import { useState, useCallback } from 'react';

export type UploadStatus = 'queued' | 'uploading' | 'done' | 'error';

export interface UploadItem {
  id:         string;        // local UUID (Date.now + index)
  file:       File;
  status:     UploadStatus;
  progress:   number;        // 0 – 100
  errorMsg:   string | null;
}

interface UseFileUploadResult {
  uploads:        UploadItem[];
  startUpload:    (files: File[]) => void;
  cancelUpload:   (id: string)   => void;
  clearCompleted: ()             => void;
  isUploading:    boolean;
}

function getCookie(name: string): string {
  const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
  return match ? decodeURIComponent(match[2]) : '';
}

export function useFileUpload(revisionId: number | null): UseFileUploadResult {
  const [uploads, setUploads] = useState<UploadItem[]>([]);
  // Map of upload id → XHR (for cancellation)
  const xhrMap = new Map<string, XMLHttpRequest>();

  const updateItem = (id: string, patch: Partial<UploadItem>) => {
    setUploads(prev =>
      prev.map(u => u.id === id ? { ...u, ...patch } : u)
    );
  };

  const startUpload = useCallback((files: File[]) => {
    if (!revisionId) return;

    const newItems: UploadItem[] = files.map((file, i) => ({
      id:       `${Date.now()}-${i}`,
      file,
      status:   'queued',
      progress: 0,
      errorMsg: null,
    }));

    setUploads(prev => [...prev, ...newItems]);

    newItems.forEach(item => {
      const xhr  = new XMLHttpRequest();
      xhrMap.set(item.id, xhr);

      const formData = new FormData();
      formData.append('file', item.file);
      formData.append('file_name', item.file.name);

      xhr.open('POST', `/api/edms/revisions/${revisionId}/files/`);
      xhr.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));

      xhr.upload.onprogress = (e) => {
        if (e.lengthComputable) {
          const pct = Math.round((e.loaded / e.total) * 100);
          updateItem(item.id, { status: 'uploading', progress: pct });
        }
      };

      xhr.onload = () => {
        xhrMap.delete(item.id);
        if (xhr.status >= 200 && xhr.status < 300) {
          updateItem(item.id, { status: 'done', progress: 100 });
        } else {
          let msg = `HTTP ${xhr.status}`;
          try { msg = JSON.parse(xhr.responseText)?.detail ?? msg; } catch {}
          updateItem(item.id, { status: 'error', errorMsg: msg });
        }
      };

      xhr.onerror = () => {
        xhrMap.delete(item.id);
        updateItem(item.id, { status: 'error', errorMsg: 'Network error' });
      };

      updateItem(item.id, { status: 'uploading' });
      xhr.send(formData);
    });
  }, [revisionId]);

  const cancelUpload = useCallback((id: string) => {
    xhrMap.get(id)?.abort();
    xhrMap.delete(id);
    setUploads(prev => prev.filter(u => u.id !== id));
  }, []);

  const clearCompleted = useCallback(() => {
    setUploads(prev => prev.filter(u => u.status !== 'done'));
  }, []);

  const isUploading = uploads.some(u => u.status === 'uploading');

  return { uploads, startUpload, cancelUpload, clearCompleted, isUploading };
}
