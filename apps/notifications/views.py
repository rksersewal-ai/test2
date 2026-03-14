# =============================================================================
# FILE: apps/notifications/views.py
# SPRINT 4 — Notification API endpoints
#
# GET  /api/notifications/              — list (paginated, newest first)
# GET  /api/notifications/unread-count/ — {count: N}
# POST /api/notifications/{id}/read/    — mark one read
# POST /api/notifications/read-all/     — mark all read
# GET  /api/notifications/stream/       — SSE endpoint (long-poll fallback)
# =============================================================================
import json
import time
from django.http  import StreamingHttpResponse
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.notifications.models     import Notification
from apps.notifications.serializers import NotificationSerializer
from apps.notifications.services    import NotificationService


class NotificationViewSet(viewsets.GenericViewSet,
                          viewsets.mixins.ListModelMixin,
                          viewsets.mixins.RetrieveModelMixin):
    serializer_class   = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Notification.objects.filter(user=self.request.user)
        if self.request.query_params.get('unread') == 'true':
            qs = qs.filter(is_read=False)
        return qs[:100]  # cap at 100 for list

    @action(detail=False, methods=['get'], url_path='unread-count')
    def unread_count(self, request):
        return Response({'count': NotificationService.unread_count(request.user)})

    @action(detail=True, methods=['post'], url_path='read')
    def mark_read(self, request, pk=None):
        found = NotificationService.mark_read(pk, request.user)
        if not found:
            return Response({'error': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'read': True})

    @action(detail=False, methods=['post'], url_path='read-all')
    def mark_all_read(self, request):
        count = NotificationService.mark_all_read(request.user)
        return Response({'marked_read': count})

    @action(detail=False, methods=['get'], url_path='stream')
    def stream(self, request):
        """
        Server-Sent Events stream.
        Client connects once; server pushes {count, items} every 15 seconds.
        Runs for max 4 minutes (16 cycles) to avoid long-lived connections
        on a LAN deployment without load-balancing keep-alive.

        Frontend usage:
          const es = new EventSource('/api/notifications/stream/');
          es.onmessage = e => setNotifs(JSON.parse(e.data));
        """
        user = request.user

        def event_generator():
            for _ in range(16):   # 16 × 15s = 4 min max
                qs    = Notification.objects.filter(user=user, is_read=False)\
                            .order_by('-created_at')[:10]
                items = NotificationSerializer(qs, many=True).data
                payload = json.dumps({'count': len(items), 'items': list(items)})
                yield f'data: {payload}\n\n'
                time.sleep(15)
            yield 'data: {"eof": true}\n\n'

        resp = StreamingHttpResponse(
            event_generator(),
            content_type='text/event-stream',
        )
        resp['Cache-Control'] = 'no-cache'
        resp['X-Accel-Buffering'] = 'no'   # nginx: disable buffering
        return resp
