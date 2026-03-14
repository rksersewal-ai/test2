# =============================================================================
# FILE: apps/work_ledger/signals.py
# Auto-resolve linked_pl_number from reference_number when creating a WorkEntry
# =============================================================================
from django.db.models.signals import pre_save
from django.dispatch          import receiver
from .models import WorkEntry, WorkType


@receiver(pre_save, sender=WorkEntry)
def auto_link_pl_master(sender, instance, **kwargs):
    """
    If work_type is PL_ENTRY or reference_number looks like a PL number
    and linked_pl_number is not yet set, try to resolve it.
    """
    if instance.linked_pl_number_id:
        return  # Already set, skip

    ref = (instance.reference_number or '').strip()
    if not ref:
        return

    # Only attempt auto-link for PL-related work types
    pl_work_types = {
        WorkType.PL_ENTRY,
        WorkType.DRAWING_PROCESSING,
        WorkType.SPEC_PROCESSING,
        WorkType.SMI_IMPLEMENTATION,
    }
    if instance.work_type not in pl_work_types:
        return

    try:
        from apps.pl_master.models import PLMaster
        pl = PLMaster.objects.filter(pl_number__iexact=ref, is_active=True).first()
        if pl:
            instance.linked_pl_number = pl
    except Exception:
        pass  # Never fail a save due to signal issues
