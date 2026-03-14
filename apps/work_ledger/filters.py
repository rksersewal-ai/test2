# =============================================================================
# FILE: apps/work_ledger/filters.py
# =============================================================================
import django_filters
from .models import WorkEntry, WorkStatus, WorkType


class WorkEntryFilter(django_filters.FilterSet):
    work_date_gte   = django_filters.DateFilter(field_name='work_date', lookup_expr='gte')
    work_date_lte   = django_filters.DateFilter(field_name='work_date', lookup_expr='lte')
    user            = django_filters.NumberFilter(field_name='user__id')
    status          = django_filters.ChoiceFilter(choices=WorkStatus.choices)
    work_type       = django_filters.ChoiceFilter(choices=WorkType.choices)
    reference_number = django_filters.CharFilter(lookup_expr='icontains')
    linked_pl       = django_filters.CharFilter(
        field_name='linked_pl_number__pl_number', lookup_expr='icontains'
    )

    class Meta:
        model  = WorkEntry
        fields = [
            'work_date_gte', 'work_date_lte',
            'user', 'status', 'work_type',
            'reference_number', 'linked_pl',
            'category',
        ]
