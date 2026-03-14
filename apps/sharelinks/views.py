# =============================================================================
# FILE: apps/sharelinks/views.py
# SPRINT 7 — ShareLink REST API + public access view
#
# Authenticated endpoints (JWT required):
#   POST   /api/v1/sharelinks/                         create link
#   GET    /api/v1/sharelinks/                         list my links
#   GET    /api/v1/sharelinks/{id}/                    detail
#   POST   /api/v1/sharelinks/{id}/revoke/             revoke
#
# Public endpoints (NO authentication — AllowAny):
#   GET    /s/{token}/                                 view document metadata
#   GET    /s/{token}/download/                        download primary file
#   POST   /s/{token}/verify/                          verify password
# =============================================================================
import mimetypes
from pathlib import Path

from django.http     import FileResponse, Http404
from django.conf     import settings
from django.utils    import timezone
from django.shortcuts import get_object_or_404
from rest_framework  import viewsets, permissions, status, serializers
from rest_framework.decorators import action
from rest_framework.response   import Response

from apps.sharelinks.models   import ShareLink
from apps.sharelinks.services import ShareLinkService
from apps.sharelinks.serializers import (
    ShareLinkSerializer, CreateShareLinkSerializer,
    PublicDocumentSerializer, VerifyPasswordSerializer,
)


# ---------------------------------------------------------------------------
# Authenticated management API
# ---------------------------------------------------------------------------

class ShareLinkViewSet(viewsets.GenericViewSet,
                       viewsets.mixins.ListModelMixin,
                       viewsets.mixins.RetrieveModelMixin,
                       viewsets.mixins.CreateModelMixin):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ShareLink.objects.filter(
            created_by=self.request.user
        ).select_related('document', 'revision', 'created_by', 'revoked_by')

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateShareLinkSerializer
        return ShareLinkSerializer

    def create(self, request, *args, **kwargs):
        ser = CreateShareLinkSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data

        from apps.edms.models import Document, Revision
        doc = get_object_or_404(Document, pk=d['document_id'])
        rev = None
        if d.get('revision_id'):
            rev = get_object_or_404(Revision, pk=d['revision_id'], document=doc)

        link = ShareLinkService.create(
            document        = doc,
            created_by      = request.user,
            revision        = rev,
            access_level    = d.get('access_level', ShareLink.AccessLevel.VIEW_FILE),
            label           = d.get('label', ''),
            expires_in_days = d.get('expires_in_days', 7),
            max_uses        = d.get('max_uses'),
            rate_limit      = d.get('rate_limit_per_hour', 20),
            password        = d.get('password'),
        )
        return Response(ShareLinkSerializer(link).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='revoke')
    def revoke(self, request, pk=None):
        link = self.get_object()
        if not link.is_active:
            return Response({'error': 'Link already revoked.'}, status=400)
        ShareLinkService.revoke(link, revoked_by=request.user)
        return Response(ShareLinkSerializer(link).data)


# ---------------------------------------------------------------------------
# Public access views  (AllowAny — token validates access)
# ---------------------------------------------------------------------------

def _get_valid_link(token: str) -> ShareLink:
    link = get_object_or_404(
        ShareLink.objects.select_related(
            'document', 'document__document_type', 'document__category',
            'revision'
        ),
        token=token
    )
    if not link.is_valid:
        raise Http404('Link has expired or been revoked.')
    return link


def _client_ip(request) -> str:
    xff = request.META.get('HTTP_X_FORWARDED_FOR', '')
    return xff.split(',')[0].strip() if xff else request.META.get('REMOTE_ADDR', '')


class PublicShareView:
    """Class-based view namespace — actual views are standalone functions below."""
    pass


from django.views import View
from django.http  import JsonResponse
import json


class PublicDocumentView(View):
    """GET /s/{token}/ — returns document metadata as JSON."""

    def get(self, request, token):
        link = _get_valid_link(token)
        ip   = _client_ip(request)

        if not ShareLinkService.check_rate_limit(link, ip):
            return JsonResponse(
                {'error': 'Rate limit exceeded. Try again later.'}, status=429
            )
        if link.password_hash:
            # Require password verification first
            if not request.session.get(f'sl_auth_{token}'):
                return JsonResponse(
                    {'error': 'Password required.', 'password_required': True},
                    status=403
                )

        link.record_access(ip, request.META.get('HTTP_USER_AGENT', ''))

        # Get the revision to display
        rev = link.revision
        if not rev:
            rev = (
                link.document.revisions
                .filter(status='CURRENT')
                .order_by('-created_at')
                .first()
            )

        data = {
            'document_number': link.document.document_number,
            'title':           link.document.title,
            'description':     link.document.description,
            'category':        link.document.category.name if link.document.category else None,
            'document_type':   link.document.document_type.name if link.document.document_type else None,
            'status':          link.document.status,
            'revision_number': rev.revision_number if rev else None,
            'revision_date':   str(rev.revision_date) if rev and rev.revision_date else None,
            'access_level':    link.access_level,
            'expires_at':      link.expires_at.isoformat(),
            'can_download':    link.access_level == ShareLink.AccessLevel.VIEW_FILE,
        }
        return JsonResponse(data)


class PublicDownloadView(View):
    """GET /s/{token}/download/ — stream primary PDF file."""

    def get(self, request, token):
        link = _get_valid_link(token)
        if link.access_level != ShareLink.AccessLevel.VIEW_FILE:
            raise Http404('Download not permitted for this link.')

        ip = _client_ip(request)
        if not ShareLinkService.check_rate_limit(link, ip):
            return JsonResponse({'error': 'Rate limit exceeded.'}, status=429)
        if link.password_hash and not request.session.get(f'sl_auth_{token}'):
            return JsonResponse({'error': 'Password required.'}, status=403)

        rev = link.revision
        if not rev:
            rev = (
                link.document.revisions
                .filter(status='CURRENT')
                .order_by('-created_at')
                .first()
            )
        if not rev:
            raise Http404('No current revision available.')

        primary_file = rev.files.filter(is_primary=True).first()
        if not primary_file:
            raise Http404('No primary file attached to this revision.')

        file_path = Path(settings.MEDIA_ROOT) / str(primary_file.file_path)
        if not file_path.exists():
            raise Http404('File not found on server.')

        link.record_access(ip, request.META.get('HTTP_USER_AGENT', ''))

        mime, _ = mimetypes.guess_type(str(file_path))
        return FileResponse(
            open(file_path, 'rb'),
            content_type  = mime or 'application/octet-stream',
            as_attachment = True,
            filename      = primary_file.file_name,
        )


class PublicPasswordVerifyView(View):
    """POST /s/{token}/verify/  {password: '...'}"""

    def post(self, request, token):
        link = _get_valid_link(token)
        try:
            body     = json.loads(request.body)
            password = body.get('password', '')
        except Exception:
            return JsonResponse({'error': 'Invalid JSON.'}, status=400)

        if ShareLinkService.verify_password(link, password):
            request.session[f'sl_auth_{token}'] = True
            return JsonResponse({'status': 'ok'})
        return JsonResponse({'error': 'Incorrect password.'}, status=403)
