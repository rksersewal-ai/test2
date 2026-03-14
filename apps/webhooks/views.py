# =============================================================================
# FILE: apps/webhooks/views.py
# SPRINT 7 — Webhook management API
#
# GET/POST/PATCH/DELETE  /api/v1/webhooks/endpoints/
# GET                    /api/v1/webhooks/endpoints/{id}/deliveries/
# POST                   /api/v1/webhooks/endpoints/{id}/test/
#                          (sends a test ping event to the endpoint)
# GET                    /api/v1/webhooks/deliveries/
# GET                    /api/v1/webhooks/events/  (list all known event names)
# =============================================================================
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response   import Response

from apps.webhooks.models      import WebhookEndpoint, WebhookDelivery
from apps.webhooks.serializers import WebhookEndpointSerializer, WebhookDeliverySerializer
from apps.core.permissions     import IsAdminOrSectionHead


class WebhookEndpointViewSet(viewsets.ModelViewSet):
    serializer_class   = WebhookEndpointSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSectionHead]

    def get_queryset(self):
        return WebhookEndpoint.objects.select_related('created_by').all()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['get'], url_path='deliveries')
    def deliveries(self, request, pk=None):
        ep   = self.get_object()
        qs   = ep.deliveries.order_by('-created_at')[:100]
        data = WebhookDeliverySerializer(qs, many=True).data
        return Response(data)

    @action(detail=True, methods=['post'], url_path='test')
    def test(self, request, pk=None):
        """Send a test.ping event to verify endpoint connectivity."""
        ep = self.get_object()
        from apps.webhooks.models import WebhookDelivery
        from apps.webhooks.tasks  import deliver_webhook
        delivery = WebhookDelivery.objects.create(
            endpoint   = ep,
            event_name = 'test.ping',
            payload    = {'message': 'Test ping from PLW EDMS', 'endpoint_id': ep.pk},
        )
        deliver_webhook.delay(delivery.pk)
        return Response(
            {'status': 'queued', 'delivery_id': delivery.pk},
            status=status.HTTP_202_ACCEPTED
        )

    @action(detail=False, methods=['get'], url_path='events')
    def events(self, request):
        """List all built-in event names."""
        return Response({'events': WebhookEndpoint.BUILTIN_EVENTS})


class WebhookDeliveryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class   = WebhookDeliverySerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSectionHead]

    def get_queryset(self):
        qs = WebhookDelivery.objects.select_related('endpoint').all()
        ep = self.request.query_params.get('endpoint')
        ev = self.request.query_params.get('event')
        st = self.request.query_params.get('status')
        if ep: qs = qs.filter(endpoint_id=ep)
        if ev: qs = qs.filter(event_name=ev)
        if st: qs = qs.filter(status=st)
        return qs
