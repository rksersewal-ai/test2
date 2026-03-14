# =============================================================================
# FILE: apps/pl_master/management/commands/resolve_mother_parts.py
#
# PURPOSE:
#   Second-pass after import_category_book.
#   Reads the 'mother_part' field stored as a plain string during bulk import
#   and resolves it to the actual PLMaster FK.
#
# USAGE:
#   python manage.py resolve_mother_parts
#   python manage.py resolve_mother_parts --dry-run
#   python manage.py resolve_mother_parts --report   (print orphan summary only)
# =============================================================================
from django.core.management.base import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    help = 'Resolve PLMaster.mother_part_raw strings to FK references'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Do not write to DB')
        parser.add_argument('--report',  action='store_true', help='Print orphan summary only')

    def handle(self, *args, **options):
        from apps.pl_master.models import PLMaster

        dry_run = options['dry_run']
        report  = options['report']

        # All PLMaster rows that have a raw mother-part string but no FK yet
        # We store the raw value in remarks-alike field mother_part_raw (CharField)
        # and the resolved FK in mother_part (ForeignKey, null=True)
        pending = PLMaster.objects.filter(
            mother_part_raw__isnull=False,
            mother_part_raw__gt='',
            mother_part__isnull=True,
        ).select_related('mother_part')

        total     = pending.count()
        resolved  = 0
        orphans   = []

        self.stdout.write(f'Found {total} PLMaster rows with unresolved mother_part_raw.')

        for pl in pending:
            raw = (pl.mother_part_raw or '').strip()
            if not raw:
                continue
            parent = PLMaster.objects.filter(pl_number=raw).first()
            if parent:
                if parent.pk == pl.pk:
                    self.stdout.write(self.style.WARNING(f'  SKIP self-ref: {pl.pl_number}'))
                    continue
                if not dry_run:
                    with transaction.atomic():
                        pl.mother_part = parent
                        pl.save(update_fields=['mother_part'])
                resolved += 1
                self.stdout.write(f'  LINKED  {pl.pl_number}  →  {raw}')
            else:
                orphans.append({'pl_number': pl.pl_number, 'mother_part_raw': raw})

        self.stdout.write('\n' + '='*60)
        mode = '[DRY-RUN] ' if dry_run else ''
        self.stdout.write(self.style.SUCCESS(
            f'{mode}Resolve complete:\n'
            f'  Total pending : {total}\n'
            f'  Resolved      : {resolved}\n'
            f'  Orphans       : {len(orphans)}'
        ))

        if orphans:
            self.stdout.write(self.style.WARNING('\nOrphan PLMaster rows (mother PL not found)::'))
            for o in orphans[:50]:
                self.stdout.write(f'  {o["pl_number"]}  →  mother={o["mother_part_raw"]}')
            if len(orphans) > 50:
                self.stdout.write(f'  ... and {len(orphans)-50} more.')

            if report:
                import csv, io
                buf = io.StringIO()
                w   = csv.DictWriter(buf, fieldnames=['pl_number', 'mother_part_raw'])
                w.writeheader()
                w.writerows(orphans)
                self.stdout.write('\nCSV dump of orphans:')
                self.stdout.write(buf.getvalue())
