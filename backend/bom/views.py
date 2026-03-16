import logging
from rest_framework.views import APIView
from rest_framework import permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
from .models import BOMTree, BOMNode, BOMSnapshot
from .serializers import BOMTreeSerializer, BOMNodeSerializer, BOMSnapshotSerializer

log = logging.getLogger('edms.bom')
CAT_COLOR = {'A': '#ef4444', 'B': '#f59e0b', 'C': '#22c55e', 'D': '#3b82f6', '': '#6b7280'}


def _recalc_level(node):
    depth, cur, visited = 0, node, set()
    while cur.parent_id and cur.parent_id not in visited:
        visited.add(cur.id)
        cur = cur.parent
        depth += 1
        if depth > 30:
            break
    node.level = depth
    node.save(update_fields=['level'])
    for child in node.children.filter(is_active=True):
        child.parent = node
        _recalc_level(child)


def _build_reactflow(tree_id):
    qs = BOMNode.objects.filter(tree_id=tree_id, is_active=True).select_related('parent')
    rf_nodes, rf_edges = [], []
    for n in qs:
        rf_nodes.append({
            'id': str(n.id),
            'type': 'bomNode',
            'position': {'x': n.canvas_x, 'y': n.canvas_y},
            'data': {
                'id': n.id, 'pl_number': n.pl_number, 'description': n.description,
                'node_type': n.node_type, 'inspection_category': n.inspection_category,
                'safety_item': n.safety_item, 'quantity': str(n.quantity), 'unit': n.unit,
                'level': n.level,
                'children_count': n.children.filter(is_active=True).count(),
                'cat_color': CAT_COLOR.get(n.inspection_category, '#6b7280'),
                'remarks': n.remarks,
            },
        })
        if n.parent_id:
            rf_edges.append({
                'id': f'e{n.parent_id}-{n.id}',
                'source': str(n.parent_id),
                'target': str(n.id),
                'type': 'smoothstep',
                'animated': False,
                'style': {'stroke': '#2d3555', 'strokeWidth': 2},
            })
    return {'nodes': rf_nodes, 'edges': rf_edges}


# ---------------------------------------------------------------------------
class BOMTreeListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        qs = BOMTree.objects.filter(is_active=True)
        loco = request.query_params.get('loco_type')
        if loco:
            qs = qs.filter(loco_type=loco)
        return Response(BOMTreeSerializer(qs, many=True).data)

    def post(self, request):
        ser = BOMTreeSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        ser.save(created_by=request.user)
        return Response(ser.data, status=status.HTTP_201_CREATED)


class BOMTreeDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def _get(self, pk): return get_object_or_404(BOMTree, pk=pk)

    def get(self, request, pk):
        return Response(BOMTreeSerializer(self._get(pk)).data)

    def patch(self, request, pk):
        ser = BOMTreeSerializer(self._get(pk), data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response(ser.data)

    def delete(self, request, pk):
        t = self._get(pk)
        t.is_active = False
        t.save(update_fields=['is_active'])
        return Response(status=status.HTTP_204_NO_CONTENT)


class BOMTreeNodesView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        qs = BOMNode.objects.filter(tree_id=pk, is_active=True).select_related('parent')
        return Response(BOMNodeSerializer(qs, many=True).data)


class BOMReactFlowView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        get_object_or_404(BOMTree, pk=pk)
        return Response(_build_reactflow(pk))


class BOMSnapshotListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        tree = get_object_or_404(BOMTree, pk=pk)
        return Response(BOMSnapshotSerializer(tree.snapshots.all(), many=True).data)

    def post(self, request, pk):
        get_object_or_404(BOMTree, pk=pk)
        ser = BOMSnapshotSerializer(data={
            'tree': pk,
            'name': request.data.get('name', ''),
            'description': request.data.get('description', ''),
        })
        ser.is_valid(raise_exception=True)
        snap = ser.save(created_by=request.user, snapshot_data=_build_reactflow(pk))
        return Response(BOMSnapshotSerializer(snap).data, status=status.HTTP_201_CREATED)


class BOMNodeCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        ser = BOMNodeSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        node = ser.save(created_by=request.user, updated_by=request.user)
        node.recalculate_level()
        node.save(update_fields=['level'])
        log.info('BOM node %s created by %s', node.pl_number, request.user)
        return Response(BOMNodeSerializer(node).data, status=status.HTTP_201_CREATED)


class BOMNodeDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def _get(self, pk): return get_object_or_404(BOMNode, pk=pk)

    def get(self, request, pk):
        return Response(BOMNodeSerializer(self._get(pk)).data)

    def patch(self, request, pk):
        node = self._get(pk)
        ser = BOMNodeSerializer(node, data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        ser.save(updated_by=request.user)
        return Response(BOMNodeSerializer(node).data)

    def delete(self, request, pk):
        node = self._get(pk)
        mode = request.query_params.get('mode', 'promote')
        with transaction.atomic():
            if mode == 'cascade':
                self._cascade(node)
            else:
                for child in node.children.filter(is_active=True):
                    child.parent = node.parent
                    child.save(update_fields=['parent'])
                    _recalc_level(child)
            node.is_active = False
            node.updated_by = request.user
            node.save(update_fields=['is_active', 'updated_by', 'updated_at'])
        return Response(status=status.HTTP_204_NO_CONTENT)

    def _cascade(self, node):
        for child in node.children.filter(is_active=True):
            self._cascade(child)
        node.is_active = False
        node.save(update_fields=['is_active'])


class BOMNodeMoveView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        node = get_object_or_404(BOMNode, pk=pk)
        new_parent = request.data.get('parent_id')
        if new_parent:
            parent = get_object_or_404(BOMNode, pk=new_parent, tree=node.tree)
            cur = parent
            while cur:
                if cur.id == node.id:
                    return Response(
                        {'detail': 'Circular reference - cannot make a node its own ancestor.'},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                cur = cur.parent
            node.parent = parent
        else:
            node.parent = None
        with transaction.atomic():
            node.updated_by = request.user
            node.save(update_fields=['parent', 'updated_by', 'updated_at'])
            _recalc_level(node)
        return Response(BOMNodeSerializer(node).data)


class BOMNodeCanvasView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        node = get_object_or_404(BOMNode, pk=pk)
        node.canvas_x = float(request.data.get('x', node.canvas_x))
        node.canvas_y = float(request.data.get('y', node.canvas_y))
        node.save(update_fields=['canvas_x', 'canvas_y', 'updated_at'])
        return Response({'id': node.id, 'x': node.canvas_x, 'y': node.canvas_y})
