# =============================================================================
# FILE: apps/pl_master/signals.py
#
# AUTO-TRIGGERS:
#   1. DrawingMaster.current_alteration change  → AlterationHistory record
#   2. SpecificationMaster.current_alteration change → AlterationHistory record
#
# APPROACH:
#   - pre_save  : capture old value from DB (before save)
#   - post_save : compare with new value; create AlterationHistory if changed
# =============================================================================
from django.db.models.signals import pre_save, post_save
from django.dispatch          import receiver

# ---- cache key for pre-save state -----------------------------------------
_ALTERATION_CACHE = {}


# ===========================================================================
# DrawingMaster signals
# ===========================================================================
@receiver(pre_save, sender='pl_master.DrawingMaster')
def drawing_pre_save(sender, instance, **kwargs):
    """
    Before saving a DrawingMaster, capture the current (old) alteration
    from the database so we can compare after save.
    """
    if not instance.pk:
        return  # New record — nothing to compare
    try:
        old = sender.objects.only('current_alteration', 'drawing_number').get(pk=instance.pk)
        _ALTERATION_CACHE[f'DRW_{instance.pk}'] = old.current_alteration
    except sender.DoesNotExist:
        pass


@receiver(post_save, sender='pl_master.DrawingMaster')
def drawing_post_save(sender, instance, created, **kwargs):
    """
    After saving a DrawingMaster:
    - If newly created: record initial alteration (Alt 00) in history
    - If updated and current_alteration changed: record new alteration
    """
    if created:
        _create_alteration_history(
            document_type    = 'DRAWING',
            document_number  = instance.drawing_number,
            alteration_number= instance.current_alteration or '00',
            previous_alteration = None,
            alteration_date  = instance.alteration_date,
            changes_description = instance.alteration_description or 'Initial entry',
            probable_impacts = getattr(instance, 'probable_impacts', ''),
            source_agency    = instance.controlling_agency,
        )
        return

    cache_key = f'DRW_{instance.pk}'
    old_alt   = _ALTERATION_CACHE.pop(cache_key, None)
    new_alt   = instance.current_alteration

    if old_alt is None or old_alt == new_alt:
        return  # No change in alteration — skip

    _create_alteration_history(
        document_type    = 'DRAWING',
        document_number  = instance.drawing_number,
        alteration_number= new_alt,
        previous_alteration = old_alt,
        alteration_date  = instance.alteration_date,
        changes_description = instance.alteration_description or f'Alteration changed {old_alt} → {new_alt}',
        probable_impacts = getattr(instance, 'probable_impacts', ''),
        source_agency    = instance.controlling_agency,
    )


# ===========================================================================
# SpecificationMaster signals
# ===========================================================================
@receiver(pre_save, sender='pl_master.SpecificationMaster')
def spec_pre_save(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        old = sender.objects.only('current_alteration', 'spec_number').get(pk=instance.pk)
        _ALTERATION_CACHE[f'SPEC_{instance.pk}'] = old.current_alteration
    except sender.DoesNotExist:
        pass


@receiver(post_save, sender='pl_master.SpecificationMaster')
def spec_post_save(sender, instance, created, **kwargs):
    if created:
        _create_alteration_history(
            document_type    = 'SPEC',
            document_number  = instance.spec_number,
            alteration_number= instance.current_alteration or '00',
            previous_alteration = None,
            alteration_date  = instance.alteration_date,
            changes_description = instance.alteration_description or 'Initial entry',
            probable_impacts = getattr(instance, 'probable_impacts', ''),
            source_agency    = instance.controlling_agency,
        )
        return

    cache_key = f'SPEC_{instance.pk}'
    old_alt   = _ALTERATION_CACHE.pop(cache_key, None)
    new_alt   = instance.current_alteration

    if old_alt is None or old_alt == new_alt:
        return

    _create_alteration_history(
        document_type    = 'SPEC',
        document_number  = instance.spec_number,
        alteration_number= new_alt,
        previous_alteration = old_alt,
        alteration_date  = instance.alteration_date,
        changes_description = instance.alteration_description or f'Alteration changed {old_alt} → {new_alt}',
        probable_impacts = getattr(instance, 'probable_impacts', ''),
        source_agency    = instance.controlling_agency,
    )


# ===========================================================================
# Helper: create AlterationHistory record
# ===========================================================================
def _create_alteration_history(
    document_type, document_number, alteration_number,
    previous_alteration, alteration_date,
    changes_description, probable_impacts, source_agency,
):
    """
    Safely create an AlterationHistory record.
    Never raises — errors are swallowed to not break the parent save.
    """
    try:
        from apps.pl_master.models import AlterationHistory
        from django.utils import timezone

        # Resolve affected PL numbers from the drawing/spec
        affected_pl = []
        if document_type == 'DRAWING':
            from apps.pl_master.models import PLDrawingLink
            affected_pl = list(
                PLDrawingLink.objects.filter(
                    drawing__drawing_number=document_number
                ).values_list('pl_master__pl_number', flat=True)
            )
        elif document_type == 'SPEC':
            from apps.pl_master.models import PLSpecLink
            affected_pl = list(
                PLSpecLink.objects.filter(
                    specification__spec_number=document_number
                ).values_list('pl_master__pl_number', flat=True)
            )

        AlterationHistory.objects.create(
            document_type       = document_type,
            document_number     = document_number,
            alteration_number   = alteration_number or '00',
            previous_alteration = previous_alteration or '',
            alteration_date     = alteration_date or timezone.now().date(),
            changes_description = changes_description or '',
            probable_impacts    = probable_impacts or '',
            source_agency       = source_agency or '',
            affected_pl_numbers = affected_pl,
            implementation_status = 'PENDING',
        )
    except Exception:
        pass  # Signal errors must never crash the parent save
