# =============================================================================
# FILE: apps/lifecycle/services.py
# FR-011: Lifecycle management business logic
# assign_policy, transition_state, place_legal_hold, release_legal_hold,
# archive, schedule_deletion, run_due_reviews (batch scheduler).
# =============================================================================
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from django.db import transaction
from apps.edms.models import Document
from .models import RetentionPolicy, DocumentLifecycle, LifecycleEvent


class LifecycleService:

    @staticmethod
    @transaction.atomic
    def assign_policy(
        document: Document, policy: RetentionPolicy,
        created_date: date = None, user=None
    ) -> DocumentLifecycle:
        """Assign a retention policy to a document and calculate due date."""
        created_date    = created_date or date.today()
        retention_due   = created_date + relativedelta(years=policy.retention_years)
        lifecycle, _    = DocumentLifecycle.objects.update_or_create(
            document=document,
            defaults={
                'policy': policy,
                'state': DocumentLifecycle.LifecycleState.ACTIVE,
                'created_date': created_date,
                'retention_due_date': retention_due,
                'notes': f'Policy assigned by {user}' if user else ''
            }
        )
        return lifecycle

    @staticmethod
    @transaction.atomic
    def _transition(
        document: Document, to_state: str, user=None, reason: str = ''
    ) -> DocumentLifecycle:
        lc = DocumentLifecycle.objects.select_for_update().get(document=document)
        from_state  = lc.state
        lc.state    = to_state
        if to_state == DocumentLifecycle.LifecycleState.ARCHIVED:
            lc.archived_at = timezone.now()
        elif to_state == DocumentLifecycle.LifecycleState.DELETED:
            lc.deleted_at = timezone.now()
            lc.deleted_by = user
        lc.save()
        LifecycleEvent.objects.create(
            document=document,
            from_state=from_state,
            to_state=to_state,
            triggered_by=user,
            reason=reason,
        )
        return lc

    @staticmethod
    def place_legal_hold(document: Document, reason: str, user=None) -> DocumentLifecycle:
        lc = DocumentLifecycle.objects.get(document=document)
        lc.state             = DocumentLifecycle.LifecycleState.LEGAL_HOLD
        lc.legal_hold_reason = reason
        lc.legal_hold_by     = user
        lc.legal_hold_at     = timezone.now()
        lc.save()
        LifecycleEvent.objects.create(
            document=document,
            from_state=DocumentLifecycle.LifecycleState.ACTIVE,
            to_state=DocumentLifecycle.LifecycleState.LEGAL_HOLD,
            triggered_by=user,
            reason=reason,
        )
        return lc

    @staticmethod
    def release_legal_hold(document: Document, user=None, reason: str = '') -> DocumentLifecycle:
        return LifecycleService._transition(
            document, DocumentLifecycle.LifecycleState.ACTIVE, user, reason
        )

    @staticmethod
    def archive(document: Document, user=None, reason: str = '') -> DocumentLifecycle:
        return LifecycleService._transition(
            document, DocumentLifecycle.LifecycleState.ARCHIVED, user, reason
        )

    @staticmethod
    def schedule_deletion(document: Document, user=None, reason: str = '') -> DocumentLifecycle:
        """Moves to PENDING_DEL state. Actual deletion requires explicit confirm_delete."""
        return LifecycleService._transition(
            document, DocumentLifecycle.LifecycleState.PENDING_DEL, user, reason
        )

    @staticmethod
    def confirm_delete(document: Document, user=None, reason: str = '') -> DocumentLifecycle:
        """Permanent deletion marker — actual file purge should be handled separately."""
        lc = DocumentLifecycle.objects.get(document=document)
        if lc.state == DocumentLifecycle.LifecycleState.LEGAL_HOLD:
            raise ValueError('Cannot delete document under legal hold.')
        return LifecycleService._transition(
            document, DocumentLifecycle.LifecycleState.DELETED, user, reason
        )

    @staticmethod
    def run_due_reviews() -> int:
        """Batch task: flag ACTIVE documents past retention_due_date as REVIEW_DUE.
        Returns count of documents flagged."""
        today   = date.today()
        due_lcs = DocumentLifecycle.objects.filter(
            state=DocumentLifecycle.LifecycleState.ACTIVE,
            retention_due_date__lte=today
        ).select_related('document')
        count = 0
        for lc in due_lcs:
            LifecycleService._transition(
                lc.document,
                DocumentLifecycle.LifecycleState.REVIEW_DUE,
                user=None,
                reason='Auto-flagged: retention period elapsed'
            )
            count += 1
        return count
