# =============================================================================
# FILE: apps/sanity/checks.py
# SPRINT 6 — Document Sanity Checker
#
# Checks run in order. Each check returns a list of SanityIssue dicts:
#   { code, severity, message, document_id, document_number, detail }
#
# Severity levels:
#   ERROR   — data integrity problem (duplicate hash, no primary file)
#   WARNING — policy violation (draft too old, missing category)
#   INFO    — advisory (missing keywords, no correspondents)
#
# Entry point: run_all_checks() → list[dict]
# Also exposed individually for targeted use.
# =============================================================================
import logging
from datetime import timedelta
from typing   import List, Dict, Any

from django.utils import timezone

log = logging.getLogger('sanity')

Issue = Dict[str, Any]   # type alias


def _issue(
    code:            str,
    severity:        str,
    message:         str,
    document_id:     int  = None,
    document_number: str  = '',
    detail:          str  = '',
) -> Issue:
    return {
        'code':            code,
        'severity':        severity,
        'message':         message,
        'document_id':     document_id,
        'document_number': document_number,
        'detail':          detail,
    }


# ---------------------------------------------------------------------------
# CHECK 1: Duplicate file checksums
# ---------------------------------------------------------------------------

def check_duplicate_files() -> List[Issue]:
    """
    Find FileAttachment rows sharing the same checksum_sha256.
    Indicates the same physical file was uploaded under different documents
    or revisions — possible duplicate document problem.
    """
    from django.db.models import Count
    from apps.edms.models import FileAttachment

    issues = []
    dupes  = (
        FileAttachment.objects
        .exclude(checksum_sha256='')
        .values('checksum_sha256')
        .annotate(cnt=Count('id'))
        .filter(cnt__gt=1)
    )
    for row in dupes:
        sha = row['checksum_sha256']
        files = (
            FileAttachment.objects
            .filter(checksum_sha256=sha)
            .select_related('revision__document')
        )
        doc_nums = ', '.join(
            f.revision.document.document_number for f in files
        )
        issues.append(_issue(
            code='DUPLICATE_FILE_HASH',
            severity='ERROR',
            message=f'Duplicate file hash {sha[:12]}… found in {row["cnt"]} attachments',
            detail=f'Documents: {doc_nums}',
        ))
    return issues


# ---------------------------------------------------------------------------
# CHECK 2: Documents with no CURRENT revision
# ---------------------------------------------------------------------------

def check_no_current_revision() -> List[Issue]:
    """
    ACTIVE documents that have no revision with status=CURRENT.
    Indicates a data entry gap.
    """
    from apps.edms.models import Document, Revision

    docs_with_current = (
        Revision.objects
        .filter(status=Revision.Status.CURRENT)
        .values_list('document_id', flat=True)
    )
    issues = []
    for doc in Document.objects.filter(
        status=Document.Status.ACTIVE
    ).exclude(pk__in=docs_with_current):
        issues.append(_issue(
            code='NO_CURRENT_REVISION',
            severity='ERROR',
            message=f'{doc.document_number} has no CURRENT revision',
            document_id=doc.pk,
            document_number=doc.document_number,
        ))
    return issues


# ---------------------------------------------------------------------------
# CHECK 3: Revisions with no primary file attachment
# ---------------------------------------------------------------------------

def check_missing_primary_file() -> List[Issue]:
    """
    CURRENT revisions that have zero FileAttachment rows where is_primary=True.
    """
    from apps.edms.models import Revision, FileAttachment

    revs_with_primary = (
        FileAttachment.objects
        .filter(is_primary=True)
        .values_list('revision_id', flat=True)
    )
    issues = []
    for rev in Revision.objects.filter(
        status=Revision.Status.CURRENT
    ).select_related('document').exclude(pk__in=revs_with_primary):
        issues.append(_issue(
            code='MISSING_PRIMARY_FILE',
            severity='ERROR',
            message=(
                f'{rev.document.document_number} Rev {rev.revision_number} '
                f'has no primary file attachment'
            ),
            document_id=rev.document_id,
            document_number=rev.document.document_number,
            detail=f'Revision #{rev.pk}',
        ))
    return issues


# ---------------------------------------------------------------------------
# CHECK 4: DRAFT documents older than threshold
# ---------------------------------------------------------------------------

def check_stale_drafts(max_days: int = 90) -> List[Issue]:
    """
    Documents that have been in DRAFT status for more than max_days.
    Default threshold: 90 days.
    """
    from apps.edms.models import Document

    cutoff = timezone.now() - timedelta(days=max_days)
    issues = []
    for doc in Document.objects.filter(
        status=Document.Status.DRAFT,
        created_at__lt=cutoff,
    ):
        age = (timezone.now() - doc.created_at).days
        issues.append(_issue(
            code='STALE_DRAFT',
            severity='WARNING',
            message=f'{doc.document_number} has been DRAFT for {age} days',
            document_id=doc.pk,
            document_number=doc.document_number,
            detail=f'Created: {doc.created_at.date()}. Threshold: {max_days} days.',
        ))
    return issues


