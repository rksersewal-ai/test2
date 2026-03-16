import React, { useEffect, useState } from 'react';
import { bomService } from '../../services/bomService';

interface WhereUsedResult {
  tree_id: number;
  loco_type: string;
  variant: string;
  path: Array<{
    id: number;
    pl_number: string;
    description: string;
    node_type: string;
    quantity: string;
  }>;
}

interface WhereUsedModalProps {
  plNumber: string;
  onClose: () => void;
}

export default function WhereUsedModal({ plNumber, onClose }: WhereUsedModalProps) {
  const [loading, setLoading] = useState(true);
  const [results, setResults] = useState<WhereUsedResult[]>([]);
  const [error, setError] = useState('');

  useEffect(() => {
    bomService.getWhereUsed(plNumber)
      .then(data => {
        setResults(data);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setError('Failed to fetch where-used data.');
        setLoading(false);
      });
  }, [plNumber]);

  return (
    <div style={{
      position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
      background: 'rgba(0,0,0,0.6)', backdropFilter: 'blur(4px)',
      display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 99999
    }}>
      <div style={{
        background: '#1a2035', border: '1px solid #2d3555',
        borderRadius: 8, width: '90%', maxWidth: 800, maxHeight: '85vh',
        display: 'flex', flexDirection: 'column',
        boxShadow: '0 20px 40px rgba(0,0,0,0.5)', overflow: 'hidden'
      }}>
        {/* Header */}
        <div style={{ 
          padding: '16px 20px', borderBottom: '1px solid #2d3555', 
          display: 'flex', justifyContent: 'space-between', alignItems: 'center',
          background: 'linear-gradient(90deg, #1e293b, #0f172a)'
        }}>
          <div>
            <h2 style={{ margin: 0, fontSize: 18, color: '#f8fafc' }}>Where Used Analysis</h2>
            <p style={{ margin: '4px 0 0', fontSize: 13, color: '#94a3b8' }}>
              Impact paths for component: <strong style={{color: '#60a5fa'}}>{plNumber}</strong>
            </p>
          </div>
          <button onClick={onClose} style={{
            background: 'none', border: 'none', color: '#94a3b8', fontSize: 24, cursor: 'pointer', padding: 4
          }}>&times;</button>
        </div>

        {/* Body */}
        <div style={{ padding: 20, overflowY: 'auto', flex: 1 }}>
          {loading ? (
            <div style={{ textAlign: 'center', color: '#94a3b8', padding: 40 }}>Loading impact paths...</div>
          ) : error ? (
            <div style={{ color: '#ef4444', textAlign: 'center', padding: 20 }}>{error}</div>
          ) : results.length === 0 ? (
            <div style={{ textAlign: 'center', color: '#94a3b8', padding: 40 }}>
              This component is not currently used in any active BOM structures.
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
              {results.map((res, idx) => (
                <div key={idx} style={{ 
                  background: '#0f172a', border: '1px solid #334155', borderRadius: 6, padding: 16
                }}>
                  <div style={{ 
                    fontSize: 14, fontWeight: 'bold', color: '#e2e8f0', marginBottom: 12,
                    display: 'flex', gap: 8, alignItems: 'center'
                  }}>
                    <span style={{ fontSize: 16 }}>🚂</span>
                    {res.loco_type} - {res.variant}
                  </div>
                  
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                    {res.path.map((node, i) => (
                      <div key={node.id} style={{ 
                        display: 'flex', alignItems: 'center', gap: 8, 
                        paddingLeft: i * 16, fontSize: 13, color: '#cbd5e1'
                      }}>
                        {i > 0 && <span style={{ color: '#64748b' }}>↳</span>}
                        <span style={{ 
                          background: '#1e293b', border: '1px solid #475569', 
                          padding: '2px 6px', borderRadius: 4, fontFamily: 'monospace', color: '#60a5fa'
                        }}>
                          {node.pl_number}
                        </span>
                        <span style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                          {node.description}
                        </span>
                        <span style={{ marginLeft: 'auto', color: '#94a3b8', fontSize: 11 }}>
                          Qty: {node.quantity}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
