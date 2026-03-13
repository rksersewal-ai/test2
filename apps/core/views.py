"""Core API views - users, sections."""
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
    queryset = Section.objects.filter(is_active=True).order_by('code')
    serializer_class = SectionSerializer
    permission_classes = [permissions.IsAuthenticated]


class SectionDetailView(generics.RetrieveUpdateAPIView):
    queryset = Section.objects.all()
    serializer_class = SectionSerializer
    permission_classes = [IsAdminRole]
