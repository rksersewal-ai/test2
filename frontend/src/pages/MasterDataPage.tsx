import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../api/client';
import styles from './MasterDataPage.module.css';

interface LocoModel {
  id: number;
  model_id: string;
  name: string;
  loco_class: string;
  status: string;
  engine_power: string;
  engine_type: string;
  manufacturer: string;
  year_introduced: number | null;
}

interface RecentUpdate {
  id: number;
  action: 'modified' | 'added' | 'deprecated';
  description: string;
  detail: string;
  timestamp: string;
  user_name: string;
}

interface LookupCategory {
  id: number;
  name: string;
  code: string;
  item_count: number;
  items: { id: number; label: string; color: string }[];
}

interface MasterDataSummary {
  loco_type_count: number;
  component_count: number;
  lookup_category_count: number;
  loco_models: LocoModel[];
  recent_updates: RecentUpdate[];
  lookup_categories: LookupCategory[];
}

const STATUS_COLOR: Record<string, string> = {
  Production: '#059669', Testing: '#3b82f6', Concept: '#d97706',
  Legacy: '#6b7280', 'Under Review': '#8b5cf6',
};

const ACTION_ICON: Record<string, string> = {
  modified: '✏️', added: '➕', deprecated: '⚠️',
};

export default function MasterDataPage() {
  const navigate = useNavigate();
  const [selectedCategory, setSelectedCategory] = useState<number | null>(null);
  const [hasUnsaved, setHasUnsaved] = useState(false);

  const { data, isLoading } = useQuery<MasterDataSummary>({
    queryKey: ['master-data-summary'],
    queryFn: () => apiClient.get('/master/summary/').then(r => r.data),
    staleTime: 60_000,
  });

  const selectedCat = data?.lookup_categories.find(c => c.id === selectedCategory)
    ?? data?.lookup_categories[0]
    ?? null;

  const heroCards = [
    {
      key: 'loco', title: 'Locomotive Types', icon: '🚂',
      desc: 'Manage technical specifications, engine classes, and fleet configurations.',
      count: data?.loco_type_count ?? 0, unit: 'Active Types',
      color: '#1e3a5f', onClick: () => navigate('/master/locos'),
    },
    {
      key: 'comp', title: 'Component Catalog', icon: '⚙️',
      desc: 'Define standard parts, supplier variants, and assembly hierarchies.',
      count: data?.component_count ?? 0, unit: 'Items',
      color: '#1e3a5f', onClick: () => navigate('/master/components'),
    },
    {
      key: 'look', title: 'System Lookups', icon: '📊',
      desc: 'Control dropdown values, status codes, and global enumerations.',
      count: data?.lookup_category_count ?? 0, unit: 'Categories',
      color: '#1e3a5f', onClick: () => navigate('/master/lookups'),
    },
  ];

  return (
    <div className={styles.root}>
      <div className={styles.header}>
        <div>
          <h1 className={styles.pageTitle}>Master Data Explorer</h1>
          <p className={styles.pageSub}>Centralized hub for system definitions, vehicle specs, and global lookups.</p>
        </div>
        <div className={styles.headerActions}>
          <button className={styles.auditBtn} onClick={() => navigate('/audit')}>🕐 Audit Log</button>
          <button className={styles.newBtn} onClick={() => navigate('/master/new')}>+ New Definition</button>
        </div>
      </div>

      {/* Hero Cards */}
      <div className={styles.heroGrid}>
        {heroCards.map(card => (
          <div key={card.key} className={styles.heroCard} onClick={card.onClick} role="button" tabIndex={0}>
            <div className={styles.heroCardImg} style={{ background: card.color }}>
              <span className={styles.heroCardIcon}>{card.icon}</span>
              <span className={styles.heroCardTitle}>{card.title}</span>
            </div>
            <div className={styles.heroCardBody}>
              <p className={styles.heroCardDesc}>{card.desc}</p>
              <div className={styles.heroCardFooter}>
                <span className={styles.heroCardCount}>
                  <span className={styles.countDot} />
                  {isLoading ? '…' : card.count.toLocaleString()} {card.unit}
                </span>
                <button className={styles.manageLink} onClick={e => { e.stopPropagation(); card.onClick(); }}>
                  Manage →
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Bottom row */}
      <div className={styles.bottomRow}>
        {/* Recent Updates */}
        <div className={styles.updatesCard}>
          <div className={styles.cardHeader}>
            <span className={styles.cardTitle}>Recent Updates</span>
            <button className={styles.viewAll} onClick={() => navigate('/audit')}>View All</button>
          </div>
          <div className={styles.updatesList}>
            {(data?.recent_updates ?? []).map(upd => (
              <div key={upd.id} className={styles.updateRow}>
                <span className={styles.updateIcon}>{ACTION_ICON[upd.action]}</span>
                <div className={styles.updateBody}>
                  <div className={styles.updateDesc}>{upd.description}</div>
                  <div className={styles.updateDetail}>{upd.detail}</div>
                  <div className={styles.updateMeta}>
                    {new Date(upd.timestamp).toLocaleString('en-IN', { dateStyle: 'short', timeStyle: 'short' })}
                    &nbsp;•&nbsp;{upd.user_name}
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Quick Lookup */}
          <div className={styles.quickLookup}>
            <div className={styles.qlTitle}>Quick Lookup</div>
            <div className={styles.qlLabel}>SELECT CATEGORY</div>
            <select
              className={styles.qlSelect}
              value={selectedCategory ?? ''}
              onChange={e => setSelectedCategory(Number(e.target.value))}
            >
              {(data?.lookup_categories ?? []).map(cat => (
                <option key={cat.id} value={cat.id}>{cat.name}</option>
              ))}
            </select>
            <div className={styles.qlItems}>
              {(selectedCat?.items ?? []).map(item => (
                <div key={item.id} className={styles.qlItem}>
                  <span className={styles.qlDrag}>⋮⋮</span>
                  <span className={styles.qlLabel2}>{item.label}</span>
                  <span className={styles.qlDot} style={{ background: item.color }} />
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Active Loco Models table */}
        <div className={styles.tableCard}>
          <div className={styles.cardHeader}>
            <div>
              <div className={styles.cardTitle}>Active Locomotive Models</div>
              <div className={styles.cardSub}>Quick view of technical specifications.</div>
            </div>
            <div className={styles.tableActions}>
              <button className={styles.iconBtn} title="Filter">≡</button>
              <button className={styles.iconBtn} title="Export">⬇</button>
            </div>
          </div>
          <table className={styles.locoTable}>
            <thead>
              <tr>
                <th>Model ID</th><th>Class</th><th>Status</th>
                <th>Engine Power</th><th>Action</th>
              </tr>
            </thead>
            <tbody>
              {(data?.loco_models ?? []).map(loco => (
                <tr key={loco.id}>
                  <td className={styles.modelId}>{loco.model_id}</td>
                  <td>{loco.loco_class}</td>
                  <td>
                    <span
                      className={styles.statusPill}
                      style={{ background: STATUS_COLOR[loco.status] ?? '#6b7280' }}
                    >{loco.status}</span>
                  </td>
                  <td>{loco.engine_power}</td>
                  <td>
                    <button
                      className={styles.actionLink}
                      onClick={() => navigate(`/master/locos/${loco.id}`)}
                    >View →</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <button className={styles.viewAllModels} onClick={() => navigate('/master/locos')}>
            View All {data?.loco_type_count ?? ''} Models
          </button>
        </div>
      </div>

      {/* Unsaved changes bar */}
      {hasUnsaved && (
        <div className={styles.unsavedBar}>
          <span>⚠️ {3} unsaved changes</span>
          <button className={styles.discardBtn} onClick={() => setHasUnsaved(false)}>Discard</button>
          <button className={styles.saveBtn} onClick={() => setHasUnsaved(false)}>Save Changes</button>
        </div>
      )}
    </div>
  );
}
