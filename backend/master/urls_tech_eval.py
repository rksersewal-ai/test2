# =============================================================================
# FILE: backend/master/urls_tech_eval.py
# URL patterns for Technical Evaluation Documents — included in main urls.py
#
# Include this in config/urls.py (or edms/urls.py) as:
#   path('api/v1/pl-master/', include('master.urls_tech_eval')),
#
# Routes added:
#   GET  /api/v1/pl-master/{pl_number}/tech-eval-docs/
#   POST /api/v1/pl-master/{pl_number}/tech-eval-docs/
#   DELETE /api/v1/pl-master/{pl_number}/tech-eval-docs/{pk}/
# =============================================================================
from django.urls import path
from .views_tech_eval import PLTechEvalDocListView, PLTechEvalDocDetailView

urlpatterns = [
    path(
        '<str:pl_number>/tech-eval-docs/',
        PLTechEvalDocListView.as_view(),
        name='pl-tech-eval-doc-list',
    ),
    path(
        '<str:pl_number>/tech-eval-docs/<int:pk>/',
        PLTechEvalDocDetailView.as_view(),
        name='pl-tech-eval-doc-detail',
    ),
]
