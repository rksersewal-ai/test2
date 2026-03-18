import React, { useCallback, useEffect, useRef, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Btn, ConfirmDialog, PageHeader, SearchBar, Toast } from '../components/common';
import type { ToastMsg } from '../components/common';
import { usePreviewTabs } from '../context/PreviewTabsContext';
import { documentService } from '../services/documentService';
import './DocumentListPage.css';

const STATUS_CLASS: Record<string, string> = {
  DRAFT: 'doc-badge-draft',
  PENDING_REVIEW: 'doc-badge-review',
  APPROVED: 'doc-badge-approved',
  OBSOLETE: 'doc-badge-obsolete',
  REJECTED: 'doc-badge-rejected',
  ACTIVE: 'doc-badge-approved',
  SUPERSEDED: 'doc-badge-review',
};

interface DocumentTypeOption {
  id: number;
  code: string;
  name: string;
}

export default function DocumentListPage() {
  const [docs, setDocs] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(false);
  const [toast, setToast] = useState<ToastMsg | null>(null);
  const [confirm, setConfirm] = useState<number | null>(null);
  const [showUpload, setShowUpload] = useState(false);
  const [search, setSearch] = useState('');
  const [searchParams] = useSearchParams();
  const [status, setStatus] = useState(searchParams.get('status') ?? '');
  const navigate = useNavigate();
  const { openTab } = usePreviewTabs();
  const PAGE_SIZE = 20;

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const params: Record<string, string> = {
        page: String(page),
        page_size: String(PAGE_SIZE),
      };
      if (search) params.search = search;
      if (status) params.status = status;
      const data = await documentService.list(params);
      setDocs(data.results ?? data);
      setTotal(data.count ?? data.total_count ?? 0);
    } catch {
      setToast({ type: 'error', text: 'Failed to load documents.' });
    } finally {
      setLoading(false);
    }
  }, [page, search, status]);

  useEffect(() => {
    void load();
  }, [load]);

  const handleDelete = async () => {
    if (!confirm) return;
    try {
      await documentService.delete(confirm);
      setToast({ type: 'success', text: 'Document deleted.' });
      await load();
    } catch {
      setToast({ type: 'error', text: 'Delete failed.' });
    } finally {
      setConfirm(null);
    }
  };

  const totalPages = Math.ceil(total / PAGE_SIZE) || 1;

  return (
    <div className="doc-list-page">
      <PageHeader title="Documents" subtitle="Controlled engineering documents - drawings, specs, manuals">
        <Btn size="sm" onClick={() => setShowUpload(true)}>Upload Document</Btn>
      </PageHeader>

      <Toast msg={toast} onClose={() => setToast(null)} />
      <ConfirmDialog
        open={!!confirm}
        title="Delete Document"
        message="Permanently delete this document? This cannot be undone."
        confirmLabel="Delete"
        onConfirm={() => void handleDelete()}
        onCancel={() => setConfirm(null)}
      />

      {showUpload && (
        <UploadModal
          onClose={() => setShowUpload(false)}
          onSuccess={() => {
            setShowUpload(false);
            void load();
            setToast({ type: 'success', text: 'Document uploaded successfully.' });
          }}
        />
      )}

      <div className="doc-toolbar">
        <SearchBar
          value={search}
          onChange={(value) => {
            setSearch(value);
            setPage(1);
          }}
          placeholder="Search title, document number, keywords..."
          width={320}
        />
        <select
          value={status}
          onChange={(event) => {
            setStatus(event.target.value);
            setPage(1);
          }}
        >
          <option value="">All Status</option>
          <option value="DRAFT">Draft</option>
          <option value="ACTIVE">Active</option>
          <option value="SUPERSEDED">Superseded</option>
          <option value="OBSOLETE">Obsolete</option>
        </select>
        <Btn size="sm" variant="ghost" onClick={() => void load()}>Refresh</Btn>
      </div>

      <div className="doc-table-wrap">
        <table className="doc-table">
          <thead>
            <tr>
              <th>Title</th>
              <th>Doc No.</th>
              <th>Type</th>
              <th>Status</th>
              <th>Version</th>
              <th>Modified</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {loading && (
              <tr>
                <td colSpan={7} className="doc-center doc-muted">Loading...</td>
              </tr>
            )}
            {!loading && docs.length === 0 && (
              <tr>
                <td colSpan={7} className="doc-center doc-muted">No documents found.</td>
              </tr>
            )}
            {docs.map((doc) => (
              <tr key={doc.id}>
                <td className="doc-title" title={doc.title}>{doc.title}</td>
                <td className="doc-mono">{doc.document_number ?? doc.drawing_number ?? '-'}</td>
                <td className="doc-muted">{doc.document_type_name ?? doc.document_type ?? doc.doc_type ?? '-'}</td>
                <td>
                  <span className={`doc-badge ${STATUS_CLASS[doc.status] ?? ''}`}>
                    {String(doc.status ?? '').replace('_', ' ')}
                  </span>
                </td>
                <td className="doc-center doc-muted">{doc.version ?? doc.revision ?? '-'}</td>
                <td className="doc-muted" style={{ fontSize: 11 }}>
                  {doc.updated_at ? new Date(doc.updated_at).toLocaleDateString('en-IN') : '-'}
                </td>
                <td className="doc-actions">
                  <Btn size="sm" variant="ghost" onClick={() => navigate(`/documents/${doc.id}`)}>View</Btn>
                  <Btn
                    size="sm"
                    variant="secondary"
                    onClick={() => {
                      openTab({
                        id: `doc-${doc.id}`,
                        docNumber: doc.document_number ?? doc.drawing_number ?? `DOC-${doc.id}`,
                        title: doc.title,
                        fileUrl: doc.file_url ?? `/api/v1/edms/documents/${doc.id}/file/`,
                        fileId: 0,
                        documentId: doc.id,
                        pageCount: 1,
                        mimeType: 'application/pdf',
                      });
                      navigate('/preview');
                    }}
                  >
                    Preview
                  </Btn>
                  <Btn size="sm" variant="danger" onClick={() => setConfirm(doc.id)}>Delete</Btn>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="doc-pagination">
        <span className="doc-muted">{total} documents</span>
        <div className="doc-page-btns">
          <Btn size="sm" variant="secondary" disabled={page <= 1} onClick={() => setPage((current) => current - 1)}>
            Prev
          </Btn>
          <span>Page {page} / {totalPages}</span>
          <Btn size="sm" variant="secondary" disabled={page >= totalPages} onClick={() => setPage((current) => current + 1)}>
            Next
          </Btn>
        </div>
      </div>
    </div>
  );
}

function UploadModal({ onClose, onSuccess }: { onClose: () => void; onSuccess: () => void }) {
  const [form, setForm] = useState({
    title: '',
    document_number: '',
    document_type: '',
    version: 'A',
    description: '',
  });
  const [documentTypes, setDocumentTypes] = useState<DocumentTypeOption[]>([]);
  const [file, setFile] = useState<File | null>(null);
  const [saving, setSaving] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const fileRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    let cancelled = false;
    documentService.listDocumentTypes().then((types) => {
      if (cancelled) return;
      setDocumentTypes(types);
      if (types.length > 0) {
        setForm((current) => (
          current.document_type ? current : { ...current, document_type: types[0].code }
        ));
      }
    }).catch(() => {
      if (!cancelled) {
        setErrors((current) => ({ ...current, _global: 'Failed to load document types.' }));
      }
    });
    return () => {
      cancelled = true;
    };
  }, []);

  const setField = (field: string, value: string) => {
    setForm((current) => ({ ...current, [field]: value }));
    setErrors((current) => ({ ...current, [field]: '', _global: current._global && field === 'document_type' ? '' : current._global }));
  };

  const validate = () => {
    const nextErrors: Record<string, string> = {};
    if (!form.title.trim()) nextErrors.title = 'Required';
    if (!form.document_number.trim()) nextErrors.document_number = 'Required';
    if (!form.document_type) nextErrors.document_type = 'Required';
    if (!file) nextErrors.file = 'Please select a PDF or image file.';
    setErrors(nextErrors);
    return Object.keys(nextErrors).length === 0;
  };

  const handleSave = async () => {
    if (!validate() || !file) return;
    setSaving(true);
    try {
      const formData = new FormData();
      Object.entries(form).forEach(([key, value]) => formData.append(key, value));
      formData.append('file', file);
      await documentService.create(formData);
      onSuccess();
    } catch (error: any) {
      setErrors({ _global: JSON.stringify(error?.response?.data ?? 'Upload failed.') });
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="doc-modal-overlay" onClick={onClose}>
      <div className="doc-modal" onClick={(event) => event.stopPropagation()}>
        <div className="doc-modal-header">
          <span>Upload Document</span>
          <button className="doc-modal-close" onClick={onClose}>x</button>
        </div>
        <div className="doc-modal-body">
          {errors._global && <div className="doc-alert-error">{errors._global}</div>}

          <div className="doc-form-grid">
            <div className="doc-field doc-full">
              <label>Title <span className="doc-req">*</span></label>
              <input
                type="text"
                value={form.title}
                onChange={(event) => setField('title', event.target.value)}
                placeholder="Document title..."
              />
              {errors.title && <span className="doc-err">{errors.title}</span>}
            </div>

            <div className="doc-field">
              <label>Document Number <span className="doc-req">*</span></label>
              <input
                type="text"
                value={form.document_number}
                onChange={(event) => setField('document_number', event.target.value)}
                placeholder="e.g. PLW/WAG9/TM/001"
              />
              {errors.document_number && <span className="doc-err">{errors.document_number}</span>}
            </div>

            <div className="doc-field">
              <label>Document Type <span className="doc-req">*</span></label>
              <select value={form.document_type} onChange={(event) => setField('document_type', event.target.value)}>
                {documentTypes.length === 0 && <option value="">Loading...</option>}
                {documentTypes.map((option) => (
                  <option key={option.id} value={option.code}>{option.name}</option>
                ))}
              </select>
              {errors.document_type && <span className="doc-err">{errors.document_type}</span>}
            </div>

            <div className="doc-field">
              <label>Version / Revision</label>
              <input
                type="text"
                value={form.version}
                onChange={(event) => setField('version', event.target.value)}
                placeholder="A, 1.0, R2..."
              />
            </div>

            <div className="doc-field doc-full">
              <label>Description</label>
              <textarea
                rows={2}
                value={form.description}
                onChange={(event) => setField('description', event.target.value)}
              />
            </div>

            <div className="doc-field doc-full">
              <label>File <span className="doc-req">*</span></label>
              <div
                className={`doc-dropzone${file ? ' doc-dropzone--filled' : ''}`}
                onClick={() => fileRef.current?.click()}
                onDragOver={(event) => event.preventDefault()}
                onDrop={(event) => {
                  event.preventDefault();
                  const droppedFile = event.dataTransfer.files[0];
                  if (droppedFile) setFile(droppedFile);
                }}
              >
                {file
                  ? `${file.name} (${(file.size / 1024).toFixed(1)} KB)`
                  : 'Click or drag and drop a PDF or image file.'}
              </div>
              <input
                ref={fileRef}
                type="file"
                style={{ display: 'none' }}
                accept=".pdf,.tif,.tiff,.jpg,.jpeg,.png"
                onChange={(event) => {
                  const selectedFile = event.target.files?.[0];
                  if (selectedFile) setFile(selectedFile);
                }}
              />
              {errors.file && <span className="doc-err">{errors.file}</span>}
            </div>
          </div>
        </div>

        <div className="doc-modal-footer">
          <Btn variant="secondary" onClick={onClose} disabled={saving}>Cancel</Btn>
          <Btn variant="primary" onClick={() => void handleSave()} loading={saving}>Upload</Btn>
        </div>
      </div>
    </div>
  );
}
