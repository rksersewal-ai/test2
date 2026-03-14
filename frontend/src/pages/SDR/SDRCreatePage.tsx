// =============================================================================
// FILE: frontend/src/pages/SDR/SDRCreatePage.tsx
// =============================================================================
import React from 'react';
import { useNavigate } from 'react-router-dom';
import SDRForm from './SDRForm';

export default function SDRCreatePage() {
  const navigate = useNavigate();
  return (
    <div className="page-wrapper">
      <SDRForm
        mode="create"
        onSave={()   => navigate('/sdr')}
        onCancel={()  => navigate('/sdr')}
      />
    </div>
  );
}
