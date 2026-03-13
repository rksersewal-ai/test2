# =============================================================================
# FILE: apps/workledger/dropdown_views.py
# PURPOSE: Admin CRUD views for dropdown management + public read endpoints
# =============================================================================
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .dropdown_models import DropdownMaster, DropdownAuditLog
from .dropdown_serializers import (
    DropdownItemSerializer,
    DropdownCreateSerializer,
    DropdownUpdateSerializer,
    DropdownAuditLogSerializer,
)
from .dropdown_services import (
    create_dropdown_item,
    update_dropdown_item,
    deactivate_dropdown_item,
    delete_dropdown_item,
    get_dropdown_group,
    get_all_groups,
)
from .permissions import get_user_role, ROLE_ADMIN


def require_admin(request):
    return get_user_role(request) == ROLE_ADMIN


# ---------------------------------------------------------------------------
# PUBLIC: GET /api/dropdowns/{group_key}/
# Returns sorted active items for a single dropdown group.
# Used by all form components to populate <select> elements.
# ---------------------------------------------------------------------------
class DropdownGroupView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, group_key: str):
        items = get_dropdown_group(group_key)
        return Response(DropdownItemSerializer(items, many=True).data)


# ---------------------------------------------------------------------------
# PUBLIC: GET /api/dropdowns/
# Returns all groups with their active items (for preloading in frontend).
# ---------------------------------------------------------------------------
class DropdownAllGroupsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        groups = get_all_groups()
        result = [
            {
                'group_key': gk,
                'items': DropdownItemSerializer(items, many=True).data,
            }
            for gk, items in groups.items()
        ]
        return Response(result)


# ---------------------------------------------------------------------------
# ADMIN: GET + POST /api/admin/dropdowns/{group_key}/
# GET  - list all items (including inactive) for admin management view.
# POST - add a new item to the group.
# ---------------------------------------------------------------------------
class AdminDropdownGroupView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, group_key: str):
        if not require_admin(request):
            return Response({'detail': 'Admin only.'}, status=403)
        items = DropdownMaster.objects.filter(group_key=group_key).order_by('label')
        data = []
        for item in items:
            d = DropdownItemSerializer(item).data
            d['is_active'] = item.is_active
            d['is_system'] = item.is_system
            data.append(d)
        return Response(data)

    def post(self, request, group_key: str):
        if not require_admin(request):
            return Response({'detail': 'Admin only.'}, status=403)
        payload = {**request.data, 'group_key': group_key}
        serializer = DropdownCreateSerializer(data=payload)
        if serializer.is_valid():
            item = create_dropdown_item(serializer.validated_data, created_by=request.user.id)
            return Response(DropdownItemSerializer(item).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=400)


# ---------------------------------------------------------------------------
# ADMIN: GET + PATCH + DELETE /api/admin/dropdowns/{group_key}/{item_id}/
# GET    - single item detail.
# PATCH  - update label / sort_override / is_active.
# DELETE - hard delete (system items blocked), or pass ?deactivate=1 to soft-delete.
# ---------------------------------------------------------------------------
class AdminDropdownItemView(APIView):
    permission_classes = [IsAuthenticated]

    def _get_item(self, group_key: str, item_id: int):
        try:
            return DropdownMaster.objects.get(pk=item_id, group_key=group_key)
        except DropdownMaster.DoesNotExist:
            return None

    def get(self, request, group_key: str, item_id: int):
        if not require_admin(request):
            return Response({'detail': 'Admin only.'}, status=403)
        item = self._get_item(group_key, item_id)
        if not item:
            return Response({'detail': 'Not found.'}, status=404)
        data = DropdownItemSerializer(item).data
        data['is_active'] = item.is_active
        data['is_system'] = item.is_system
        return Response(data)

    def patch(self, request, group_key: str, item_id: int):
        if not require_admin(request):
            return Response({'detail': 'Admin only.'}, status=403)
        item = self._get_item(group_key, item_id)
        if not item:
            return Response({'detail': 'Not found.'}, status=404)
        serializer = DropdownUpdateSerializer(instance=item, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                updated = update_dropdown_item(
                    item, serializer.validated_data, changed_by=request.user.id
                )
                return Response(DropdownItemSerializer(updated).data)
            except ValueError as e:
                return Response({'detail': str(e)}, status=400)
        return Response(serializer.errors, status=400)

    def delete(self, request, group_key: str, item_id: int):
        if not require_admin(request):
            return Response({'detail': 'Admin only.'}, status=403)
        item = self._get_item(group_key, item_id)
        if not item:
            return Response({'detail': 'Not found.'}, status=404)
        # ?deactivate=1  -> soft delete (keep in DB, hide from dropdowns)
        # no param       -> hard delete
        deactivate = request.query_params.get('deactivate', '0') == '1'
        try:
            if deactivate:
                deactivate_dropdown_item(item, changed_by=request.user.id)
                return Response({'detail': 'Item deactivated.'})
            else:
                delete_dropdown_item(item, changed_by=request.user.id)
                return Response(status=status.HTTP_204_NO_CONTENT)
        except ValueError as e:
            return Response({'detail': str(e)}, status=400)


# ---------------------------------------------------------------------------
# ADMIN: GET /api/admin/dropdowns/{group_key}/audit-log/
# Audit trail of all admin changes to a dropdown group.
# ---------------------------------------------------------------------------
class AdminDropdownAuditLogView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, group_key: str):
        if not require_admin(request):
            return Response({'detail': 'Admin only.'}, status=403)
        logs = DropdownAuditLog.objects.filter(group_key=group_key).order_by('-changed_at')[:200]
        return Response(DropdownAuditLogSerializer(logs, many=True).data)
