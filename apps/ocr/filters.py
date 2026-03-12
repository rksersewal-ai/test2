from django_filters import rest_framework as df
from apps.ocr.models import OCRQueue


class OCRQueueFilter(df.FilterSet):
    status = df.MultipleChoiceFilter(
        choices=OCRQueue.Status.choices,
        conjoined=False,
    )
    priority = df.NumberFilter()
    queued_after = df.DateTimeFilter(field_name='queued_at', lookup_expr='gte')
    queued_before = df.DateTimeFilter(field_name='queued_at', lookup_expr='lte')

    class Meta:
        model = OCRQueue
        fields = ['status', 'priority']
