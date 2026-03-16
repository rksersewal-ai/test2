from django.urls import path
from .views import (
    BOMTreeListView, BOMTreeDetailView, BOMTreeNodesView,
    BOMReactFlowView, BOMSnapshotListView, BOMNodeCreateView,
    BOMNodeDetailView, BOMNodeMoveView, BOMNodeCanvasView,
    BOMWhereUsedView,
)

urlpatterns = [
    path('trees/',                          BOMTreeListView.as_view()),
    path('trees/<int:pk>/',                 BOMTreeDetailView.as_view()),
    path('trees/<int:pk>/nodes/',           BOMTreeNodesView.as_view()),
    path('trees/<int:pk>/nodes/reactflow/', BOMReactFlowView.as_view()),
    path('trees/<int:pk>/snapshots/',       BOMSnapshotListView.as_view()),
    path('nodes/',                          BOMNodeCreateView.as_view()),
    path('nodes/<int:pk>/',                 BOMNodeDetailView.as_view()),
    path('nodes/<int:pk>/move/',            BOMNodeMoveView.as_view()),
    path('nodes/<int:pk>/canvas/',          BOMNodeCanvasView.as_view()),
    path('where-used/<str:pl_number>/',     BOMWhereUsedView.as_view()),
]
