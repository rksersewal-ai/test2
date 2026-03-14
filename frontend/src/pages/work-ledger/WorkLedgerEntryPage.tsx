// =============================================================================
// FILE: frontend/src/pages/work-ledger/WorkLedgerEntryPage.tsx
// PURPOSE: Create / Edit a Work Ledger entry
// =============================================================================
import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { WorkLedgerForm } from '../../components/work-ledger/WorkLedgerForm';
import { workLedgerApi } from '../../services/workLedgerApi';
import type { WorkLedgerFormData, WorkLedgerFull } from '../../types/workLedger';

export const WorkLedgerEntryPage: React.FC = () => {
  const { workId } = useParams<{ workId?: string }>(); // present when editing
  const navigate = useNavigate();
  const [existing, setExisting] = useState<WorkLedgerFull | null>(null);
  const [loading, setLoading] = useState(!!workId);
  const [saved, setSaved] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  useEffect(() => {
    if (workId) {
      workLedgerApi
        .getEntry(Number(workId))
        .then(setExisting)
        .catch(() => setErrorMsg('Failed to load entry.'))
        .finally(() => setLoading(false));
    }
  }, [workId]);

  const handleSubmit = async (data: WorkLedgerFormData) => {
    try {
      setErrorMsg('');
      if (workId) {
        await workLedgerApi.updateEntry(Number(workId), data);
      } else {
        await workLedgerApi.createEntry(data);
      }
      setSaved(true);
      setTimeout(() => navigate('/work-ledger'), 800);
    } catch (err: any) {
      setErrorMsg(err.message ?? 'Save failed.');
    }
  };

  if (loading) return <p className="wl-loading">Loading entry...</p>;

  return (
    <div className="wl-entry-page">
      {saved && <div className="wl-alert wl-alert--success">Saved successfully. Redirecting...</div>}
      {errorMsg && <div className="wl-alert wl-alert--error">{errorMsg}</div>}
      <WorkLedgerForm
        initialData={existing ?? undefined}
        onSubmit={handleSubmit}
        submitLabel={workId ? 'Update Entry' : 'Save Entry'}
      />
    </div>
  );
};
