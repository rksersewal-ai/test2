"""Core API views.

FIX #17: SectionListCreateView now paginates using PageNumberPagination
  (PAGE_SIZE=100 for dropdown use-cases) instead of returning the entire
  Section table in one response, which could be MB of JSON on large deployments.
"""
from rest_framework import generics, permissions
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.core.models import User, Section
from apps.core.serializers import UserSerializer, UserCreateSerializer, SectionSerializer
from apps.core.permissions import IsAdminRole


class SectionDropdownPagination(PageNumberPagination):
    """FIX #17: Paginate section list — prevents huge JSON response on large deployments."""
    page_size            = 100
    page_size_query_param = 'page_size'
    max_page_size        = 500


class CurrentUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class UserListCreateView(generics.ListCreateAPIView):
    queryset           = User.objects.select_related('section').all().order_by('username')
    permission_classes = [IsAdminRole]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserCreateSerializer
        return UserSerializer


class UserDetailView(generics.RetrieveUpdateAPIView):
    queryset           = User.objects.select_related('section').all()
    serializer_class   = UserSerializer
    permission_classes = [IsAdminRole]


class SectionListCreateView(generics.ListCreateAPIView):
    queryset           = Section.objects.filter(is_active=True).order_by('code')
    serializer_class   = SectionSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class   = SectionDropdownPagination   # FIX #17


class SectionDetailView(generics.RetrieveUpdateAPIView):
    # FIX #12 (previous commit): use all_objects so admins can retrieve/reactivate deactivated sections
    queryset           = Section.all_objects.all()
    serializer_class   = SectionSerializer
    permission_classes = [IsAdminRole]
