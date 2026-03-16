from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import UserRole, DocumentPermissionOverride
from .serializers import UserRoleSerializer, DocumentPermissionOverrideSerializer
from .services import RBACService
from .permissions import CanManageUsers


class UserRoleViewSet(viewsets.ModelViewSet):
    queryset           = UserRole.objects.select_related('user', 'section', 'document_type')
    serializer_class   = UserRoleSerializer
    permission_classes = [IsAuthenticated, CanManageUsers]

    def get_queryset(self):
        qs     = super().get_queryset()
        user_id = self.request.query_params.get('user')
        if user_id:
            qs = qs.filter(user_id=user_id)
        return qs

    @action(detail=False, methods=['get'], url_path='my-permissions')
    def my_permissions(self, request):
        """GET /rbac/roles/my-permissions/ — return caller's effective permissions."""
        perms = RBACService.get_effective_permissions(request.user)
        roles = RBACService.get_active_roles(request.user)
        return Response({'roles': roles, 'permissions': sorted(perms)})


class DocumentPermissionOverrideViewSet(viewsets.ModelViewSet):
    queryset           = DocumentPermissionOverride.objects.select_related('user', 'document')
    serializer_class   = DocumentPermissionOverrideSerializer
    permission_classes = [IsAuthenticated, CanManageUsers]
