"""Core API views - users, sections.

BUG FIX #12: SectionDetailView queryset was Section.objects.all().
  After Bug #9 fix (ActiveSectionManager as default), Section.objects only
  returns is_active=True records. This meant admin attempts to retrieve or
  update a deactivated section via GET/PATCH /api/core/sections/{id}/ would
  return 404 silently.
  Fixed: use Section.all_objects.all() for the admin detail view so
  deactivated sections remain accessible to admins for reactivation/editing.
"""
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.core.models import User, Section
from apps.core.serializers import UserSerializer, UserCreateSerializer, SectionSerializer
from apps.core.permissions import IsAdminRole


class CurrentUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class UserListCreateView(generics.ListCreateAPIView):
    queryset = User.objects.select_related('section').all().order_by('username')
    permission_classes = [IsAdminRole]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserCreateSerializer
        return UserSerializer


class UserDetailView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.select_related('section').all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminRole]


class SectionListCreateView(generics.ListCreateAPIView):
    # Active-only list for dropdowns and general use
    queryset = Section.objects.filter(is_active=True).order_by('code')
    serializer_class = SectionSerializer
    permission_classes = [permissions.IsAuthenticated]


class SectionDetailView(generics.RetrieveUpdateAPIView):
    # BUG FIX #12: use all_objects so admins can retrieve/reactivate
    # deactivated sections — Section.objects only returns is_active=True
    queryset = Section.all_objects.all()
    serializer_class = SectionSerializer
    permission_classes = [IsAdminRole]
