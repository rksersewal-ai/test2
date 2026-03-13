# =============================================================================
# FILE: apps/workflow/services.py
# SPRINT 4: ApprovalService added (advance step, record vote, notify).
# All Sprint 1 methods preserved exactly.
# =============================================================================
from django.utils import timezone
from django.db    import transaction

from apps.workflow.models import (
    WorkLedgerEntry, ApprovalChain, ApprovalStep,
    ApprovalRequest, ApprovalVote,
)


class WorkLedgerService:
    @staticmethod
    def log_create(entry: WorkLedgerEntry, user) -> None:
        from apps.audit.services import AuditService
        AuditService.log(
            user=user, action='CREATE', model='WorkLedgerEntry',
            object_id=entry.pk, detail=f'Created: {entry.subject or entry.eoffice_subject}'
        )

    @staticmethod
    def log_update(entry: WorkLedgerEntry, user) -> None:
        from apps.audit.services import AuditService
        AuditService.log(
            user=user, action='UPDATE', model='WorkLedgerEntry',
            object_id=entry.pk, detail=f'Updated status to {entry.status}'
        )


class ApprovalService:
    """
    Encapsulates all state transitions for the Approval Engine.

    Public API:
      initiate(chain, revision, user)          → ApprovalRequest
      cast_vote(request, step, user, vote, comment) → ApprovalVote
      withdraw(request, user)                  → ApprovalRequest
      get_active_step(request)                 → ApprovalStep | None
    """

    # ------------------------------------------------------------------ #

    @classmethod
    @transaction.atomic
    def initiate(
        cls,
        chain:    ApprovalChain,
        revision,
        user,
        remarks:  str = '',
    ) -> ApprovalRequest:
        """
        Start an approval run for `revision` using `chain`.
        Raises ValueError if an active run already exists.
        """
        existing = ApprovalRequest.objects.filter(
            revision=revision, chain=chain,
            status__in=[
                ApprovalRequest.Status.PENDING,
                ApprovalRequest.Status.IN_REVIEW,
            ]
        ).first()
        if existing:
            raise ValueError(
                f'An active approval request (#{existing.pk}) already exists '
                f'for this revision with chain "{chain.name}".',
            )

        first_step = chain.steps.order_by('step_order').first()
        if not first_step:
            raise ValueError(f'Chain "{chain.name}" has no steps defined.')

        req = ApprovalRequest.objects.create(
            chain=chain,
            revision=revision,
            status=ApprovalRequest.Status.IN_REVIEW,
            current_step=first_step.step_order,
            initiated_by=user,
            remarks=remarks,
        )

        cls._notify_step_approver(req, first_step)
        cls._audit('APPROVAL_INITIATE', req, user,
                   f'Initiated chain "{chain.name}" on revision #{revision.pk}')
        return req

    # ------------------------------------------------------------------ #

    @classmethod
    @transaction.atomic
    def cast_vote(
        cls,
        request:  ApprovalRequest,
        step:     ApprovalStep,
        user,
        vote:     str,
        comment:  str = '',
    ) -> ApprovalVote:
        """
        Record an approver's vote on the current step.
        Automatically advances to the next step or closes the request.
        """
        if request.status not in (
            ApprovalRequest.Status.IN_REVIEW,
            ApprovalRequest.Status.PENDING,
        ):
            raise ValueError('Cannot vote on a closed/withdrawn request.')

        if step.step_order != request.current_step:
            raise ValueError(
                f'Step {step.step_order} is not the current active step '
                f'({request.current_step}).'
            )

        v = ApprovalVote.objects.create(
            request=request, step=step,
            voted_by=user, vote=vote, comment=comment,
        )

        if vote == ApprovalVote.Vote.REJECTED:
            request.status       = ApprovalRequest.Status.REJECTED
            request.completed_at = timezone.now()
            request.save(update_fields=['status', 'completed_at'])
            cls._notify_initiator(request, 'APPROVAL_REJECTED')

        elif vote == ApprovalVote.Vote.RETURNED:
            # Return to PENDING so initiator can amend and re-initiate
            request.status = ApprovalRequest.Status.PENDING
            request.save(update_fields=['status'])
            cls._notify_initiator(request, 'APPROVAL_RETURNED')

        elif vote in (ApprovalVote.Vote.APPROVED, ApprovalVote.Vote.DELEGATED):
            next_step = (
                ApprovalStep.objects
                .filter(chain=request.chain, step_order__gt=step.step_order)
                .order_by('step_order')
                .first()
            )
            if next_step:
                request.current_step = next_step.step_order
                request.save(update_fields=['current_step'])
                cls._notify_step_approver(request, next_step)
            else:
                # All steps passed — mark APPROVED
                request.status       = ApprovalRequest.Status.APPROVED
                request.completed_at = timezone.now()
                request.save(update_fields=['status', 'completed_at'])
                cls._notify_initiator(request, 'APPROVAL_APPROVED')
                cls._auto_activate_revision(request)

        cls._audit('APPROVAL_VOTE', request, user,
                   f'Vote={vote} on step {step.step_order} ({step.label})')
        return v

    # ------------------------------------------------------------------ #

    @classmethod
    @transaction.atomic
    def withdraw(cls, request: ApprovalRequest, user) -> ApprovalRequest:
        """Initiator or admin can withdraw a pending/in-review request."""
        if request.status not in (
            ApprovalRequest.Status.PENDING,
            ApprovalRequest.Status.IN_REVIEW,
        ):
            raise ValueError('Can only withdraw PENDING or IN_REVIEW requests.')

        request.status       = ApprovalRequest.Status.WITHDRAWN
        request.completed_at = timezone.now()
        request.save(update_fields=['status', 'completed_at'])
        cls._audit('APPROVAL_WITHDRAW', request, user, 'Request withdrawn.')
        return request

    # ------------------------------------------------------------------ #

    @staticmethod
    def get_active_step(request: ApprovalRequest):
        """Return the current active ApprovalStep, or None if complete."""
        return (
            ApprovalStep.objects
            .filter(chain=request.chain, step_order=request.current_step)
            .first()
        )

    # ------------------------------------------------------------------ private

    @staticmethod
    def _notify_step_approver(request: ApprovalRequest, step: ApprovalStep):
        """Send in-app notification to the step's assigned approver."""
        target_user = step.assigned_user
        if not target_user:
            return
        try:
            from apps.notifications.services import NotificationService
            NotificationService.create(
                user=target_user,
                kind='APPROVAL_REQUESTED',
                title=f'Approval required: {request.revision}',
                body=(
                    f'You are requested to approve step "{step.label}" '
                    f'in chain "{request.chain.name}".'
                ),
                action_url=f'/documents/{request.revision.document_id}/'
                           f'revisions/{request.revision_id}/approval/{request.pk}/',
            )
        except Exception:
            pass  # notification failure must never break approval flow

    @staticmethod
    def _notify_initiator(request: ApprovalRequest, kind: str):
        """Notify the initiator of a terminal approval event."""
        if not request.initiated_by_id:
            return
        try:
            from apps.notifications.services import NotificationService
            label_map = {
                'APPROVAL_APPROVED': 'Approved ✓',
                'APPROVAL_REJECTED': 'Rejected ✗',
                'APPROVAL_RETURNED': 'Returned for Correction',
            }
            label = label_map.get(kind, kind)
            NotificationService.create(
                user=request.initiated_by,
                kind=kind if kind in (
                    'APPROVAL_APPROVED', 'APPROVAL_REJECTED') else 'INFO',
                title=f'Approval {label}: {request.revision}',
                body=f'Request #{request.pk} using chain "{request.chain.name}".',
                action_url=f'/documents/{request.revision.document_id}/',
            )
        except Exception:
            pass

    @staticmethod
    def _auto_activate_revision(request: ApprovalRequest):
        """
        When all steps pass, auto-activate the revision's parent document
        if it is still in DRAFT status.
        """
        try:
            doc = request.revision.document
            if doc.status == 'DRAFT':
                doc.status = 'ACTIVE'
                doc.save(update_fields=['status', 'updated_at'])
        except Exception:
            pass

    @staticmethod
    def _audit(action: str, request: ApprovalRequest, user, detail: str):
        try:
            from apps.audit.services import AuditService
            AuditService.log(
                user=user, action=action,
                model='ApprovalRequest', object_id=request.pk,
                detail=detail,
            )
        except Exception:
            pass
