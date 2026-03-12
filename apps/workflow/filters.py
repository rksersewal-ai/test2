from django_filters import rest_framework as df
from apps.workflow.models import WorkLedgerEntry


class WorkLedgerFilter(df.FilterSet):
    status = df.MultipleChoiceFilter(
        choices=WorkLedgerEntry.Status.choices,
        conjoined=False,
    )
    section = df.NumberFilter(field_name='section__id')
    assigned_to = df.NumberFilter(field_name='assigned_to__id')
    work_type = df.NumberFilter(field_name='work_type__id')
    eoffice_file_number = df.CharFilter(lookup_expr='icontains')
    received_after = df.DateFilter(field_name='received_date', lookup_expr='gte')
    received_before = df.DateFilter(field_name='received_date', lookup_expr='lte')
    target_before = df.DateFilter(field_name='target_date', lookup_expr='lte')
    overdue = df.BooleanFilter(method='filter_overdue')

    class Meta:
        model = WorkLedgerEntry
        fields = ['status', 'section', 'assigned_to', 'work_type', 'eoffice_file_number']

    def filter_overdue(self, queryset, name, value):
        from django.utils import timezone
        if value:
            return queryset.filter(
                target_date__lt=timezone.now().date()
            ).exclude(status=WorkLedgerEntry.Status.CLOSED)
        return queryset
