import { useCallback, useRef, useState } from 'react';

export type UploadStatus = 'queued' | 'uploading' | 'done' | 'error';

export interface UploadItem {
  id: string;
  file: File;
  status: UploadStatus;
  progress: number;
  errorMsg: string | null;
}

interface UseFileUploadResult {
  uploads: UploadItem[];
  startUpload: (files: File[]) => void;
  cancelUpload: (id: string) => void;
  clearCompleted: () => void;
  isUploading: boolean;
}

function getCookie(name: string): string {
  const match = document.cookie.match(new RegExp(`(^| )${name}=([^;]+)`));
  return match ? decodeURIComponent(match[2]) : '';
}

export function useFileUpload(revisionId: number | null): UseFileUploadResult {
  const [uploads, setUploads] = useState<UploadItem[]>([]);
  const xhrMapRef = useRef(new Map<string, XMLHttpRequest>());

  const updateItem = (id: string, patch: Partial<UploadItem>) => {
    setUploads(prev => prev.map(item => (item.id === id ? { ...item, ...patch } : item)));
  };

  const startUpload = useCallback((files: File[]) => {
    if (!revisionId) {
      return;
    }

    const xhrMap = xhrMapRef.current;
    const newItems: UploadItem[] = files.map((file, index) => ({
      id: `${Date.now()}-${index}`,
      file,
      status: 'queued',
      progress: 0,
      errorMsg: null,
    }));

    setUploads(prev => [...prev, ...newItems]);

    newItems.forEach(item => {
      const xhr = new XMLHttpRequest();
      xhrMap.set(item.id, xhr);

      const formData = new FormData();
      formData.append('file', item.file);
      formData.append('file_name', item.file.name);

      xhr.open('POST', `/api/edms/revisions/${revisionId}/files/`);
      xhr.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));

      xhr.upload.onprogress = event => {
        if (!event.lengthComputable) {
          return;
        }

        const progress = Math.round((event.loaded / event.total) * 100);
        updateItem(item.id, { status: 'uploading', progress });
      };

      xhr.onload = () => {
        xhrMap.delete(item.id);
        if (xhr.status >= 200 && xhr.status < 300) {
          updateItem(item.id, { status: 'done', progress: 100 });
          return;
        }

        let errorMsg = `HTTP ${xhr.status}`;
        try {
          errorMsg = JSON.parse(xhr.responseText)?.detail ?? errorMsg;
        } catch {
          // Ignore JSON parse failures and keep the status-derived message.
        }
        updateItem(item.id, { status: 'error', errorMsg });
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
    const xhrMap = xhrMapRef.current;
    xhrMap.get(id)?.abort();
    xhrMap.delete(id);
    setUploads(prev => prev.filter(item => item.id !== id));
  }, []);

  const clearCompleted = useCallback(() => {
    setUploads(prev => prev.filter(item => item.status !== 'done'));
  }, []);

  const isUploading = uploads.some(item => item.status === 'uploading');

  return { uploads, startUpload, cancelUpload, clearCompleted, isUploading };
}
