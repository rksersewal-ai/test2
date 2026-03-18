import { useNavigate } from 'react-router-dom';
import styles from './MasterDataPage.module.css';

interface HubCard {
  key: string;
  title: string;
  badge: string;
  desc: string;
  unit: string;
  color: string;
  to: string;
}

interface HubAction {
  id: string;
  title: string;
  detail: string;
  to: string;
}

interface RouteRow {
  key: string;
  title: string;
  to: string;
  detail: string;
}

const HERO_CARDS: HubCard[] = [
  {
    key: 'pl-master',
    title: 'PL Master',
    badge: 'PL',
    desc: 'Manage parts, drawings, specifications, and linked engineering definitions.',
    unit: 'Parts, drawings, and specs',
    color: '#1e3a5f',
    to: '/pl-master',
  },
  {
    key: 'bom',
    title: 'BOM Structure',
    badge: 'BOM',
    desc: 'Open the interactive structure editor to review and reorganize assemblies.',
    unit: 'Assembly hierarchy editor',
    color: '#184b63',
    to: '/bom',
  },
  {
    key: 'config',
    title: 'Configuration Control',
    badge: 'CFG',
    desc: 'Track locomotive configurations and ECN records in the active engineering module.',
    unit: 'Configs and ECNs',
    color: '#32516d',
    to: '/config',
  },
];

const OPERATIONS: HubAction[] = [
  {
    id: 'pl-workbench',
    title: 'Open PL workbench',
    detail: 'Review PL records, linked specs, drawings, and BOM relationships.',
    to: '/pl-master',
  },
  {
    id: 'bom-workbench',
    title: 'Edit product structure',
    detail: 'Inspect and reorganize assemblies using the live BOM editor.',
    to: '/bom',
  },
  {
    id: 'config-control',
    title: 'Review ECN activity',
    detail: 'Approve, reject, and audit live configuration-change items.',
    to: '/config',
  },
  {
    id: 'work-ledger',
    title: 'Track engineering effort',
    detail: 'Use Work Ledger for section activity, reports, and verification flow.',
    to: '/work-ledger',
  },
];

const QUICK_LINKS: HubAction[] = [
  {
    id: 'settings',
    title: 'Application settings',
    detail: 'Save operator defaults, OCR preferences, and export behavior.',
    to: '/settings',
  },
  {
    id: 'audit',
    title: 'Audit trail',
    detail: 'Inspect system changes and user actions across engineering modules.',
    to: '/audit',
  },
  {
    id: 'documents',
    title: 'Document register',
    detail: 'Browse controlled drawings, manuals, specifications, and revisions.',
    to: '/documents',
  },
  {
    id: 'search',
    title: 'Global search',
    detail: 'Search document metadata and OCR content from one place.',
    to: '/search',
  },
];

const ROUTE_ROWS: RouteRow[] = [
  ...HERO_CARDS.map((card) => ({
    key: card.key,
    title: card.title,
    to: card.to,
    detail: card.desc,
  })),
  ...QUICK_LINKS.map((item) => ({
    key: item.id,
    title: item.title,
    to: item.to,
    detail: item.detail,
  })),
];

export default function MasterDataPage() {
  const navigate = useNavigate();

  return (
    <div className={styles.root}>
      <div className={styles.header}>
        <div>
          <h1 className={styles.pageTitle}>Engineering Master Data</h1>
          <p className={styles.pageSub}>
            Use this hub to reach the live master-data modules that are wired in the current application.
          </p>
        </div>
        <div className={styles.headerActions}>
          <button className={styles.auditBtn} onClick={() => navigate('/audit')}>Audit Log</button>
          <button className={styles.newBtn} onClick={() => navigate('/pl-master/new')}>New PL Item</button>
        </div>
      </div>

      <div className={styles.heroGrid}>
        {HERO_CARDS.map(card => (
          <div
            key={card.key}
            className={styles.heroCard}
            onClick={() => navigate(card.to)}
            role="button"
            tabIndex={0}
          >
            <div className={styles.heroCardImg} style={{ background: card.color }}>
              <span className={styles.heroCardIcon}>{card.badge}</span>
              <span className={styles.heroCardTitle}>{card.title}</span>
            </div>
            <div className={styles.heroCardBody}>
              <p className={styles.heroCardDesc}>{card.desc}</p>
              <div className={styles.heroCardFooter}>
                <span className={styles.heroCardCount}>
                  <span className={styles.countDot} />
                  {card.unit}
                </span>
                <button
                  className={styles.manageLink}
                  onClick={(event) => {
                    event.stopPropagation();
                    navigate(card.to);
                  }}
                >
                  Open
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className={styles.bottomRow}>
        <div className={styles.updatesCard}>
          <div className={styles.cardHeader}>
            <span className={styles.cardTitle}>Available Workspaces</span>
            <button className={styles.viewAll} onClick={() => navigate('/search')}>Search</button>
          </div>
          <div className={styles.updatesList}>
            {OPERATIONS.map(item => (
              <div key={item.id} className={styles.updateRow}>
                <span className={styles.updateIcon}>{item.title.slice(0, 2).toUpperCase()}</span>
                <div className={styles.updateBody}>
                  <div className={styles.updateDesc}>{item.title}</div>
                  <div className={styles.updateDetail}>{item.detail}</div>
                  <div className={styles.updateMeta}>
                    Active route: {item.to}
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className={styles.quickLookup}>
            <div className={styles.qlTitle}>Quick Access</div>
            <div className={styles.qlLabel}>LIVE MODULES</div>
            <div className={styles.qlItems}>
              {QUICK_LINKS.map(item => (
                <button
                  key={item.id}
                  className={styles.qlItem}
                  onClick={() => navigate(item.to)}
                  type="button"
                >
                  <span className={styles.qlLabel2}>{item.title}</span>
                  <span className={styles.qlDot} />
                </button>
              ))}
            </div>
          </div>
        </div>

        <div className={styles.tableCard}>
          <div className={styles.cardHeader}>
            <div>
              <div className={styles.cardTitle}>Route Map</div>
              <div className={styles.cardSub}>All actions below point to routes that exist in the current app shell.</div>
            </div>
          </div>
          <table className={styles.locoTable}>
            <thead>
              <tr>
                <th>Module</th>
                <th>Route</th>
                <th>Purpose</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {ROUTE_ROWS.map((item) => (
                <tr key={item.key}>
                  <td className={styles.modelId}>{item.title}</td>
                  <td>{item.to}</td>
                  <td>{item.detail}</td>
                  <td>
                    <button
                      className={styles.actionLink}
                      onClick={() => navigate(item.to)}
                      type="button"
                    >
                      Open
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <button className={styles.viewAllModels} onClick={() => navigate('/pl-master')}>
            Go to PL Master
          </button>
        </div>
      </div>
    </div>
  );
}
