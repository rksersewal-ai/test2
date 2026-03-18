import { useCallback, useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Btn, ConfirmDialog, PageHeader, SearchBar, Toast } from '../../components/common';
import type { ToastMsg } from '../../components/common';
import { useAuthContext } from '../../context/AuthContext';
import { workLedgerService } from '../../services/workLedgerService';
import type { WorkLedgerListItem } from '../../types/workLedger';
import './WorkLedgerPage.css';

type EntryRow = WorkLedgerListItem & { status: string };
type ReviewAction = 'approve' | 'reject';

const STATUS_CLASS: Record<string, string> = {
  DRAFT: 'wl-badge-draft',
  SUBMITTED: 'wl-badge-submitted',
  VERIFIED: 'wl-badge-verified',
  APPROVED: 'wl-badge-approved',
  RETURNED: 'wl-badge-returned',
};

interface ReviewState {
  entry: EntryRow;
  remarks: string;
}

export default function WorkLedgerPage() {
  const navigate = useNavigate();
  const { user } = useAuthContext();
  const [entries, setEntries] = useState<EntryRow[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [status, setStatus] = useState('');
  const [loading, setLoading] = useState(false);
  const [toast, setToast] = useState<ToastMsg | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<EntryRow | null>(null);
  const [reviewState, setReviewState] = useState<ReviewState | null>(null);
  const pageSize = 20;
  const canReviewEntries = Boolean(
    user?.is_staff || ['ADMIN', 'SECTION_HEAD'].includes(String(user?.role ?? '').toUpperCase())
  );

  const params = useMemo(() => {
    const next: Record<string, string> = {
      page: String(page),
      page_size: String(pageSize),
    };
    if (search.trim()) next.search = search.trim();
    if (status) next.status = status;
    return next;
  }, [page, search, status]);

  const loadEntries = useCallback(async () => {
    setLoading(true);
    try {
      const data = await workLedgerService.listEntries(params);
      setEntries((data.results ?? []) as EntryRow[]);
      setTotal(data.count ?? data.total_count ?? 0);
    } catch {
      setToast({ type: 'error', text: 'Failed to load work entries.' });
    } finally {
      setLoading(false);
    }
  }, [params]);

  useEffect(() => {
    void loadEntries();
  }, [loadEntries]);

  const totalPages = Math.max(1, Math.ceil(total / pageSize));

  const handleDelete = async () => {
    if (!deleteTarget) return;
    try {
      await workLedgerService.deleteEntry(deleteTarget.work_id);
      setToast({ type: 'success', text: 'Entry deleted.' });
      await loadEntries();
    } catch {
      setToast({ type: 'error', text: 'Delete failed.' });
    } finally {
      setDeleteTarget(null);
    }
  };

  const handleSubmit = async (entry: EntryRow) => {
    try {
      await workLedgerService.submitEntry(entry.work_id);
      setToast({ type: 'success', text: 'Entry submitted for verification.' });
      await loadEntries();
    } catch {
      setToast({ type: 'error', text: 'Submit failed.' });
    }
  };

  const handleReview = async (action: ReviewAction) => {
    if (!reviewState) return;
    try {
      await workLedgerService.verifyEntry(reviewState.entry.work_id, action, reviewState.remarks || undefined);
      setToast({
        type: 'success',
        text: action === 'approve' ? 'Entry approved.' : 'Entry returned for correction.',
      });
      await loadEntries();
    } catch {
      setToast({ type: 'error', text: 'Action failed.' });
    } finally {
      setReviewState(null);
    }
  };

  const handleDownload = async (format: 'pdf' | 'xlsx') => {
    const now = new Date();
    try {
      const blob = await workLedgerService.downloadReport(
        now.getFullYear(),
        now.getMonth() + 1,
        format,
      );
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `work-ledger-${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}.${format}`;
      link.click();
      URL.revokeObjectURL(url);
    } catch {
      setToast({ type: 'error', text: 'Report download failed.' });
    }
  };

  return (
    <div className="wl-page">
      <PageHeader title="Work Ledger" subtitle="Track entries, review status, and export reports.">
        <Btn size="sm" variant="secondary" onClick={() => handleDownload('xlsx')}>Excel Report</Btn>
        <Btn size="sm" variant="secondary" onClick={() => handleDownload('pdf')}>PDF Report</Btn>
        <Btn size="sm" onClick={() => navigate('/work-ledger/new')}>New Entry</Btn>
      </PageHeader>

      <Toast msg={toast} onClose={() => setToast(null)} />

      <ConfirmDialog
        open={!!deleteTarget}
        title="Delete Entry"
        message="Delete this work entry? This cannot be undone."
        confirmLabel="Delete"
        onConfirm={handleDelete}
        onCancel={() => setDeleteTarget(null)}
      />

      {reviewState && (
        <div className="wl-modal-overlay" onClick={() => setReviewState(null)}>
          <div className="wl-modal" onClick={(event) => event.stopPropagation()}>
            <div className="wl-modal-title">Review Entry</div>
            <p style={{ fontSize: 13, color: '#444', marginBottom: 12 }}>
              Entry: <strong>{reviewState.entry.description.slice(0, 80)}</strong>
            </p>
            <label style={{ fontSize: 12, fontWeight: 600 }}>Remarks (optional)</label>
            <textarea
              className="wl-remarks"
              rows={3}
              value={reviewState.remarks}
              onChange={(event) => {
                setReviewState((current) => (current ? { ...current, remarks: event.target.value } : current));
              }}
            />
            <div className="wl-modal-actions">
              <Btn variant="secondary" size="sm" onClick={() => setReviewState(null)}>Cancel</Btn>
              <Btn variant="danger" size="sm" onClick={() => handleReview('reject')}>Return</Btn>
              <Btn variant="primary" size="sm" onClick={() => handleReview('approve')}>Approve</Btn>
            </div>
          </div>
        </div>
      )}

      <div className="wl-toolbar">
        <SearchBar
          value={search}
          onChange={(value) => {
            setSearch(value);
            setPage(1);
          }}
          placeholder="Search work code, description, or reference..."
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
          <option value="SUBMITTED">Submitted</option>
          <option value="VERIFIED">Verified</option>
          <option value="APPROVED">Approved</option>
          <option value="RETURNED">Returned</option>
        </select>
        <Btn size="sm" variant="ghost" onClick={() => void loadEntries()}>Refresh</Btn>
      </div>

      <div className="wl-table-wrap">
        <table className="wl-table">
          <thead>
            <tr>
              <th>Work Code</th>
              <th>Date</th>
              <th>Section</th>
              <th>Category</th>
              <th>Description</th>
              <th>Reference</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {loading && (
              <tr>
                <td colSpan={8} className="wl-center wl-muted">Loading...</td>
              </tr>
            )}
            {!loading && entries.length === 0 && (
              <tr>
                <td colSpan={8} className="wl-center wl-muted">No work entries found.</td>
              </tr>
            )}
            {entries.map((entry) => {
              const editable = ['DRAFT', 'RETURNED'].includes(entry.status);
              const submittable = ['DRAFT', 'RETURNED'].includes(entry.status);
              const reviewable = canReviewEntries && entry.status === 'SUBMITTED';

              return (
                <tr key={entry.work_id}>
                  <td className="wl-mono">{entry.work_code}</td>
                  <td className="wl-muted">{entry.received_date}</td>
                  <td>{entry.section}</td>
                  <td>{entry.work_category_label}</td>
                  <td className="wl-desc">{entry.description}</td>
                  <td className="wl-mono">{formatReference(entry)}</td>
                  <td>
                    <span className={`wl-badge ${STATUS_CLASS[entry.status] ?? ''}`}>
                      {entry.status.replace('_', ' ')}
                    </span>
                  </td>
                  <td className="wl-actions">
                    {editable && (
                      <Btn size="sm" variant="secondary" onClick={() => navigate(`/work-ledger/${entry.work_id}/edit`)}>
                        Edit
                      </Btn>
                    )}
                    {submittable && (
                      <Btn size="sm" variant="gold" onClick={() => void handleSubmit(entry)}>
                        Submit
                      </Btn>
                    )}
                    {reviewable && (
                      <Btn
                        size="sm"
                        variant="primary"
                        onClick={() => setReviewState({ entry, remarks: '' })}
                      >
                        Review
                      </Btn>
                    )}
                    {editable && (
                      <Btn size="sm" variant="danger" onClick={() => setDeleteTarget(entry)}>
                        Delete
                      </Btn>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <div className="wl-pagination">
        <span className="wl-muted">Showing {entries.length} of {total}</span>
        <div className="wl-page-btns">
          <Btn size="sm" variant="secondary" disabled={page <= 1} onClick={() => setPage((current) => current - 1)}>
            Prev
          </Btn>
          <span>Page {page} / {totalPages}</span>
          <Btn
            size="sm"
            variant="secondary"
            disabled={page >= totalPages}
            onClick={() => setPage((current) => current + 1)}
          >
            Next
          </Btn>
        </div>
      </div>
    </div>
  );
}

function formatReference(entry: EntryRow) {
  return entry.pl_number || entry.drawing_number || entry.tender_number || '-';
}
