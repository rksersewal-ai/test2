# =============================================================================
# FILE: tests/test_lifecycle.py
# FR-011: Tests for Document Retention & Lifecycle module
# Covers policy assignment, legal hold, archive, schedule deletion,
# batch run_due_reviews, and deletion block on legal hold.
# =============================================================================
import pytest
from datetime import date, timedelta
from apps.lifecycle.models import RetentionPolicy, DocumentLifecycle, LifecycleEvent
from apps.lifecycle.services import LifecycleService
from tests.factories import UserFactory, DocumentFactory


@pytest.mark.django_db
class TestRetentionPolicyAssignment:

    def test_assign_policy_calculates_due_date(self):
        user    = UserFactory()
        doc     = DocumentFactory()
        policy  = RetentionPolicy.objects.create(
            name='Railways Act 7yr',
            retention_years=7,
            action_after_retention=RetentionPolicy.ActionAfterRetention.ARCHIVE,
            legal_basis='Railways Act 1989'
        )
        created = date(2020, 1, 1)
        lc = LifecycleService.assign_policy(doc, policy, created_date=created, user=user)
        assert lc.retention_due_date == date(2027, 1, 1)
        assert lc.state == DocumentLifecycle.LifecycleState.ACTIVE

    def test_policy_event_not_created_on_assign(self):
        doc    = DocumentFactory()
        policy = RetentionPolicy.objects.create(
            name='5yr Policy', retention_years=5,
            action_after_retention='ARCHIVE'
        )
        LifecycleService.assign_policy(doc, policy, created_date=date.today())
        assert LifecycleEvent.objects.filter(document=doc).count() == 0


@pytest.mark.django_db
class TestLegalHold:

    def test_place_legal_hold(self):
        user   = UserFactory()
        doc    = DocumentFactory()
        policy = RetentionPolicy.objects.create(
            name='Hold Policy', retention_years=3, action_after_retention='ARCHIVE'
        )
        LifecycleService.assign_policy(doc, policy, date.today())
        lc = LifecycleService.place_legal_hold(doc, 'Audit investigation', user)
        assert lc.state == DocumentLifecycle.LifecycleState.LEGAL_HOLD
        assert lc.legal_hold_reason == 'Audit investigation'

    def test_cannot_delete_under_legal_hold(self):
        user   = UserFactory()
        doc    = DocumentFactory()
        policy = RetentionPolicy.objects.create(
            name='Hold P2', retention_years=1, action_after_retention='ARCHIVE'
        )
        LifecycleService.assign_policy(doc, policy, date.today())
        LifecycleService.place_legal_hold(doc, 'Hold', user)
        LifecycleService._transition(doc, DocumentLifecycle.LifecycleState.PENDING_DEL)
        # Manually set state to LEGAL_HOLD to simulate
        lc = DocumentLifecycle.objects.get(document=doc)
        lc.state = DocumentLifecycle.LifecycleState.LEGAL_HOLD
        lc.save()
        with pytest.raises(ValueError, match='legal hold'):
            LifecycleService.confirm_delete(doc, user)

    def test_release_legal_hold(self):
        user   = UserFactory()
        doc    = DocumentFactory()
        policy = RetentionPolicy.objects.create(
            name='Hold P3', retention_years=2, action_after_retention='ARCHIVE'
        )
        LifecycleService.assign_policy(doc, policy, date.today())
        LifecycleService.place_legal_hold(doc, 'Hold', user)
        lc = LifecycleService.release_legal_hold(doc, user)
        assert lc.state == DocumentLifecycle.LifecycleState.ACTIVE


@pytest.mark.django_db
class TestArchiveAndBatchReview:

    def test_archive_document(self):
        user   = UserFactory()
        doc    = DocumentFactory()
        policy = RetentionPolicy.objects.create(
            name='Arch P', retention_years=10, action_after_retention='ARCHIVE'
        )
        LifecycleService.assign_policy(doc, policy, date.today())
        lc = LifecycleService.archive(doc, user, 'Superseded')
        assert lc.state == DocumentLifecycle.LifecycleState.ARCHIVED
        assert lc.archived_at is not None
        event = LifecycleEvent.objects.filter(document=doc, to_state='ARCHIVED').first()
        assert event is not None

    def test_run_due_reviews_flags_overdue(self):
        doc    = DocumentFactory()
        policy = RetentionPolicy.objects.create(
            name='Due P', retention_years=1, action_after_retention='REVIEW'
        )
        past_date = date.today() - timedelta(days=400)
        LifecycleService.assign_policy(doc, policy, created_date=past_date)
        count = LifecycleService.run_due_reviews()
        assert count >= 1
        lc = DocumentLifecycle.objects.get(document=doc)
        assert lc.state == DocumentLifecycle.LifecycleState.REVIEW_DUE
