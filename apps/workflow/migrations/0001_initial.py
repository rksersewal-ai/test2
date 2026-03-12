# Generated migration for apps.workflow
from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0001_initial'),
        ('edms', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='WorkType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('code', models.CharField(max_length=30, unique=True)),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={'db_table': 'workflow_work_type', 'ordering': ['code']},
        ),
        migrations.CreateModel(
            name='Vendor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('code', models.CharField(max_length=30, unique=True)),
                ('name', models.CharField(max_length=200)),
                ('address', models.TextField(blank=True)),
                ('contact', models.CharField(blank=True, max_length=100)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={'db_table': 'workflow_vendor', 'ordering': ['name']},
        ),
        migrations.CreateModel(
            name='Tender',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('tender_number', models.CharField(db_index=True, max_length=100, unique=True)),
                ('title', models.CharField(max_length=300)),
                ('description', models.TextField(blank=True)),
                ('status', models.CharField(
                    choices=[('OPEN', 'Open'), ('EVALUATION', 'Under Evaluation'),
                             ('CLOSED', 'Closed'), ('CANCELLED', 'Cancelled')],
                    default='OPEN', max_length=20)),
                ('issue_date', models.DateField(blank=True, null=True)),
                ('closing_date', models.DateField(blank=True, null=True)),
                ('eoffice_file_number', models.CharField(blank=True, db_index=True, max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL,
                                                 related_name='tenders_created',
                                                 to=settings.AUTH_USER_MODEL)),
            ],
            options={'db_table': 'workflow_tender', 'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='WorkLedger',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('status', models.CharField(
                    choices=[('OPEN', 'Open'), ('IN_PROGRESS', 'In Progress'),
                             ('CLOSED', 'Closed'), ('ON_HOLD', 'On Hold')],
                    default='OPEN', max_length=20)),
                ('received_date', models.DateField(blank=True, null=True)),
                ('target_date', models.DateField(blank=True, null=True)),
                ('closed_date', models.DateField(blank=True, null=True)),
                ('eoffice_file_number', models.CharField(blank=True, db_index=True, max_length=100)),
                ('eoffice_subject', models.CharField(blank=True, max_length=300)),
                ('subject', models.CharField(max_length=300)),
                ('remarks', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('work_type', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL,
                                                related_name='work_ledger_entries', to='workflow.worktype')),
                ('section', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                                              related_name='work_ledger_entries', to='core.section')),
                ('assigned_to', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                                                  related_name='work_ledger_assigned',
                                                  to=settings.AUTH_USER_MODEL)),
                ('document', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                                               related_name='work_ledger_entries', to='edms.document')),
                ('revision', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                                               related_name='work_ledger_entries', to='edms.revision')),
                ('tender', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                                             related_name='work_ledger_entries', to='workflow.tender')),
                ('vendor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                                             related_name='work_ledger_entries', to='workflow.vendor')),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL,
                                                 related_name='work_ledger_created',
                                                 to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'workflow_work_ledger',
                'ordering': ['-created_at'],
                'indexes': [
                    models.Index(fields=['eoffice_file_number'], name='wf_ledger_eoffice_idx'),
                    models.Index(fields=['status', 'section'], name='wf_ledger_status_section_idx'),
                    models.Index(fields=['received_date', 'closed_date'], name='wf_ledger_dates_idx'),
                ],
            },
        ),
    ]
