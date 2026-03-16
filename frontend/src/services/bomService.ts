import api from '../api/axios';

const B = '/bom';

export const bomService = {
  listTrees: (locoType?: string) =>
    api.get(`${B}/trees/`, { params: locoType ? { loco_type: locoType } : {} }).then(r => r.data),

  createTree: (data: Record<string, unknown>) =>
    api.post(`${B}/trees/`, data).then(r => r.data),

  updateTree: (id: number, data: Record<string, unknown>) =>
    api.patch(`${B}/trees/${id}/`, data).then(r => r.data),

  deleteTree: (id: number) => api.delete(`${B}/trees/${id}/`),

  getReactFlow: (treeId: number) =>
    api.get(`${B}/trees/${treeId}/nodes/reactflow/`).then(r => r.data),

  listSnapshots: (treeId: number) =>
    api.get(`${B}/trees/${treeId}/snapshots/`).then(r => r.data),

  createSnapshot: (treeId: number, name: string, description = '') =>
    api.post(`${B}/trees/${treeId}/snapshots/`, { name, description }).then(r => r.data),

  createNode: (data: Record<string, unknown>) =>
    api.post(`${B}/nodes/`, data).then(r => r.data),

  updateNode: (id: number, data: Record<string, unknown>) =>
    api.patch(`${B}/nodes/${id}/`, data).then(r => r.data),

  deleteNode: (id: number, mode: 'cascade' | 'promote' = 'promote') =>
    api.delete(`${B}/nodes/${id}/`, { params: { mode } }),

  moveNode: (id: number, parentId: number | null) =>
    api.patch(`${B}/nodes/${id}/move/`, { parent_id: parentId }).then(r => r.data),

  saveCanvas: (id: number, x: number, y: number) =>
    api.patch(`${B}/nodes/${id}/canvas/`, { x, y }).then(r => r.data),
};
