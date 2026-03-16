import React, { useState, useCallback, useEffect, useRef } from 'react';
import {
  ReactFlow, Background, Controls, MiniMap, useNodesState, useEdgesState,
  addEdge, Node, Edge, NodeTypes, Connection, NodeDragHandler,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { bomService } from '../../services/bomService';
import BOMNodeCard, { BOMNodeData } from './BOMNodeCard';
import WhereUsedModal from './WhereUsedModal';

const LOCO_TYPES = ['WAG9','WAG9H','WAG12B','WAP7','WAP5','DETC','MEMU','DEMU','WDG4','WDP4'];

const nodeTypes: NodeTypes = { bomNode: BOMNodeCard as any };

interface Flash { msg: string; type: 'success'|'error'; }
interface ModalState {
  type: 'newTree'|'addNode'|'editNode'|'deleteNode'|'moveNode'|'snapshot'|null;
  nodeId?: number;
  treeId?: number;
}

const S = {
  page:    { background:'#0d1117', minHeight:'100vh', display:'flex', flexDirection:'column' as const },
  toolbar: { display:'flex', alignItems:'center', gap:8, padding:'8px 16px',
             background:'#151b2e', borderBottom:'1px solid #1e2a3e', flexWrap:'wrap' as const },
  select:  { background:'#1e2332', color:'#e2e8f0', border:'1px solid #2d3555',
             borderRadius:6, padding:'5px 10px', fontSize:13, cursor:'pointer' },
  btn:     (g: string) => ({ background:g, color:'#fff', border:'none', borderRadius:6,
             padding:'6px 14px', fontSize:12, cursor:'pointer', fontWeight:600 }),
  modal:   { position:'fixed' as const, inset:0, background:'#000a', zIndex:9000,
             display:'flex', alignItems:'center', justifyContent:'center' },
  mbox:    { background:'#151b2e', border:'1px solid #2d3555', borderRadius:12,
             padding:28, minWidth:340, maxWidth:480, width:'90%', color:'#e2e8f0' },
  input:   { width:'100%', background:'#1e2332', border:'1px solid #2d3555', borderRadius:6,
             color:'#e2e8f0', padding:'7px 10px', fontSize:13, boxSizing:'border-box' as const, marginTop:4 },
  label:   { fontSize:12, color:'#9ca3af', display:'block' as const, marginTop:10 },
};

function Flash({ flash }: { flash: Flash|null }) {
  if (!flash) return null;
  return (
    <div style={{
      position:'fixed', top:16, right:16, zIndex:9999,
      background: flash.type==='success' ? '#14532d' : '#7f1d1d',
      border:`1px solid ${flash.type==='success'?'#22c55e':'#ef4444'}`,
      color:'#fff', padding:'10px 20px', borderRadius:8, fontSize:13, maxWidth:320,
    }}>{flash.msg}</div>
  );
}

export default function BOMPage() {
  const { user } = useAuth();
  const navigate  = useNavigate();
  const isAdmin   = !!(user?.role === 'Admin' || (user as any)?.is_staff);

  const [locoType,    setLocoType]    = useState('');
  const [trees,       setTrees]       = useState<any[]>([]);
  const [treeId,      setTreeId]      = useState<number|null>(null);
  const [nodes,       setNodes, onNodesChange] = useNodesState<Node>([]);
  const [edges,       setEdges, onEdgesChange] = useEdgesState<Edge>([]);
  const [snapshots,   setSnapshots]   = useState<any[]>([]);
  const [snapOpen,    setSnapOpen]    = useState(false);
  const [flash,       setFlash]       = useState<Flash|null>(null);
  const [modal,       setModal]       = useState<ModalState>({ type: null });
  const [form,        setForm]        = useState<Record<string, string>>({});
  const [whereUsedPL, setWhereUsedPL] = useState<string>('');
  const dragTimer = useRef<ReturnType<typeof setTimeout>|null>(null);

  const showFlash = (msg: string, type: 'success'|'error' = 'success') => {
    setFlash({ msg, type });
    setTimeout(() => setFlash(null), 4000);
  };

  const loadTrees = useCallback(async (lt = locoType) => {
    try { setTrees(await bomService.listTrees(lt || undefined)); }
    catch { showFlash('Failed to load trees', 'error'); }
  }, [locoType]);

  useEffect(() => { loadTrees(); }, [locoType]);

  const loadCanvas = useCallback(async (id: number) => {
    try {
      const data = await bomService.getReactFlow(id);
      const withCb = (data.nodes as Node[]).map((n: Node) => ({
        ...n,
        data: {
          ...(n.data as BOMNodeData),
          isAdmin,
          onOpenPL:   (pl: string) => navigate(`/pl-master/${pl}`),
          onAddChild: (nid: number) => openModal('addNode', nid),
          onEdit:     (nid: number) => openModal('editNode', nid),
          onDelete:   (nid: number) => openModal('deleteNode', nid),
          onMove:     (nid: number) => openModal('moveNode', nid),
          onWhereUsed:(pl: string) => setWhereUsedPL(pl),
        },
      }));
      setNodes(withCb);
      setEdges(data.edges as Edge[]);
    } catch { showFlash('Failed to load canvas', 'error'); }
  }, [isAdmin, navigate, setNodes, setEdges]);

  useEffect(() => { if (treeId) loadCanvas(treeId); }, [treeId]);

  const openModal = (type: ModalState['type'], nodeId?: number) => {
    setForm({});
    setModal({ type, nodeId, treeId: treeId ?? undefined });
  };
  const closeModal = () => setModal({ type: null });

  const onNodeDragStop: NodeDragHandler = useCallback((_e, node) => {
    if (dragTimer.current) clearTimeout(dragTimer.current);
    dragTimer.current = setTimeout(() => {
      bomService.saveCanvas(Number(node.id), node.position.x, node.position.y).catch(() => {});
    }, 600);
  }, []);

  // ---- Modal submit handlers ----
  const handleSubmit = async () => {
    try {
      switch (modal.type) {
        case 'newTree': {
          await bomService.createTree({ loco_type: form.loco_type, variant: form.variant||'', description: form.description||'' });
          showFlash('Tree created!');
          await loadTrees();
          break;
        }
        case 'addNode': {
          await bomService.createNode({
            tree: treeId, parent: modal.nodeId || null,
            pl_number: form.pl_number, description: form.description||'',
            node_type: form.node_type||'PART', inspection_category: form.inspection_category||'',
            safety_item: form.safety_item==='true', quantity: form.quantity||1, unit: form.unit||'Nos',
            remarks: form.remarks||'',
          });
          showFlash('Node added!');
          if (treeId) await loadCanvas(treeId);
          break;
        }
        case 'editNode': {
          if (!modal.nodeId) break;
          await bomService.updateNode(modal.nodeId, {
            pl_number: form.pl_number, description: form.description,
            node_type: form.node_type, inspection_category: form.inspection_category,
            safety_item: form.safety_item==='true', quantity: form.quantity, unit: form.unit, remarks: form.remarks,
          });
          showFlash('Node updated!');
          if (treeId) await loadCanvas(treeId);
          break;
        }
        case 'deleteNode': {
          if (!modal.nodeId) break;
          await bomService.deleteNode(modal.nodeId, (form.mode || 'promote') as 'promote'|'cascade');
          showFlash('Node removed.');
          if (treeId) await loadCanvas(treeId);
          break;
        }
        case 'moveNode': {
          if (!modal.nodeId) break;
          const pid = form.parent_id ? Number(form.parent_id) : null;
          await bomService.moveNode(modal.nodeId, pid);
          showFlash('Node moved!');
          if (treeId) await loadCanvas(treeId);
          break;
        }
        case 'snapshot': {
          if (!treeId) break;
          await bomService.createSnapshot(treeId, form.name||'Snapshot', form.description||'');
          showFlash('Snapshot saved!');
          setSnapshots(await bomService.listSnapshots(treeId));
          break;
        }
      }
      closeModal();
    } catch (e: any) {
      showFlash(e?.response?.data?.detail || 'Error', 'error');
    }
  };

  const loadSnapshots = async () => {
    if (!treeId) return;
    setSnapshots(await bomService.listSnapshots(treeId));
    setSnapOpen(true);
  };

  const f = (key: string, label: string, type = 'text', opts?: string[]) => (
    <div>
      <label style={S.label}>{label}</label>
      {opts ? (
        <select value={form[key]||''} onChange={e => setForm(v => ({...v,[key]:e.target.value}))}
          style={{...S.input, marginTop:4}}>
          <option value=''>-- select --</option>
          {opts.map(o => <option key={o} value={o}>{o}</option>)}
        </select>
      ) : (
        <input type={type} value={form[key]||''}
          onChange={e => setForm(v => ({...v,[key]:e.target.value}))}
          style={S.input} />
      )}
    </div>
  );

  const nodeFormFields = () => <>
    {f('pl_number',           'PL Number *')}
    {f('description',         'Description')}
    {f('node_type',           'Type',                'text', ['ASSEMBLY','SUBASSEMBLY','COMPONENT','PART'])}
    {f('inspection_category', 'Inspection Category', 'text', ['','A','B','C','D'])}
    {f('safety_item',         'Safety Item',         'text', ['false','true'])}
    {f('quantity',            'Quantity',            'number')}
    {f('unit',                'Unit')}
    {f('remarks',             'Remarks')}
  </>;

  return (
    <div style={S.page}>
      <Flash flash={flash} />

      {/* Toolbar */}
      <div style={S.toolbar}>
        <span style={{ color:'#60a5fa', fontWeight:700, fontSize:14 }}>BOM Canvas</span>
        <select value={locoType} onChange={e => { setLocoType(e.target.value); setTreeId(null); }}
          style={S.select}>
          <option value=''>All Loco Types</option>
          {LOCO_TYPES.map(l => <option key={l} value={l}>{l}</option>)}
        </select>
        <select value={treeId ?? ''} onChange={e => setTreeId(Number(e.target.value) || null)}
          style={S.select}>
          <option value=''>-- Select BOM Tree --</option>
          {trees.map(t => <option key={t.id} value={t.id}>{t.loco_type} {t.variant} ({t.node_count} nodes)</option>)}
        </select>
        {isAdmin && (
          <>
            <button onClick={() => openModal('newTree')} style={S.btn('linear-gradient(135deg,#4b6cb7,#182848)')}>+ New Tree</button>
            <button onClick={() => openModal('addNode')} disabled={!treeId}
              style={S.btn('linear-gradient(135deg,#14532d,#052e16)')}>+ Root Node</button>
            <button onClick={() => openModal('snapshot')} disabled={!treeId}
              style={S.btn('linear-gradient(135deg,#7c3aed,#3b0764)')}>Save Snapshot</button>
          </>
        )}
        <button onClick={loadSnapshots} disabled={!treeId}
          style={S.btn('linear-gradient(135deg,#1e3a5f,#0f172a)')}>Snapshots</button>
      </div>

      <div style={{ flex: 1, position: 'relative' }}>
        {!treeId ? (
          <div style={{ display:'flex', flexDirection:'column', alignItems:'center',
            justifyContent:'center', height:'100%', gap:16, color:'#4b5563' }}>
            <div style={{ fontSize:48 }}>🏛️</div>
            <div style={{ fontSize:18, fontWeight:600 }}>Select a BOM Tree to begin</div>
            {isAdmin && (
              <button onClick={() => openModal('newTree')}
                style={S.btn('linear-gradient(135deg,#4b6cb7,#182848)')}>Create First BOM Tree</button>
            )}
          </div>
        ) : (
          <ReactFlow
            nodes={nodes} edges={edges}
            onNodesChange={onNodesChange} onEdgesChange={onEdgesChange}
            onConnect={(c: Connection) => setEdges(eds => addEdge(c, eds))}
            onNodeDragStop={onNodeDragStop}
            nodeTypes={nodeTypes}
            fitView deleteKeyCode={null}
            style={{ background:'#0d1117' }}>
            <Background color='#1e2a3e' gap={20} />
            <Controls style={{ background:'#151b2e', border:'1px solid #2d3555' }} />
            <MiniMap
              style={{ background:'#151b2e', border:'1px solid #2d3555' }}
              nodeColor={(n: Node) => (n.data as BOMNodeData).cat_color || '#6b7280'}
            />
          </ReactFlow>
        )}

        {/* Snapshot panel */}
        {snapOpen && (
          <div style={{
            position:'absolute', top:0, right:0, bottom:0, width:280,
            background:'#151b2e', borderLeft:'1px solid #2d3555',
            overflowY:'auto', padding:16, zIndex:100,
          }}>
            <div style={{ display:'flex', justifyContent:'space-between', marginBottom:12 }}>
              <span style={{ fontWeight:700, color:'#60a5fa', fontSize:13 }}>Snapshots</span>
              <button onClick={() => setSnapOpen(false)} style={{ background:'none', border:'none', color:'#9ca3af', cursor:'pointer', fontSize:18 }}>×</button>
            </div>
            {snapshots.length === 0 && <div style={{ color:'#6b7280', fontSize:12 }}>No snapshots yet.</div>}
            {snapshots.map((s: any) => (
              <div key={s.id} style={{ background:'#1e2332', borderRadius:8, padding:10, marginBottom:8, border:'1px solid #2d3555' }}>
                <div style={{ fontWeight:700, fontSize:12, color:'#e2e8f0' }}>{s.name}</div>
                <div style={{ fontSize:11, color:'#9ca3af', marginTop:2 }}>{s.description}</div>
                <div style={{ fontSize:10, color:'#6b7280', marginTop:4 }}>
                  {s.created_by_name} &bull; {new Date(s.created_at).toLocaleDateString()}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Modals */}
      {modal.type && (
        <div style={S.modal} onClick={e => e.target===e.currentTarget && closeModal()}>
          <div style={S.mbox}>
            <h3 style={{ margin:'0 0 14px', color:'#60a5fa', fontSize:16 }}>
              {modal.type==='newTree'    && 'New BOM Tree'}
              {modal.type==='addNode'    && 'Add Node'}
              {modal.type==='editNode'   && 'Edit Node'}
              {modal.type==='deleteNode' && 'Remove Node'}
              {modal.type==='moveNode'   && 'Move / Reparent Node'}
              {modal.type==='snapshot'   && 'Save Snapshot'}
            </h3>

            {modal.type==='newTree' && <>
              {f('loco_type','Loco Type *','text',LOCO_TYPES)}
              {f('variant','Variant (optional)')}
              {f('description','Description')}
            </>}

            {(modal.type==='addNode'||modal.type==='editNode') && nodeFormFields()}

            {modal.type==='deleteNode' && <>
              <p style={{ color:'#fca5a5', margin:'0 0 12px' }}>Choose how to handle child nodes:</p>
              <div style={{ display:'flex', gap:8 }}>
                <button onClick={() => { setForm(v=>({...v,mode:'promote'})); }}
                  style={{...S.btn('linear-gradient(135deg,#1e3a5f,#0f172a)'),
                    flex:1, border: form.mode!=='cascade'?'2px solid #60a5fa':'2px solid transparent'}}>
                  Promote children
                </button>
                <button onClick={() => { setForm(v=>({...v,mode:'cascade'})); }}
                  style={{...S.btn('linear-gradient(135deg,#7f1d1d,#3f0606)'),
                    flex:1, border: form.mode==='cascade'?'2px solid #ef4444':'2px solid transparent'}}>
                  Cascade delete
                </button>
              </div>
            </>}

            {modal.type==='moveNode' && <>
              <p style={{ color:'#9ca3af', fontSize:12, margin:'0 0 8px' }}>Enter new parent node ID (leave blank for root).</p>
              {f('parent_id','New Parent Node ID','number')}
            </>}

            {modal.type==='snapshot' && <>
              {f('name','Snapshot Name *')}
              {f('description','Description')}
            </>}

            <div style={{ display:'flex', gap:8, marginTop:20, justifyContent:'flex-end' }}>
              <button onClick={closeModal} style={S.btn('#374151')}>Cancel</button>
              <button onClick={handleSubmit} style={S.btn('linear-gradient(135deg,#4b6cb7,#182848)')}>Confirm</button>
            </div>
          </div>
        </div>
      )}

      {whereUsedPL && (
        <WhereUsedModal plNumber={whereUsedPL} onClose={() => setWhereUsedPL('')} />
      )}
    </div>
  );
}
