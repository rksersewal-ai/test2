# =============================================================================
# FILE: apps/workledger/dropdown_services.py
# FIX (#4): create_dropdown_item / log helpers now accept User instance
#           (not raw int), matching FK in DropdownMaster.created_by.
# =============================================================================
from django.db import transaction
from .dropdown_models import DropdownMaster, DropdownAuditLog


def _log(dropdown: DropdownMaster, action: str, changed_by,
         old_label: str = None, new_label: str = None):
    DropdownAuditLog.objects.create(
        dropdown_id=dropdown.id,
        group_key=dropdown.group_key,
        code=dropdown.code,
        action=action,
        old_label=old_label,
        new_label=new_label,
        changed_by=changed_by,  # now a User FK object
    )


def create_dropdown_item(validated_data: dict, created_by) -> DropdownMaster:
    with transaction.atomic():
        item = DropdownMaster.objects.create(
            **validated_data,
            is_system=False,
            created_by=created_by,   # User FK
        )
        _log(item, DropdownAuditLog.ACTION_CREATED, created_by, new_label=item.label)
    return item


def update_dropdown_item(item: DropdownMaster, validated_data: dict, changed_by) -> DropdownMaster:
    old_label = item.label
    with transaction.atomic():
        for attr, value in validated_data.items():
            setattr(item, attr, value)
        item.save()
        _log(item, DropdownAuditLog.ACTION_UPDATED, changed_by,
             old_label=old_label, new_label=item.label)
    return item


def deactivate_dropdown_item(item: DropdownMaster, changed_by) -> DropdownMaster:
    if item.is_system:
        raise ValueError('System dropdown items cannot be deactivated.')
    with transaction.atomic():
        item.is_active = False
        item.save()
        _log(item, DropdownAuditLog.ACTION_DEACTIVATED, changed_by)
    return item


def delete_dropdown_item(item: DropdownMaster, changed_by) -> None:
    if item.is_system:
        raise ValueError('System dropdown items cannot be deleted.')
    with transaction.atomic():
        _log(item, DropdownAuditLog.ACTION_DELETED, changed_by)
        item.delete()


def get_dropdown_group(group_key: str) -> list:
    items = DropdownMaster.objects.filter(
        group_key=group_key, is_active=True
    ).order_by('label')
    with_override    = [i for i in items if i.sort_override is not None]
    without_override = [i for i in items if i.sort_override is None]
    with_override.sort(key=lambda x: x.sort_override)
    return with_override + without_override


def get_all_groups() -> dict:
    all_items = DropdownMaster.objects.filter(is_active=True).order_by('group_key', 'label')
    result: dict = {}
    for item in all_items:
        result.setdefault(item.group_key, []).append(item)
    return result
