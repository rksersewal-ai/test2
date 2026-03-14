from django.db import transaction
from .models import WorkLedger, WorkLedgerDetail
from .repositories import next_work_code

# category codes that require extra dynamic detail fields
CATEGORY_REQUIRED_FIELDS = {
    "DRAWING_MODIFICATION_OR_NEW": ["drawing_number", "revision", "reason_for_change"],
    "SPECIFICATION_MODIFICATION": ["specification_number", "revision", "details_of_modification"],
    "PROTOTYPE_INSPECTION": ["firm_name", "inspection_date", "inspection_location", "inspection_result"],
    "SHOP_VISIT": ["shop_name", "visit_date", "purpose"],
    "NEW_INNOVATION": ["innovation_title", "innovation_description", "impact_benefit"],
}


def create_work_entry(validated_data: dict, created_by: int) -> WorkLedger:
    details_data = validated_data.pop("details", [])
    validated_data["work_code"] = next_work_code()
    validated_data["created_by"] = created_by

    with transaction.atomic():
        entry = WorkLedger.objects.create(**validated_data)
        for detail in details_data:
            WorkLedgerDetail.objects.create(work=entry, **detail)
    return entry


def update_work_entry(entry: WorkLedger, validated_data: dict) -> WorkLedger:
    details_data = validated_data.pop("details", None)

    with transaction.atomic():
        for attr, value in validated_data.items():
            setattr(entry, attr, value)
        entry.save()

        if details_data is not None:
            WorkLedgerDetail.objects.filter(work=entry).delete()
            for detail in details_data:
                WorkLedgerDetail.objects.create(work=entry, **detail)
    return entry


def get_dynamic_fields_for_category(category_code: str) -> list:
    return CATEGORY_REQUIRED_FIELDS.get(category_code, [])
