from django_filters import rest_framework as df
from apps.audit.models import AuditLog


class AuditLogFilter(df.FilterSet):
    module  = df.MultipleChoiceFilter(choices=AuditLog.Module.choices, conjoined=False)
    action  = df.CharFilter(lookup_expr='icontains')
    username = df.CharFilter(lookup_expr='icontains')
    entity_type = df.CharFilter(lookup_expr='iexact')
    entity_id   = df.NumberFilter()
    success     = df.BooleanFilter()
    from_ts = df.DateTimeFilter(field_name='timestamp', lookup_expr='gte')
    to_ts   = df.DateTimeFilter(field_name='timestamp', lookup_expr='lte')

    class Meta:
        model  = AuditLog
        fields = ['module', 'action', 'username', 'entity_type', 'entity_id', 'success']
