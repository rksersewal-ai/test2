from apps.audit.services import AuditService


class WorkLedgerService:
    @staticmethod
    def log_create(entry, user):
        AuditService.log(
            user=user,
            module='WORKFLOW',
            action='CREATE_WORK_ENTRY',
            entity_type='WorkLedgerEntry',
            entity_id=entry.pk,
            entity_identifier=entry.eoffice_file_number or str(entry.pk),
            description=f'Work entry created: {entry.subject or entry.eoffice_subject or entry.pk}',
        )

    @staticmethod
    def log_update(entry, user):
        AuditService.log(
            user=user,
            module='WORKFLOW',
            action='UPDATE_WORK_ENTRY',
            entity_type='WorkLedgerEntry',
            entity_id=entry.pk,
            entity_identifier=entry.eoffice_file_number or str(entry.pk),
            description=f'Work entry [{entry.status}] updated: {entry.subject or entry.eoffice_subject or entry.pk}',
        )