# ---------------------------------------------------------------------------
# CHECK 5: Documents missing category or document_type
# ---------------------------------------------------------------------------

def check_missing_classification() -> List[Issue]:
    """
    ACTIVE/DRAFT documents with null category or null document_type.
    """
    from apps.edms.models import Document

    issues = []
    for doc in Document.objects.filter(
        status__in=[Document.Status.ACTIVE, Document.Status.DRAFT],
    ).filter(
        models_q=None,   # placeholder — see actual query below
    ):
        pass   # overridden below

    # Correct query
    from django.db.models import Q
    for doc in Document.objects.filter(
        status__in=[Document.Status.ACTIVE, Document.Status.DRAFT],
    ).filter(Q(category__isnull=True) | Q(document_type__isnull=True)):
        missing = []
        if not doc.category_id:     missing.append('Category')
        if not doc.document_type_id: missing.append('Document Type')
        issues.append(_issue(
            code='MISSING_CLASSIFICATION',
            severity='WARNING',
            message=f'{doc.document_number} missing: {" and ".join(missing)}',
            document_id=doc.pk,
            document_number=doc.document_number,
        ))
    return issues


# ---------------------------------------------------------------------------
# CHECK 6: Documents with no correspondent links
# ---------------------------------------------------------------------------

def check_no_correspondents() -> List[Issue]:
    """ACTIVE documents with no correspondent links at all."""
    from apps.edms.models import Document, DocumentCorrespondentLink

    docs_with_corr = (
        DocumentCorrespondentLink.objects
        .values_list('document_id', flat=True)
        .distinct()
    )
    issues = []
    for doc in Document.objects.filter(
        status=Document.Status.ACTIVE
    ).exclude(pk__in=docs_with_corr):
        issues.append(_issue(
            code='NO_CORRESPONDENT',
            severity='INFO',
            message=f'{doc.document_number} has no correspondent organisation linked',
            document_id=doc.pk,
            document_number=doc.document_number,
        ))
    return issues


# ---------------------------------------------------------------------------
# CHECK 7: Overdue work ledger entries
# ---------------------------------------------------------------------------

def check_overdue_work_entries() -> List[Issue]:
    """WorkLedgerEntries past target_date with OPEN or IN_PROGRESS status."""
    from apps.workflow.models import WorkLedgerEntry

    today  = timezone.now().date()
    issues = []
    for entry in WorkLedgerEntry.objects.filter(
        target_date__lt=today,
        status__in=['OPEN', 'IN_PROGRESS'],
    ).select_related('assigned_to'):
        assignee = (
            entry.assigned_to.get_full_name()
            if entry.assigned_to else 'Unassigned'
        )
        issues.append(_issue(
            code='OVERDUE_WORK_ENTRY',
            severity='WARNING',
            message=(
                f'Work entry #{entry.pk} “{entry.subject or entry.eoffice_subject}” '
                f'overdue by {(today - entry.target_date).days} day(s)'
            ),
            detail=f'Assignee: {assignee}. Target: {entry.target_date}.',
        ))
    return issues


# ---------------------------------------------------------------------------
# CHECK 8: Duplicate document numbers (safety net)
# ---------------------------------------------------------------------------

def check_duplicate_document_numbers() -> List[Issue]:
    """
    Should be impossible due to DB unique constraint but verifies integrity.
    """
    from django.db.models import Count
    from apps.edms.models import Document

    issues = []
    dupes  = (
        Document.objects
        .values('document_number')
        .annotate(cnt=Count('id'))
        .filter(cnt__gt=1)
    )
    for row in dupes:
        issues.append(_issue(
            code='DUPLICATE_DOC_NUMBER',
            severity='ERROR',
            message=f'Duplicate document_number: {row["document_number"]} ({row["cnt"]} rows)',
            document_number=row['document_number'],
        ))
    return issues


# ---------------------------------------------------------------------------
# Master runner
# ---------------------------------------------------------------------------

CHECKS = [
    check_duplicate_document_numbers,
    check_duplicate_files,
    check_no_current_revision,
    check_missing_primary_file,
    check_stale_drafts,
    check_missing_classification,
    check_no_correspondents,
    check_overdue_work_entries,
]


def run_all_checks(stale_draft_days: int = 90) -> List[Issue]:
    """
    Run all sanity checks. Returns combined list sorted by severity.
    Severity order: ERROR > WARNING > INFO.
    """
    SEV_ORDER = {'ERROR': 0, 'WARNING': 1, 'INFO': 2}
    all_issues = []

    for check_fn in CHECKS:
        try:
            if check_fn == check_stale_drafts:
                issues = check_fn(max_days=stale_draft_days)
            else:
                issues = check_fn()
            all_issues.extend(issues)
        except Exception as e:
            log.error(f'[Sanity] Check {check_fn.__name__} failed: {e}')

    all_issues.sort(key=lambda x: SEV_ORDER.get(x['severity'], 9))
    return all_issues
