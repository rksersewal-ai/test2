# =============================================================================
# FILE: apps/pl_master/management/commands/seed_pl_master.py
# Usage:
#   python manage.py seed_pl_master             # loads fixture + reports
#   python manage.py seed_pl_master --reset     # clears ControllingAgency first
# =============================================================================
from django.core.management.base import BaseCommand
from django.core.management      import call_command
from apps.pl_master.models       import ControllingAgency


class Command(BaseCommand):
    help = 'Seed PLMaster initial data: ControllingAgency fixture'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Delete all ControllingAgency records before seeding',
        )

    def handle(self, *args, **options):
        if options['reset']:
            count, _ = ControllingAgency.objects.all().delete()
            self.stdout.write(self.style.WARNING(f'Deleted {count} existing agency records.'))

        self.stdout.write('Loading controlling_agencies fixture...')
        call_command('loaddata', 'controlling_agencies', app_label='pl_master', verbosity=1)

        # Verification report
        agencies = ControllingAgency.objects.filter(is_active=True).order_by('agency_code')
        self.stdout.write(self.style.SUCCESS(
            f'\n[OK] {agencies.count()} controlling agencies loaded:\n'
        ))
        for a in agencies:
            self.stdout.write(f'  {a.agency_code:<10} {a.agency_name}')

        self.stdout.write(
            self.style.SUCCESS('\n[DONE] seed_pl_master completed successfully.')
        )
