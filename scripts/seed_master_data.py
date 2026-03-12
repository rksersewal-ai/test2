"""Seed master data for PLW EDMS + LDO production setup.
Run: python manage.py shell < scripts/seed_master_data.py
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.core.models import Section, User
from apps.edms.models import Category, DocumentType
from apps.workflow.models import WorkType

print('--- Seeding Sections ---')
SECTIONS = [
    ('HQ', 'Headquarters / PLW Admin'),
    ('MECH', 'Mechanical Engineering'),
    ('ELEC', 'Electrical Engineering'),
    ('LOCO', 'Locomotive Production'),
    ('QUAL', 'Quality Assurance'),
    ('STORE', 'Stores'),
    ('PROJ', 'Projects'),
    ('IT', 'Information Technology'),
    ('LDO', 'LDO / Design Office'),
]
for code, name in SECTIONS:
    obj, created = Section.objects.get_or_create(code=code, defaults={'name': name})
    print(f'  {"Created" if created else "Exists"}: {obj}')

print('--- Seeding Document Categories ---')
CATEGORIES = [
    ('SPEC', 'Technical Specifications'),
    ('DRG', 'Engineering Drawings'),
    ('STD', 'Standards and Codes'),
    ('PROC', 'Procedures and SOPs'),
    ('RPT', 'Reports'),
    ('CERT', 'Certificates'),
    ('MAINT', 'Maintenance Manuals'),
    ('TRAIN', 'Training Materials'),
    ('CORR', 'Correspondence'),
    ('TENDER', 'Tender Documents'),
]
for code, name in CATEGORIES:
    obj, created = Category.objects.get_or_create(code=code, defaults={'name': name})
    print(f'  {"Created" if created else "Exists"}: {obj}')

print('--- Seeding Document Types ---')
DOC_TYPES = [
    ('RDSO_SPEC', 'RDSO Specification'),
    ('IR_STD', 'Indian Railways Standard'),
    ('DIN_STD', 'DIN Standard'),
    ('IS_STD', 'IS / BIS Standard'),
    ('ABB_DOC', 'ABB Technical Document'),
    ('INTERNAL', 'Internal Document'),
    ('VENDOR', 'Vendor Document'),
    ('IRIS', 'IRIS Certification Document'),
]
for code, name in DOC_TYPES:
    obj, created = DocumentType.objects.get_or_create(code=code, defaults={'name': name})
    print(f'  {"Created" if created else "Exists"}: {obj}')

print('--- Seeding Work Types ---')
WORK_TYPES = [
    ('LDO-MAINT', 'Maintenance Drawing Order'),
    ('LDO-DRG', 'Drawing Preparation'),
    ('LDO-SPEC-REV', 'Specification Review'),
    ('LDO-VEND-CLR', 'Vendor Drawing Clearance'),
    ('LDO-QC', 'Quality Check / Inspection Support'),
    ('LDO-TENDER', 'Tender Technical Support'),
    ('LDO-CORR', 'Correspondence Handling'),
    ('LDO-AUDIT', 'Audit Support Work'),
    ('LDO-TRAIN', 'Training Material Preparation'),
]
for code, name in WORK_TYPES:
    obj, created = WorkType.objects.get_or_create(code=code, defaults={'name': name})
    print(f'  {"Created" if created else "Exists"}: {obj}')

print('--- Seeding Admin User ---')
if not User.objects.filter(username='admin').exists():
    admin = User.objects.create_superuser(
        username='admin',
        password='ChangeMe@2026!',
        full_name='System Administrator',
        role=User.Role.ADMIN,
    )
    print(f'  Created admin user: {admin.username} (CHANGE PASSWORD IMMEDIATELY)')
else:
    print('  Admin user already exists.')

print('\nMaster data seed complete.')
