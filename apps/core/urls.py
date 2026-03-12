from django.urls import path
from apps.core.views import (
    CurrentUserView, UserListCreateView, UserDetailView,
    SectionListCreateView, SectionDetailView,
)

urlpatterns = [
    path('me/', CurrentUserView.as_view(), name='auth-me'),
    path('users/', UserListCreateView.as_view(), name='user-list-create'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('sections/', SectionListCreateView.as_view(), name='section-list-create'),
    path('sections/<int:pk>/', SectionDetailView.as_view(), name='section-detail'),
]
