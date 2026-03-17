import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import type { DragEvent, MouseEvent as ReactMouseEvent, WheelEvent as ReactWheelEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { Btn, PageHeader, SearchBar, Toast } from '../components/common';
import type { ToastMsg } from '../components/common';
import { useAuth } from '../hooks/useAuth';
import { plMasterService } from '../services/plMasterService';
import './BOMPage.css';

type BOMTab = 'editor' | 'catalog';

interface ApiBomNode {
  pl_number: string;
  part_description?: string;
  inspection_category?: string;
  children?: ApiBomNode[];
}

interface BomTreePayload {
  pl_number: string;
  children?: ApiBomNode[];
}

interface PLDetail {
  pl_number: string;
  part_description?: string;
  inspection_category?: string;
  safety_item?: boolean;
  application_area?: string;
  used_in?: string[];
  mother_part?: string | null;
  mother_part_description?: string;
  controlling_agency_code?: string;
  remarks?: string;
}

interface StructureNode {
  id: string;
  plNumber: string;
  description: string;
  inspectionCategory: string;
  safetyItem: boolean;
  applicationArea: string;
  usedIn: string[];
  parentId: string | null;
  level: number;
  children: StructureNode[];
}

interface LayoutPoint {
  x: number;
  y: number;
}

interface LayoutEdge {
  sourceId: string;
  targetId: string;
}

interface LayoutResult {
  positions: Record<string, LayoutPoint>;
  edges: LayoutEdge[];
  visibleIds: string[];
  contentWidth: number;
  contentHeight: number;
}

interface CatalogTabProps {
  onLoadAsRoot: (plNumber: string) => void;
  onOpenPL: (plNumber: string) => void;
}

const CARD_WIDTH = 264;
const CARD_HEIGHT = 136;
const HORIZONTAL_GAP = 120;
const VERTICAL_GAP = 44;
const MIN_ZOOM = 0.45;
const MAX_ZOOM = 1.65;
const CATALOG_PAGE_SIZE = 25;
const ENGINEERING_ROLES = new Set(['ADMIN', 'SECTION_HEAD', 'ENGINEER', 'LDO_STAFF']);

function clamp(value: number, min: number, max: number) {
  return Math.min(Math.max(value, min), max);
}

function normalizeNode(node: ApiBomNode, parentId: string | null, level: number): StructureNode {
  const children = (node.children ?? []).map((child) => normalizeNode(child, node.pl_number, level + 1));
  return {
    id: node.pl_number,
    plNumber: node.pl_number,
    description: node.part_description ?? '',
    inspectionCategory: node.inspection_category ?? '',
    safetyItem: false,
    applicationArea: '',
    usedIn: [],
    parentId,
    level,
    children,
  };
}

function buildStructureTree(rootPlNumber: string, payload: BomTreePayload, detail: PLDetail | null): StructureNode {
  const root: StructureNode = {
    id: payload.pl_number || rootPlNumber,
    plNumber: payload.pl_number || rootPlNumber,
    description: detail?.part_description ?? 'Root assembly',
    inspectionCategory: detail?.inspection_category ?? '',
    safetyItem: Boolean(detail?.safety_item),
    applicationArea: detail?.application_area ?? '',
    usedIn: detail?.used_in ?? [],
    parentId: null,
    level: 0,
    children: (payload.children ?? []).map((child) => normalizeNode(child, payload.pl_number || rootPlNumber, 1)),
  };
  return updateLevels(root, null, 0);
}

function updateLevels(node: StructureNode, parentId: string | null, level: number): StructureNode {
  return {
    ...node,
    parentId,
    level,
    children: node.children.map((child) => updateLevels(child, node.id, level + 1)),
  };
}

function indexNodes(node: StructureNode): Record<string, StructureNode> {
  const result: Record<string, StructureNode> = {};
  const visit = (current: StructureNode) => {
    result[current.id] = current;
    current.children.forEach(visit);
  };
  visit(node);
  return result;
}

function findNode(node: StructureNode, id: string): StructureNode | null {
  if (node.id === id) {
    return node;
  }
  for (const child of node.children) {
    const found = findNode(child, id);
    if (found) {
      return found;
    }
  }
  return null;
}

function findPath(node: StructureNode, id: string): StructureNode[] {
  if (node.id === id) {
    return [node];
  }
  for (const child of node.children) {
    const childPath = findPath(child, id);
    if (childPath.length > 0) {
      return [node, ...childPath];
    }
  }
  return [];
}

function countNodes(node: StructureNode): number {
  return 1 + node.children.reduce((total, child) => total + countNodes(child), 0);
}

function countVisibleNodes(node: StructureNode, expandedIds: Set<string>): number {
  if (!expandedIds.has(node.id)) {
    return 1;
  }
  return 1 + node.children.reduce((total, child) => total + countVisibleNodes(child, expandedIds), 0);
}

function countLeafNodes(node: StructureNode): number {
  if (node.children.length === 0) {
    return 1;
  }
  return node.children.reduce((total, child) => total + countLeafNodes(child), 0);
}

function getTreeDepth(node: StructureNode): number {
  if (node.children.length === 0) {
    return node.level;
  }
  return Math.max(...node.children.map(getTreeDepth));
}

function getDefaultExpandedIds(node: StructureNode, depthLimit = 1): Set<string> {
  const expanded = new Set<string>();
  const visit = (current: StructureNode) => {
    if (current.level <= depthLimit && current.children.length > 0) {
      expanded.add(current.id);
      current.children.forEach(visit);
    }
  };
  visit(node);
  return expanded;
}

function getExpandableIds(node: StructureNode): Set<string> {
  const expanded = new Set<string>();
  const visit = (current: StructureNode) => {
    if (current.children.length > 0) {
      expanded.add(current.id);
      current.children.forEach(visit);
    }
  };
  visit(node);
  return expanded;
}

function branchMatches(node: StructureNode, query: string): boolean {
  if (!query) {
    return true;
  }
  const haystack = `${node.plNumber} ${node.description} ${node.inspectionCategory}`.toLowerCase();
  if (haystack.includes(query)) {
    return true;
  }
  return node.children.some((child) => branchMatches(child, query));
}

function isMatch(node: StructureNode, query: string): boolean {
  if (!query) {
    return false;
  }
  const haystack = `${node.plNumber} ${node.description} ${node.inspectionCategory}`.toLowerCase();
  return haystack.includes(query);
}

function removeNode(root: StructureNode, sourceId: string): { root: StructureNode; removed: StructureNode | null } {
  let removed: StructureNode | null = null;
  const visit = (node: StructureNode): StructureNode => {
    const nextChildren: StructureNode[] = [];
    node.children.forEach((child) => {
      if (child.id === sourceId) {
        removed = child;
        return;
      }
      nextChildren.push(visit(child));
    });
    return { ...node, children: nextChildren };
  };
  return { root: visit(root), removed };
}

function insertNode(root: StructureNode, targetId: string, nodeToInsert: StructureNode): StructureNode {
  if (root.id === targetId) {
    return { ...root, children: [...root.children, nodeToInsert] };
  }
  return {
    ...root,
    children: root.children.map((child) => insertNode(child, targetId, nodeToInsert)),
  };
}

function moveNodeInTree(root: StructureNode, sourceId: string, targetId: string): StructureNode | null {
  if (sourceId === root.id) {
    return null;
  }

  const sourceNode = findNode(root, sourceId);
  if (!sourceNode) {
    return null;
  }

  if (sourceId === targetId || findNode(sourceNode, targetId)) {
    return null;
  }

  const { root: withoutSource, removed } = removeNode(root, sourceId);
  if (!removed) {
    return null;
  }

  const inserted = insertNode(withoutSource, targetId, removed);
  return updateLevels(inserted, null, 0);
}

function computeLayout(root: StructureNode, expandedIds: Set<string>): LayoutResult {
  const positions: Record<string, LayoutPoint> = {};
  const edges: LayoutEdge[] = [];
  const visibleIds: string[] = [];
  let maxX = CARD_WIDTH;
  let maxY = CARD_HEIGHT;

  const visit = (node: StructureNode, depth: number, cursor: number): { nextCursor: number; centerY: number } => {
    visibleIds.push(node.id);
    const x = depth * (CARD_WIDTH + HORIZONTAL_GAP);
    const isExpanded = expandedIds.has(node.id);
    const visibleChildren = isExpanded ? node.children : [];

    if (visibleChildren.length === 0) {
      const y = cursor * (CARD_HEIGHT + VERTICAL_GAP);
      positions[node.id] = { x, y };
      maxX = Math.max(maxX, x + CARD_WIDTH);
      maxY = Math.max(maxY, y + CARD_HEIGHT);
      return { nextCursor: cursor + 1, centerY: y + CARD_HEIGHT / 2 };
    }

    let nextCursor = cursor;
    const childCenters: number[] = [];
    visibleChildren.forEach((child) => {
      const childLayout = visit(child, depth + 1, nextCursor);
      edges.push({ sourceId: node.id, targetId: child.id });
      nextCursor = childLayout.nextCursor;
      childCenters.push(childLayout.centerY);
    });

    const top = childCenters[0] - CARD_HEIGHT / 2;
    const bottom = childCenters[childCenters.length - 1] - CARD_HEIGHT / 2;
    const y = top + (bottom - top) / 2;

    positions[node.id] = { x, y };
    maxX = Math.max(maxX, x + CARD_WIDTH);
    maxY = Math.max(maxY, y + CARD_HEIGHT);

    return { nextCursor, centerY: y + CARD_HEIGHT / 2 };
  };

  visit(root, 0, 0);

  return {
    positions,
    edges,
    visibleIds,
    contentWidth: maxX + 120,
    contentHeight: maxY + 120,
  };
}

function CatalogTab({ onLoadAsRoot, onOpenPL }: CatalogTabProps) {
  const [items, setItems] = useState<PLDetail[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [inspectionCategory, setInspectionCategory] = useState('');
  const [safetyItem, setSafetyItem] = useState('');
  const [loading, setLoading] = useState(false);
  const [toast, setToast] = useState<ToastMsg | null>(null);

  const loadCatalog = useCallback(async () => {
    setLoading(true);
    try {
      const params: Record<string, string> = {
        page: String(page),
        page_size: String(CATALOG_PAGE_SIZE),
      };

      if (search.trim()) {
        params.q = search.trim();
      }
      if (inspectionCategory) {
        params.inspection_category = inspectionCategory;
      }
      if (safetyItem) {
        params.safety_item = safetyItem;
      }

      const response = await plMasterService.listPL(params);
      setItems(response.results ?? []);
      setTotal(response.total_count ?? 0);
    } catch {
      setToast({ type: 'error', text: 'Failed to load the PL catalog.' });
    } finally {
      setLoading(false);
    }
  }, [inspectionCategory, page, safetyItem, search]);

  useEffect(() => {
    void loadCatalog();
  }, [loadCatalog]);

  const totalPages = Math.max(1, Math.ceil(total / CATALOG_PAGE_SIZE));

  return (
    <div className="bom-catalog">
      <Toast msg={toast} onClose={() => setToast(null)} />

      <div className="bom-toolbar bom-toolbar--catalog">
        <SearchBar
          value={search}
          onChange={(value) => {
            setSearch(value);
            setPage(1);
          }}
          placeholder="Search PL, description, UVAM..."
          width={300}
        />

        <select
          className="bom-select"
          value={inspectionCategory}
          onChange={(event) => {
            setInspectionCategory(event.target.value);
            setPage(1);
          }}
        >
          <option value="">All categories</option>
          <option value="CAT-A">CAT-A</option>
          <option value="CAT-B">CAT-B</option>
          <option value="CAT-C">CAT-C</option>
          <option value="CAT-D">CAT-D</option>
        </select>

        <select
          className="bom-select"
          value={safetyItem}
          onChange={(event) => {
            setSafetyItem(event.target.value);
            setPage(1);
          }}
        >
          <option value="">Safety: all</option>
          <option value="true">Safety items</option>
          <option value="false">Non-safety</option>
        </select>

        <Btn size="sm" variant="ghost" onClick={() => void loadCatalog()} loading={loading}>
          Refresh
        </Btn>
      </div>

      <div className="bom-tableWrap">
        <table className="bom-table">
          <thead>
            <tr>
              <th>PL Number</th>
              <th>Description</th>
              <th>Category</th>
              <th>Safety</th>
              <th>Used In</th>
              <th>Application</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {loading && (
              <tr>
                <td colSpan={7} className="bom-tableEmpty">Loading catalog...</td>
              </tr>
            )}

            {!loading && items.length === 0 && (
              <tr>
                <td colSpan={7} className="bom-tableEmpty">No PL items found.</td>
              </tr>
            )}

            {!loading && items.map((item) => (
              <tr key={item.pl_number}>
                <td>
                  <strong className="bom-mono">{item.pl_number}</strong>
                </td>
                <td className="bom-tableDescription">{item.part_description ?? '-'}</td>
                <td>
                  {item.inspection_category ? (
                    <span className="bom-chip bom-chip--category">{item.inspection_category}</span>
                  ) : '-'}
                </td>
                <td>{item.safety_item ? 'Yes' : 'No'}</td>
                <td className="bom-tableMuted">{(item.used_in ?? []).join(', ') || '-'}</td>
                <td className="bom-tableMuted">{item.application_area || '-'}</td>
                <td>
                  <div className="bom-tableActions">
                    <Btn size="sm" variant="secondary" onClick={() => onLoadAsRoot(item.pl_number)}>
                      Load
                    </Btn>
                    <Btn size="sm" variant="ghost" onClick={() => onOpenPL(item.pl_number)}>
                      Open PL
                    </Btn>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="bom-pagination">
        <span className="bom-tableMuted">{total} PL items</span>
        <div className="bom-paginationControls">
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

export default function BOMPage() {
  const navigate = useNavigate();
  const { user } = useAuth();

  const canEditStructure = Boolean(user?.is_staff || ENGINEERING_ROLES.has(String(user?.role ?? '').toUpperCase()));

  const [tab, setTab] = useState<BOMTab>('editor');
  const [rootQuery, setRootQuery] = useState('');
  const [loadedRoot, setLoadedRoot] = useState('');
  const [maxDepth, setMaxDepth] = useState(5);
  const [structure, setStructure] = useState<StructureNode | null>(null);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [selectedDetail, setSelectedDetail] = useState<PLDetail | null>(null);
  const [loadingStructure, setLoadingStructure] = useState(false);
  const [loadingDetail, setLoadingDetail] = useState(false);
  const [toast, setToast] = useState<ToastMsg | null>(null);
  const [expandedIds, setExpandedIds] = useState<Set<string>>(new Set());
  const [navigatorQuery, setNavigatorQuery] = useState('');
  const [viewport, setViewport] = useState({ x: 72, y: 72, scale: 1 });
  const [isPanning, setIsPanning] = useState(false);
  const [pendingAutoFit, setPendingAutoFit] = useState(false);
  const [draggedId, setDraggedId] = useState<string | null>(null);
  const [dropTargetId, setDropTargetId] = useState<string | null>(null);
  const [movingId, setMovingId] = useState<string | null>(null);

  const canvasViewportRef = useRef<HTMLDivElement | null>(null);
  const panSessionRef = useRef<{ startX: number; startY: number; originX: number; originY: number } | null>(null);

  const nodeIndex = useMemo(() => (structure ? indexNodes(structure) : {}), [structure]);
  const selectedNode = selectedId ? nodeIndex[selectedId] ?? null : null;
  const selectedPath = useMemo(() => {
    if (!structure || !selectedId) {
      return [];
    }
    return findPath(structure, selectedId);
  }, [selectedId, structure]);
  const selectedPathIds = useMemo(() => new Set(selectedPath.map((node) => node.id)), [selectedPath]);
  const layout = useMemo(
    () => (structure ? computeLayout(structure, expandedIds) : { positions: {}, edges: [], visibleIds: [], contentWidth: 1, contentHeight: 1 }),
    [expandedIds, structure],
  );
  const normalizedNavigatorQuery = navigatorQuery.trim().toLowerCase();

  const metrics = useMemo(() => {
    if (!structure) {
      return null;
    }
    return {
      totalNodes: countNodes(structure),
      visibleNodes: countVisibleNodes(structure, expandedIds),
      leafNodes: countLeafNodes(structure),
      depth: getTreeDepth(structure) + 1,
    };
  }, [expandedIds, structure]);

  const fitCanvas = useCallback(() => {
    if (!canvasViewportRef.current || !structure) {
      return;
    }

    const padding = 80;
    const usableWidth = Math.max(1, canvasViewportRef.current.clientWidth - padding * 2);
    const usableHeight = Math.max(1, canvasViewportRef.current.clientHeight - padding * 2);
    const nextScale = clamp(
      Math.min(usableWidth / layout.contentWidth, usableHeight / layout.contentHeight, 1),
      MIN_ZOOM,
      MAX_ZOOM,
    );

    setViewport({
      scale: nextScale,
      x: padding + (usableWidth - layout.contentWidth * nextScale) / 2,
      y: padding + (usableHeight - layout.contentHeight * nextScale) / 2,
    });
  }, [layout.contentHeight, layout.contentWidth, structure]);

  const focusNode = useCallback((nodeId: string) => {
    const point = layout.positions[nodeId];
    if (!point || !canvasViewportRef.current) {
      return;
    }

    setViewport((current) => ({
      ...current,
      x: canvasViewportRef.current!.clientWidth / 2 - (point.x + CARD_WIDTH / 2) * current.scale,
      y: canvasViewportRef.current!.clientHeight / 2 - (point.y + CARD_HEIGHT / 2) * current.scale,
    }));
  }, [layout.positions]);

  const ensurePathExpanded = useCallback((nodeId: string) => {
    if (!structure) {
      return;
    }
    const path = findPath(structure, nodeId);
    setExpandedIds((current) => {
      const next = new Set(current);
      path.slice(0, -1).forEach((node) => {
        if (node.children.length > 0) {
          next.add(node.id);
        }
      });
      return next;
    });
  }, [structure]);

  const loadStructure = useCallback(async (nextRoot?: string) => {
    const requestedRoot = (nextRoot ?? rootQuery).trim();
    if (!requestedRoot) {
      setToast({ type: 'warning', text: 'Enter a PL number to load the structure.' });
      return;
    }

    setLoadingStructure(true);
    try {
      const [treePayload, detail] = await Promise.all([
        plMasterService.getBOMTree(requestedRoot, maxDepth) as Promise<BomTreePayload>,
        plMasterService.getPL(requestedRoot).catch(() => null) as Promise<PLDetail | null>,
      ]);

      const nextStructure = buildStructureTree(requestedRoot, treePayload, detail);
      setStructure(nextStructure);
      setLoadedRoot(requestedRoot);
      setRootQuery(requestedRoot);
      setSelectedId(nextStructure.id);
      setSelectedDetail(detail);
      setExpandedIds(getDefaultExpandedIds(nextStructure, 1));
      setNavigatorQuery('');
      setPendingAutoFit(true);
      setTab('editor');
    } catch {
      setToast({ type: 'error', text: `Unable to load the BOM for ${requestedRoot}.` });
    } finally {
      setLoadingStructure(false);
    }
  }, [maxDepth, rootQuery]);

  useEffect(() => {
    if (!selectedId || !structure) {
      setSelectedDetail(null);
      return;
    }

    let active = true;
    setLoadingDetail(true);
    plMasterService.getPL(selectedId)
      .then((detail) => {
        if (active) {
          setSelectedDetail(detail);
        }
      })
      .catch(() => {
        if (active) {
          setSelectedDetail(null);
        }
      })
      .finally(() => {
        if (active) {
          setLoadingDetail(false);
        }
      });

    return () => {
      active = false;
    };
  }, [selectedId, structure]);

  useEffect(() => {
    if (pendingAutoFit && structure) {
      fitCanvas();
      setPendingAutoFit(false);
    }
  }, [fitCanvas, pendingAutoFit, structure]);

  useEffect(() => {
    const handleMouseMove = (event: MouseEvent) => {
      if (!panSessionRef.current) {
        return;
      }
      const session = panSessionRef.current;
      setViewport((current) => ({
        ...current,
        x: session.originX + event.clientX - session.startX,
        y: session.originY + event.clientY - session.startY,
      }));
    };

    const handleMouseUp = () => {
      panSessionRef.current = null;
      setIsPanning(false);
    };

    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('mouseup', handleMouseUp);
    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
    };
  }, []);

  const toggleNode = useCallback((nodeId: string) => {
    setExpandedIds((current) => {
      const next = new Set(current);
      if (next.has(nodeId)) {
        next.delete(nodeId);
      } else {
        next.add(nodeId);
      }
      return next;
    });
  }, []);

  const selectNode = useCallback((nodeId: string, centerOnCanvas = false) => {
    setSelectedId(nodeId);
    ensurePathExpanded(nodeId);
    if (centerOnCanvas) {
      window.requestAnimationFrame(() => {
        focusNode(nodeId);
      });
    }
  }, [ensurePathExpanded, focusNode]);

  const handleCanvasMouseDown = useCallback((event: ReactMouseEvent<HTMLDivElement>) => {
    const target = event.target as HTMLElement;
    if (target.closest('[data-bom-card="true"]')) {
      return;
    }
    panSessionRef.current = {
      startX: event.clientX,
      startY: event.clientY,
      originX: viewport.x,
      originY: viewport.y,
    };
    setIsPanning(true);
  }, [viewport.x, viewport.y]);

  const handleCanvasWheel = useCallback((event: ReactWheelEvent<HTMLDivElement>) => {
    event.preventDefault();

    if (!canvasViewportRef.current) {
      return;
    }

    if (event.ctrlKey || event.metaKey) {
      const rect = canvasViewportRef.current.getBoundingClientRect();
      const pointerX = event.clientX - rect.left;
      const pointerY = event.clientY - rect.top;
      const nextScale = clamp(viewport.scale * (event.deltaY > 0 ? 0.92 : 1.08), MIN_ZOOM, MAX_ZOOM);
      const worldX = (pointerX - viewport.x) / viewport.scale;
      const worldY = (pointerY - viewport.y) / viewport.scale;

      setViewport({
        scale: nextScale,
        x: pointerX - worldX * nextScale,
        y: pointerY - worldY * nextScale,
      });
      return;
    }

    setViewport((current) => ({
      ...current,
      x: current.x - event.deltaX,
      y: current.y - event.deltaY,
    }));
  }, [viewport.scale, viewport.x, viewport.y]);

  const canMoveIntoTarget = useCallback((sourceId: string, targetId: string) => {
    if (!structure || sourceId === structure.id || sourceId === targetId) {
      return false;
    }
    const sourceNode = findNode(structure, sourceId);
    if (!sourceNode) {
      return false;
    }
    return !findNode(sourceNode, targetId);
  }, [structure]);

  const executeMove = useCallback(async (sourceId: string, targetId: string) => {
    if (!structure) {
      return;
    }

    if (!canEditStructure) {
      setToast({ type: 'warning', text: 'Your role has read-only BOM access.' });
      return;
    }

    const sourceNode = findNode(structure, sourceId);
    const targetNode = findNode(structure, targetId);

    if (!sourceNode || !targetNode) {
      return;
    }

    if (sourceNode.parentId === targetId) {
      setToast({ type: 'info', text: `${sourceId} is already inside ${targetId}.` });
      return;
    }

    if (!canMoveIntoTarget(sourceId, targetId)) {
      setToast({ type: 'warning', text: 'A part cannot be moved onto itself or one of its descendants.' });
      return;
    }

    const nextStructure = moveNodeInTree(structure, sourceId, targetId);
    if (!nextStructure) {
      setToast({ type: 'warning', text: 'That structure move is not allowed.' });
      return;
    }

    const previousStructure = structure;
    setStructure(nextStructure);
    setSelectedId(sourceId);
    setExpandedIds((current) => {
      const next = new Set(current);
      next.add(targetId);
      if (sourceNode.children.length > 0) {
        next.add(sourceId);
      }
      return next;
    });
    setMovingId(sourceId);

    try {
      await plMasterService.updatePL(sourceId, {
        mother_part: targetId,
        mother_part_description: targetNode.description || targetNode.plNumber,
      });
      setToast({ type: 'success', text: `${sourceId} moved under ${targetId}.` });
    } catch {
      setStructure(previousStructure);
      setToast({ type: 'error', text: 'Failed to save the move. The previous hierarchy has been restored.' });
    } finally {
      setMovingId(null);
    }
  }, [canEditStructure, canMoveIntoTarget, structure]);

  const handleDragStart = useCallback((event: DragEvent<HTMLElement>, nodeId: string) => {
    if (!canEditStructure || movingId) {
      event.preventDefault();
      return;
    }
    event.dataTransfer.effectAllowed = 'move';
    event.dataTransfer.setData('text/plain', nodeId);
    setDraggedId(nodeId);
  }, [canEditStructure, movingId]);

  const handleDragEnd = useCallback(() => {
    setDraggedId(null);
    setDropTargetId(null);
  }, []);

  const handleDragOver = useCallback((event: DragEvent<HTMLElement>, targetId: string) => {
    const sourceId = draggedId || event.dataTransfer.getData('text/plain');
    if (!sourceId || !canMoveIntoTarget(sourceId, targetId)) {
      return;
    }
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
    setDropTargetId(targetId);
  }, [canMoveIntoTarget, draggedId]);

  const handleDrop = useCallback((event: DragEvent<HTMLElement>, targetId: string) => {
    event.preventDefault();
    const sourceId = draggedId || event.dataTransfer.getData('text/plain');
    setDraggedId(null);
    setDropTargetId(null);
    if (!sourceId) {
      return;
    }
    void executeMove(sourceId, targetId);
  }, [draggedId, executeMove]);

  const renderNavigatorNode = (node: StructureNode, depth: number) => {
    const branchVisible = branchMatches(node, normalizedNavigatorQuery);
    if (!branchVisible) {
      return null;
    }

    const forceOpen = Boolean(normalizedNavigatorQuery);
    const isExpanded = forceOpen || expandedIds.has(node.id);
    const isSelected = selectedId === node.id;
    const isDropTarget = dropTargetId === node.id && draggedId !== node.id;
    const isDragging = draggedId === node.id;

    return (
      <div key={node.id} className="bom-treeNode">
        <div
          className={[
            'bom-treeRow',
            isSelected ? 'is-selected' : '',
            isDropTarget ? 'is-dropTarget' : '',
            isDragging ? 'is-dragging' : '',
          ].filter(Boolean).join(' ')}
          style={{ '--depth': String(depth) } as React.CSSProperties}
          draggable={canEditStructure && node.id !== structure?.id}
          onDragStart={(event) => handleDragStart(event, node.id)}
          onDragEnd={handleDragEnd}
          onDragOver={(event) => handleDragOver(event, node.id)}
          onDrop={(event) => handleDrop(event, node.id)}
        >
          <button
            type="button"
            className="bom-treeToggle"
            onClick={() => node.children.length > 0 && toggleNode(node.id)}
            disabled={node.children.length === 0}
            aria-label={node.children.length > 0 ? (isExpanded ? 'Collapse node' : 'Expand node') : 'Leaf node'}
          >
            {node.children.length > 0 ? (isExpanded ? '-' : '+') : '.'}
          </button>

          <button
            type="button"
            className="bom-treeContent"
            onClick={() => selectNode(node.id, true)}
          >
            <span className="bom-treePl bom-mono">{node.plNumber}</span>
            <span className="bom-treeDesc">{node.description || 'No description'}</span>
            <span className="bom-treeMeta">
              {node.children.length} child{node.children.length === 1 ? '' : 'ren'}
            </span>
          </button>
        </div>

        {node.children.length > 0 && isExpanded && (
          <div className="bom-treeChildren">
            {node.children.map((child) => renderNavigatorNode(child, depth + 1))}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="bom-page">
      <Toast msg={toast} onClose={() => setToast(null)} />

      <PageHeader
        title="Bill of Materials"
        subtitle="Interactive engineering structure editor with accordion hierarchy, relationship mapping, and drag-and-drop reparenting."
      >
        <Btn size="sm" variant={tab === 'editor' ? 'primary' : 'secondary'} onClick={() => setTab('editor')}>
          Structure Editor
        </Btn>
        <Btn size="sm" variant={tab === 'catalog' ? 'primary' : 'secondary'} onClick={() => setTab('catalog')}>
          Part Catalog
        </Btn>
      </PageHeader>

      <div className="bom-toolbar">
        <SearchBar
          value={rootQuery}
          onChange={setRootQuery}
          placeholder="Load root PL number..."
          width={280}
        />

        <select
          className="bom-select"
          value={maxDepth}
          onChange={(event) => setMaxDepth(Number(event.target.value))}
        >
          {[2, 3, 4, 5, 6, 7].map((depth) => (
            <option key={depth} value={depth}>Depth {depth}</option>
          ))}
        </select>

        <Btn size="sm" onClick={() => void loadStructure()} loading={loadingStructure}>
          Load Structure
        </Btn>

        <Btn size="sm" variant="ghost" disabled={!structure} onClick={() => structure && setExpandedIds(getExpandableIds(structure))}>
          Expand All
        </Btn>

        <Btn size="sm" variant="ghost" disabled={!structure} onClick={() => structure && setExpandedIds(new Set([structure.id]))}>
          Collapse All
        </Btn>

        <Btn size="sm" variant="secondary" disabled={!structure} onClick={fitCanvas}>
          Fit Canvas
        </Btn>

        <Btn
          size="sm"
          variant="secondary"
          disabled={!selectedId}
          onClick={() => selectedId && focusNode(selectedId)}
        >
          Focus Selection
        </Btn>
      </div>

      {tab === 'catalog' ? (
        <CatalogTab
          onLoadAsRoot={(plNumber) => {
            setRootQuery(plNumber);
            void loadStructure(plNumber);
          }}
          onOpenPL={(plNumber) => navigate(`/pl-master/${plNumber}`)}
        />
      ) : (
        <div className="bom-shell">
          <aside className="bom-panel bom-panel--tree">
            <div className="bom-panelHeader">
              <div>
                <h3>Structure Navigator</h3>
                <p>Accordion view for assemblies and sub-assemblies.</p>
              </div>
              {loadedRoot && <span className="bom-chip bom-chip--outline">Root {loadedRoot}</span>}
            </div>

            <SearchBar
              value={navigatorQuery}
              onChange={setNavigatorQuery}
              placeholder="Filter the hierarchy..."
              width="100%"
            />

            {metrics && (
              <div className="bom-statGrid">
                <div className="bom-stat">
                  <span>{metrics.totalNodes}</span>
                  <small>Total nodes</small>
                </div>
                <div className="bom-stat">
                  <span>{metrics.visibleNodes}</span>
                  <small>Visible now</small>
                </div>
                <div className="bom-stat">
                  <span>{metrics.depth}</span>
                  <small>Levels</small>
                </div>
                <div className="bom-stat">
                  <span>{metrics.leafNodes}</span>
                  <small>Leaf parts</small>
                </div>
              </div>
            )}

            {!structure && (
              <div className="bom-emptyState bom-emptyState--panel">
                <h4>Load a root assembly</h4>
                <p>Enter a PL number and load the BOM tree to start editing the structure.</p>
              </div>
            )}

            {structure && (
              <>
                <div className="bom-instructions">
                  <strong>{canEditStructure ? 'Drag enabled.' : 'Read only.'}</strong>
                  <span>
                    {canEditStructure
                      ? 'Drag a row or card onto another assembly to rehome that part.'
                      : 'Open parts and explore the hierarchy from the navigator or canvas.'}
                  </span>
                </div>
                <div className="bom-treeViewport">
                  {renderNavigatorNode(structure, 0)}
                </div>
              </>
            )}
          </aside>

          <section className="bom-panel bom-panel--canvas">
            <div className="bom-panelHeader">
              <div>
                <h3>Structure Canvas</h3>
                <p>Pan across large assemblies and inspect relationships visually.</p>
              </div>
              <div className="bom-canvasControls">
                <Btn size="sm" variant="ghost" onClick={() => setViewport((current) => ({ ...current, scale: clamp(current.scale - 0.1, MIN_ZOOM, MAX_ZOOM) }))}>
                  Zoom Out
                </Btn>
                <Btn size="sm" variant="ghost" onClick={() => setViewport((current) => ({ ...current, scale: clamp(current.scale + 0.1, MIN_ZOOM, MAX_ZOOM) }))}>
                  Zoom In
                </Btn>
                <Btn size="sm" variant="secondary" onClick={() => setViewport({ x: 72, y: 72, scale: 1 })}>
                  Reset View
                </Btn>
              </div>
            </div>

            {!structure ? (
              <div className="bom-emptyState">
                <h4>No structure loaded</h4>
                <p>Load a BOM tree first. The canvas then becomes a lightweight engineering editor instead of a static list.</p>
              </div>
            ) : (
              <div
                ref={canvasViewportRef}
                className={`bom-canvasViewport ${isPanning ? 'is-panning' : ''}`}
                onMouseDown={handleCanvasMouseDown}
                onWheel={handleCanvasWheel}
              >
                <div
                  className="bom-canvasTransform"
                  style={{
                    width: `${layout.contentWidth}px`,
                    height: `${layout.contentHeight}px`,
                    transform: `translate(${viewport.x}px, ${viewport.y}px) scale(${viewport.scale})`,
                  }}
                >
                  <svg className="bom-canvasLinks" width={layout.contentWidth} height={layout.contentHeight} viewBox={`0 0 ${layout.contentWidth} ${layout.contentHeight}`}>
                    {layout.edges.map((edge) => {
                      const source = layout.positions[edge.sourceId];
                      const target = layout.positions[edge.targetId];
                      const isActive = selectedPathIds.has(edge.sourceId) && selectedPathIds.has(edge.targetId);

                      if (!source || !target) {
                        return null;
                      }

                      const startX = source.x + CARD_WIDTH;
                      const startY = source.y + CARD_HEIGHT / 2;
                      const endX = target.x;
                      const endY = target.y + CARD_HEIGHT / 2;
                      const bend = Math.max(40, (endX - startX) / 2);

                      return (
                        <path
                          key={`${edge.sourceId}-${edge.targetId}`}
                          d={`M ${startX} ${startY} C ${startX + bend} ${startY}, ${endX - bend} ${endY}, ${endX} ${endY}`}
                          className={isActive ? 'is-active' : ''}
                        />
                      );
                    })}
                  </svg>

                  {layout.visibleIds.map((nodeId) => {
                    const node = nodeIndex[nodeId];
                    const position = layout.positions[nodeId];
                    const isExpanded = expandedIds.has(nodeId);
                    const isSelected = selectedId === nodeId;
                    const isDropTarget = dropTargetId === nodeId && draggedId !== nodeId;
                    const isDragging = draggedId === nodeId;
                    const isMatchResult = isMatch(node, normalizedNavigatorQuery);

                    return (
                      <div
                        key={nodeId}
                        data-bom-card="true"
                        className={[
                          'bom-card',
                          isSelected ? 'is-selected' : '',
                          isDropTarget ? 'is-dropTarget' : '',
                          isDragging ? 'is-dragging' : '',
                          isMatchResult ? 'is-match' : '',
                        ].filter(Boolean).join(' ')}
                        style={{ left: `${position.x}px`, top: `${position.y}px` }}
                        draggable={canEditStructure && nodeId !== structure.id}
                        onDragStart={(event) => handleDragStart(event, nodeId)}
                        onDragEnd={handleDragEnd}
                        onDragOver={(event) => handleDragOver(event, nodeId)}
                        onDrop={(event) => handleDrop(event, nodeId)}
                        onClick={() => selectNode(nodeId)}
                      >
                        <div className="bom-cardHeader">
                          <div>
                            <span className="bom-cardEyebrow">{node.parentId ? 'Assembly node' : 'Root assembly'}</span>
                            <strong className="bom-cardTitle bom-mono">{node.plNumber}</strong>
                          </div>
                          <button
                            type="button"
                            className="bom-cardToggle"
                            disabled={node.children.length === 0}
                            onClick={(event) => {
                              event.stopPropagation();
                              toggleNode(node.id);
                            }}
                            aria-label={node.children.length > 0 ? (isExpanded ? 'Collapse node' : 'Expand node') : 'Leaf node'}
                          >
                            {node.children.length > 0 ? (isExpanded ? '-' : '+') : '.'}
                          </button>
                        </div>

                        <p className="bom-cardDescription">{node.description || 'No description available.'}</p>

                        <div className="bom-cardMeta">
                          {node.inspectionCategory && <span className="bom-chip bom-chip--category">{node.inspectionCategory}</span>}
                          {node.safetyItem && <span className="bom-chip bom-chip--safety">Safety</span>}
                          <span className="bom-chip bom-chip--outline">{node.children.length} child{node.children.length === 1 ? '' : 'ren'}</span>
                        </div>

                        <div className="bom-cardFooter">
                          <button
                            type="button"
                            className="bom-linkButton"
                            onClick={(event) => {
                              event.stopPropagation();
                              navigate(`/pl-master/${node.plNumber}`);
                            }}
                          >
                            Open PL
                          </button>
                          <button
                            type="button"
                            className="bom-linkButton"
                            onClick={(event) => {
                              event.stopPropagation();
                              selectNode(node.id, true);
                            }}
                          >
                            Center
                          </button>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </section>

          <aside className="bom-panel bom-panel--inspector">
            <div className="bom-panelHeader">
              <div>
                <h3>Inspector</h3>
                <p>Chronology and hierarchy details for the selected part.</p>
              </div>
              {selectedNode && <span className="bom-chip bom-chip--outline">Level {selectedNode.level + 1}</span>}
            </div>

            {!selectedNode ? (
              <div className="bom-emptyState bom-emptyState--panel">
                <h4>No selection</h4>
                <p>Select a node from the navigator or the canvas to inspect it.</p>
              </div>
            ) : (
              <div className="bom-inspector">
                <div className="bom-inspectorHero">
                  <div>
                    <span className="bom-cardEyebrow">Selected node</span>
                    <h4 className="bom-mono">{selectedNode.plNumber}</h4>
                  </div>
                  {movingId === selectedNode.id && <span className="bom-chip bom-chip--pending">Saving move...</span>}
                </div>

                <p className="bom-inspectorDescription">
                  {(selectedDetail?.part_description ?? selectedNode.description) || 'No description available.'}
                </p>

                <div className="bom-breadcrumbs">
                  {selectedPath.map((node, index) => (
                    <button
                      key={node.id}
                      type="button"
                      className="bom-breadcrumb"
                      onClick={() => selectNode(node.id, true)}
                    >
                      {node.plNumber}
                      {index < selectedPath.length - 1 && <span>/</span>}
                    </button>
                  ))}
                </div>

                <div className="bom-inspectorGrid">
                  <div>
                    <span>Parent</span>
                    <strong className="bom-mono">{selectedNode.parentId ?? 'Root'}</strong>
                  </div>
                  <div>
                    <span>Children</span>
                    <strong>{selectedNode.children.length}</strong>
                  </div>
                  <div>
                    <span>Inspection</span>
                    <strong>{(selectedDetail?.inspection_category ?? selectedNode.inspectionCategory) || '-'}</strong>
                  </div>
                  <div>
                    <span>Safety</span>
                    <strong>{selectedDetail?.safety_item ?? selectedNode.safetyItem ? 'Yes' : 'No'}</strong>
                  </div>
                  <div>
                    <span>Agency</span>
                    <strong>{selectedDetail?.controlling_agency_code || '-'}</strong>
                  </div>
                  <div>
                    <span>Application</span>
                    <strong>{(selectedDetail?.application_area ?? selectedNode.applicationArea) || '-'}</strong>
                  </div>
                </div>

                <div className="bom-inspectorBlock">
                  <span className="bom-inspectorLabel">Loco applicability</span>
                  <div className="bom-inlineList">
                    {(selectedDetail?.used_in ?? selectedNode.usedIn).length > 0
                      ? (selectedDetail?.used_in ?? selectedNode.usedIn).map((item) => (
                          <span key={item} className="bom-chip bom-chip--outline">{item}</span>
                        ))
                      : <span className="bom-tableMuted">Not specified</span>}
                  </div>
                </div>

                <div className="bom-inspectorBlock">
                  <span className="bom-inspectorLabel">Engineering actions</span>
                  <div className="bom-inspectorActions">
                    <Btn size="sm" onClick={() => navigate(`/pl-master/${selectedNode.plNumber}`)}>
                      Open PL
                    </Btn>
                    <Btn size="sm" variant="secondary" onClick={() => void loadStructure(selectedNode.plNumber)}>
                      Load As Root
                    </Btn>
                    <Btn size="sm" variant="ghost" onClick={() => focusNode(selectedNode.id)}>
                      Center On Canvas
                    </Btn>
                    <Btn
                      size="sm"
                      variant="ghost"
                      disabled={!canEditStructure || selectedNode.id === structure?.id}
                      onClick={() => structure && selectedNode.parentId && void executeMove(selectedNode.id, structure.id)}
                    >
                      Move To Top Level
                    </Btn>
                  </div>
                </div>

                <div className="bom-inspectorBlock">
                  <span className="bom-inspectorLabel">Remarks</span>
                  <p className="bom-inspectorNotes">{loadingDetail ? 'Loading latest detail...' : selectedDetail?.remarks || 'No remarks recorded.'}</p>
                </div>
              </div>
            )}
          </aside>
        </div>
      )}
    </div>
  );
}
