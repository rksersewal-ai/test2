// =============================================================================
// FILE: frontend/src/pages/SDR/SDREditPage.tsx
// =============================================================================
import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import SDRForm from './SDRForm';
import { sdrService } from '../../services/sdrService';
import type { SDRRecord, SDRRecordForm } from '../../types/sdr';

export default function SDREditPage() {
  const navigate   = useNavigate();
  const { id }     = useParams<{ id: string }>();
  const [record, setRecord]   = useState<SDRRecord | null>(null);
  const [loading, setLoading] = useState(true);
  const [error,   setError]   = useState('');

  useEffect(() => {
    if (!id) return;
    sdrService.get(Number(id))
      .then(setRecord)
      .catch(() => setError('Record not found.'))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return <div className="loading">Loading…</div>;
  if (error)   return <div className="alert alert-error">{error}</div>;
  if (!record) return null;

  // Strip read-only fields to get the form-compatible shape
  const initialData: SDRRecordForm = {
    issue_date:          record.issue_date,
    shop_name:           record.shop_name,
    requesting_official: record.requesting_official,
    issuing_official:    record.issuing_official,
    receiving_official:  record.receiving_official,
    remarks:             record.remarks,
    items:               record.items,
  };

  return (
    <div className="page-wrapper">
      <SDRForm
        mode="edit"
        initialData={initialData}
        recordId={record.id}
        sdrNumber={record.sdr_number}
        onSave={()   => navigate('/sdr')}
        onCancel={()  => navigate('/sdr')}
      />
    </div>
  );
}
