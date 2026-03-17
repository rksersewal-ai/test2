import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Btn, PageHeader, Toast } from '../../components/common';
import type { ToastMsg } from '../../components/common';
import { plMasterService } from '../../services/plMasterService';

function cardStyle(): React.CSSProperties {
  return {
    background: '#151b2e',
    border: '1px solid #2d3555',
    borderRadius: 12,
    padding: 18,
  };
}

export default function PLDetailPage() {
  const { plNumber } = useParams<{ plNumber: string }>();
  const navigate = useNavigate();
  const [plItem, setPlItem] = useState<any>(null);
  const [bomTree, setBomTree] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [toast, setToast] = useState<ToastMsg | null>(null);

  useEffect(() => {
    if (!plNumber) return;

    let cancelled = false;
    Promise.all([
      plMasterService.getPL(plNumber),
      plMasterService.getBOMTree(plNumber).catch(() => ({ children: [] })),
    ])
      .then(([detail, bom]) => {
        if (cancelled) return;
        setPlItem(detail);
        setBomTree(bom.children ?? []);
      })
      .catch(() => {
        if (!cancelled) {
          setToast({ type: 'error', text: 'PL item not found.' });
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [plNumber]);

  if (loading) {
    return <div style={{ padding: 24, color: '#94a3b8' }}>Loading PL details...</div>;
  }

  if (!plItem) {
    return (
      <div style={{ padding: 24 }}>
        <Btn size="sm" variant="secondary" onClick={() => navigate('/pl-master')}>Back</Btn>
      </div>
    );
  }

  return (
    <div style={{ padding: 24 }}>
      <PageHeader title={plItem.pl_number} subtitle={plItem.description ?? plItem.part_description ?? 'PL detail'}>
        <Btn size="sm" variant="secondary" onClick={() => navigate('/pl-master')}>Back</Btn>
        <Btn size="sm" onClick={() => navigate(`/pl-master/${plItem.pl_number}/edit`)}>Edit</Btn>
      </PageHeader>

      <Toast msg={toast} onClose={() => setToast(null)} />

      <div style={{ display: 'grid', gridTemplateColumns: '1.4fr 1fr', gap: 20, alignItems: 'start' }}>
        <div style={{ display: 'grid', gap: 20 }}>
          <section style={cardStyle()}>
            <h3 style={{ marginTop: 0, color: '#e2e8f0' }}>PL Information</h3>
            <DetailGrid
              rows={[
                ['PL Number', plItem.pl_number],
                ['Description', plItem.description ?? plItem.part_description ?? '-'],
                ['Inspection Category', plItem.inspection_category ?? '-'],
                ['Safety Item', plItem.safety_item ? 'Yes' : 'No'],
                ['UVAM ID', plItem.uvam_id ?? '-'],
                ['Application Area', plItem.application_area ?? '-'],
                ['Agency', plItem.controlling_agency_name ?? plItem.controlling_agency_code ?? '-'],
                ['Loco Types', (plItem.loco_types ?? plItem.used_in ?? []).join(', ') || '-'],
                ['Version', String(plItem.version ?? '-')],
                ['Keywords', (plItem.keywords ?? []).join(', ') || '-'],
                ['Remarks', plItem.remarks ?? '-'],
              ]}
            />
          </section>

          <section style={cardStyle()}>
            <h3 style={{ marginTop: 0, color: '#e2e8f0' }}>BOM Structure</h3>
            {bomTree.length === 0 ? (
              <div style={{ color: '#94a3b8' }}>No BOM children linked.</div>
            ) : (
              <BomList items={bomTree} depth={0} />
            )}
          </section>
        </div>

        <div style={{ display: 'grid', gap: 20 }}>
          <section style={cardStyle()}>
            <h3 style={{ marginTop: 0, color: '#e2e8f0' }}>Linked Drawings</h3>
            <LinkTable
              emptyText="No linked drawings."
              rows={(plItem.drawing_links ?? []).map((item: any) => [
                item.drawing_number,
                item.drawing_title,
                item.current_alteration ?? '-',
              ])}
            />
          </section>

          <section style={cardStyle()}>
            <h3 style={{ marginTop: 0, color: '#e2e8f0' }}>Linked Specifications</h3>
            <LinkTable
              emptyText="No linked specifications."
              rows={(plItem.spec_links ?? []).map((item: any) => [
                item.spec_number,
                item.spec_title,
                item.current_alteration ?? '-',
              ])}
            />
          </section>

          <section style={cardStyle()}>
            <h3 style={{ marginTop: 0, color: '#e2e8f0' }}>Standards and SMI</h3>
            <LinkTable
              emptyText="No linked standards or SMI records."
              rows={[
                ...(plItem.standard_links ?? []).map((item: any) => [
                  item.rdso_doc_number,
                  item.rdso_doc_title,
                  item.rdso_doc_type ?? '-',
                ]),
                ...(plItem.smi_links ?? []).map((item: any) => [
                  item.smi_number,
                  item.smi_title,
                  item.implementation_status ?? '-',
                ]),
              ]}
            />
          </section>

          <section style={cardStyle()}>
            <h3 style={{ marginTop: 0, color: '#e2e8f0' }}>Alternates and Applicability</h3>
            <LinkTable
              emptyText="No alternates or loco applicability records."
              rows={[
                ...(plItem.alternates ?? []).map((item: any) => [
                  item.alternate_pl_number,
                  item.alternate_description,
                  item.interchangeable ? 'Interchangeable' : '-',
                ]),
                ...(plItem.loco_applicabilities ?? []).map((item: any) => [
                  item.loco_type,
                  item.assembly_group ?? '-',
                  item.qty_per_loco ?? '-',
                ]),
              ]}
            />
          </section>
        </div>
      </div>
    </div>
  );
}

function DetailGrid({ rows }: { rows: Array<[string, string]> }) {
  return (
    <div style={{ display: 'grid', gap: 10 }}>
      {rows.map(([label, value]) => (
        <div key={label} style={{ display: 'grid', gridTemplateColumns: '160px 1fr', gap: 12 }}>
          <div style={{ color: '#94a3b8', fontSize: 12, fontWeight: 600 }}>{label}</div>
          <div style={{ color: '#d1d5db', fontSize: 13 }}>{value}</div>
        </div>
      ))}
    </div>
  );
}

function LinkTable({ rows, emptyText }: { rows: string[][]; emptyText: string }) {
  if (rows.length === 0) {
    return <div style={{ color: '#94a3b8' }}>{emptyText}</div>;
  }

  return (
    <div style={{ display: 'grid', gap: 10 }}>
      {rows.map((row, index) => (
        <div key={index} style={{ border: '1px solid #2d3555', borderRadius: 8, padding: 12 }}>
          <div style={{ color: '#e2e8f0', fontWeight: 600 }}>{row[0] || '-'}</div>
          <div style={{ color: '#94a3b8', fontSize: 12, marginTop: 4 }}>{row[1] || '-'}</div>
          <div style={{ color: '#60a5fa', fontSize: 12, marginTop: 6 }}>{row[2] || '-'}</div>
        </div>
      ))}
    </div>
  );
}

function BomList({ items, depth }: { items: any[]; depth: number }) {
  return (
    <div style={{ display: 'grid', gap: 10 }}>
      {items.map(item => (
        <div key={`${item.pl_number}-${depth}`} style={{ marginLeft: depth * 16 }}>
          <div style={{ color: '#e2e8f0', fontWeight: 600 }}>{item.pl_number ?? '-'}</div>
          <div style={{ color: '#94a3b8', fontSize: 12 }}>{item.part_description ?? item.description ?? '-'}</div>
          {Array.isArray(item.children) && item.children.length > 0 && (
            <BomList items={item.children} depth={depth + 1} />
          )}
        </div>
      ))}
    </div>
  );
}
