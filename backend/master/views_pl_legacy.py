# =============================================================================
# FILE: backend/master/views_pl_legacy.py
# LEGACY READ-ONLY VIEWS for Drawings, Specifications, Alteration History,
# Controlling Agencies — these are served from the PLMaster module's existing
# models (Drawing, Specification, AlterationHistory) in the config_mgmt app
# or similar. Until those models are confirmed, these views return the data
# from the relevant source or a helpful empty response.
#
# The frontend's plMasterService.ts calls these endpoints; they must exist
# and return {results: [], total_count: 0} to avoid 404 crashes.
# =============================================================================
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.db.models import Q

logger = logging.getLogger('edms.pl_legacy')


class PLDrawingsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Try to load from config_mgmt Drawing model if it exists
        try:
            from django.apps import apps
            Drawing = apps.get_model('config_mgmt', 'Drawing')
            q    = request.query_params.get('q', '')
            dtype= request.query_params.get('drawing_type', '')
            page = int(request.query_params.get('page', 1))
            size = int(request.query_params.get('page_size', 20))
            qs   = Drawing.objects.all()
            if q:     qs = qs.filter(Q(drawing_number__icontains=q)|Q(drawing_title__icontains=q))
            if dtype: qs = qs.filter(drawing_type=dtype)
            total  = qs.count()
            start  = (page-1)*size
            results= list(qs.values()[start:start+size])
            return Response({'total_count':total,'results':results})
        except Exception:
            return Response({'total_count':0,'results':[]})


class PLSpecificationsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            from django.apps import apps
            Spec = apps.get_model('config_mgmt', 'Specification')
            q    = request.query_params.get('q', '')
            stype= request.query_params.get('spec_type', '')
            page = int(request.query_params.get('page', 1))
            size = int(request.query_params.get('page_size', 20))
            qs   = Spec.objects.all()
            if q:     qs = qs.filter(Q(spec_number__icontains=q)|Q(spec_title__icontains=q))
            if stype: qs = qs.filter(spec_type=stype)
            total  = qs.count()
            start  = (page-1)*size
            results= list(qs.values()[start:start+size])
            return Response({'total_count':total,'results':results})
        except Exception:
            return Response({'total_count':0,'results':[]})


class PLAlterationHistoryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            from django.apps import apps
            Alt  = apps.get_model('config_mgmt', 'AlterationHistory')
            q    = request.query_params.get('document_number', '')
            dtype= request.query_params.get('document_type', '')
            page = int(request.query_params.get('page', 1))
            size = int(request.query_params.get('page_size', 20))
            qs   = Alt.objects.all()
            if q:     qs = qs.filter(document_number__icontains=q)
            if dtype: qs = qs.filter(document_type=dtype)
            total  = qs.count()
            start  = (page-1)*size
            results= list(qs.values()[start:start+size])
            return Response({'total_count':total,'results':results})
        except Exception:
            return Response({'total_count':0,'results':[]})


class PLAgenciesView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            from django.apps import apps
            Agency = apps.get_model('config_mgmt', 'ControllingAgency')
            return Response(list(Agency.objects.values('id','name','code')))
        except Exception:
            return Response([])
