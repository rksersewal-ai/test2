"""DRF / django-filter FilterSets for the EDMS app."""
from django_filters import rest_framework as df
from apps.edms.models import Document, Revision, FileAttachment


class DocumentFilter(df.FilterSet):
    status = df.MultipleChoiceFilter(
        choices=Document.Status.choices,
        conjoined=False,
    )
    category = df.NumberFilter(field_name='category__id')
    section = df.NumberFilter(field_name='section__id')
    document_type = df.NumberFilter(field_name='document_type__id')
    source_standard = df.CharFilter(field_name='source_standard', lookup_expr='icontains')
    created_after = df.DateFilter(field_name='created_at', lookup_expr='date__gte')
    created_before = df.DateFilter(field_name='created_at', lookup_expr='date__lte')
    updated_after = df.DateFilter(field_name='updated_at', lookup_expr='date__gte')
    keywords = df.CharFilter(field_name='keywords', lookup_expr='icontains')
    eoffice_file_number = df.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Document
        fields = [
            'status', 'category', 'section', 'document_type',
            'source_standard', 'created_after', 'created_before',
            'updated_after', 'keywords', 'eoffice_file_number',
        ]


class RevisionFilter(df.FilterSet):
    document = df.NumberFilter(field_name='document__id')
    status = df.MultipleChoiceFilter(
        choices=Revision.Status.choices,
        conjoined=False,
    )
    revision_date_after = df.DateFilter(field_name='revision_date', lookup_expr='gte')
    revision_date_before = df.DateFilter(field_name='revision_date', lookup_expr='lte')
    has_files = df.BooleanFilter(method='filter_has_files')

    class Meta:
        model = Revision
        fields = ['document', 'status', 'revision_date_after', 'revision_date_before']

    def filter_has_files(self, queryset, name, value):
        if value:
            return queryset.filter(files__isnull=False).distinct()
        return queryset.filter(files__isnull=True)


class FileAttachmentFilter(df.FilterSet):
    revision = df.NumberFilter(field_name='revision__id')
    ocr_status = df.MultipleChoiceFilter(
        choices=FileAttachment.OCRStatus.choices,
        conjoined=False,
    )

    class Meta:
        model = FileAttachment
        fields = ['revision', 'ocr_status']
