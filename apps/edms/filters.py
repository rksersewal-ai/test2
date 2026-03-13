# =============================================================================
# FILE: apps/edms/filters.py
# SPRINT 1: Added filters for Correspondent, CorrespondentLink, DocumentNote.
# Existing DocumentFilter, RevisionFilter, FileAttachmentFilter unchanged.
# =============================================================================
import django_filters
from apps.edms.models import (
    Document, Revision, FileAttachment,
    Correspondent, DocumentCorrespondentLink, DocumentNote,
)


class DocumentFilter(django_filters.FilterSet):
    status        = django_filters.CharFilter(field_name='status',        lookup_expr='exact')
    category      = django_filters.NumberFilter(field_name='category',    lookup_expr='exact')
    document_type = django_filters.NumberFilter(field_name='document_type', lookup_expr='exact')
    section       = django_filters.NumberFilter(field_name='section',     lookup_expr='exact')
    created_after = django_filters.DateFilter(field_name='created_at',    lookup_expr='gte')
    created_before= django_filters.DateFilter(field_name='created_at',    lookup_expr='lte')

    class Meta:
        model  = Document
        fields = ['status', 'category', 'document_type', 'section']


class RevisionFilter(django_filters.FilterSet):
    document = django_filters.NumberFilter(field_name='document', lookup_expr='exact')
    status   = django_filters.CharFilter(field_name='status',     lookup_expr='exact')

    class Meta:
        model  = Revision
        fields = ['document', 'status']


class FileAttachmentFilter(django_filters.FilterSet):
    revision  = django_filters.NumberFilter(field_name='revision',  lookup_expr='exact')
    file_type = django_filters.CharFilter(field_name='file_type',   lookup_expr='exact')

    class Meta:
        model  = FileAttachment
        fields = ['revision', 'file_type']


# ---- Sprint 1 filters ----

class CorrespondentFilter(django_filters.FilterSet):
    org_type  = django_filters.CharFilter(field_name='org_type',  lookup_expr='exact')
    is_active = django_filters.BooleanFilter(field_name='is_active')

    class Meta:
        model  = Correspondent
        fields = ['org_type', 'is_active']


class DocumentCorrespondentLinkFilter(django_filters.FilterSet):
    document      = django_filters.NumberFilter(field_name='document',      lookup_expr='exact')
    correspondent = django_filters.NumberFilter(field_name='correspondent', lookup_expr='exact')
    link_type     = django_filters.CharFilter(field_name='link_type',       lookup_expr='exact')

    class Meta:
        model  = DocumentCorrespondentLink
        fields = ['document', 'correspondent', 'link_type']


class DocumentNoteFilter(django_filters.FilterSet):
    document    = django_filters.NumberFilter(field_name='document',    lookup_expr='exact')
    revision    = django_filters.NumberFilter(field_name='revision',    lookup_expr='exact')
    note_type   = django_filters.CharFilter(field_name='note_type',     lookup_expr='exact')
    is_resolved = django_filters.BooleanFilter(field_name='is_resolved')

    class Meta:
        model  = DocumentNote
        fields = ['document', 'revision', 'note_type', 'is_resolved']
