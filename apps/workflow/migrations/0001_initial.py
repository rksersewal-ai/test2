from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ('edms', '0001_initial'),
        ('core', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [
        migrations.CreateModel(
            name='WorkType',
            fields=[
                ('id',          models.BigAutoField(auto_created=True, primary_key=True)),
                ('name',        models.CharField(max_length=120, unique=True)),
                ('code',        models.CharField(max_length=20, unique=True)),
                ('description', models.TextField(blank=True)),
                ('is_active',   models.BooleanField(default=True)),
            ],
            options={'db_table': 'workflow_work_type', 'ordering': ['name']},
        ),
        migrations.CreateModel(
            name='WorkLedgerEntry',
            fields=[
                ('id',                    models.BigAutoField(auto_created=True, primary_key=True)),
                ('subject',               models.CharField(blank=True, max_length=500)),
                ('description',           models.TextField(blank=True)),
                ('eoffice_file_number',   models.CharField(blank=True, db_index=True, max_length=100)),
                ('eoffice_subject',       models.CharField(blank=True, max_length=500)),
                ('eoffice_diary_number',  models.CharField(blank=True, max_length=100)),
                ('status',                models.CharField(choices=[('OPEN','Open'),('IN_PROGRESS','In Progress'),('ON_HOLD','On Hold'),('CLOSED','Closed')], db_index=True, default='OPEN', max_length=20)),
                ('received_date',         models.DateField(blank=True, null=True)),
                ('target_date',           models.DateField(blank=True, null=True)),
                ('closed_date',           models.DateField(blank=True, null=True)),
                ('remarks',               models.TextField(blank=True)),
                ('created_at',            models.DateTimeField(auto_now_add=True)),
                ('updated_at',            models.DateTimeField(auto_now=True)),
                ('work_type',      models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='entries', to='workflow.worktype')),
                ('section',        models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='work_entries', to='core.section')),
                ('assigned_to',    models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_work_entries', to=settings.AUTH_USER_MODEL)),
                ('created_by',     models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_work_entries', to=settings.AUTH_USER_MODEL)),
                ('linked_document',models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='work_entries', to='edms.document')),
                ('linked_revision',models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='work_entries', to='edms.revision')),
            ],
            options={'db_table': 'workflow_work_ledger_entry', 'ordering': ['-created_at']},
        ),
        migrations.AddIndex(model_name='workledgerentry', index=models.Index(fields=['status'],              name='wl_status_idx')),
        migrations.AddIndex(model_name='workledgerentry', index=models.Index(fields=['section'],             name='wl_section_idx')),
        migrations.AddIndex(model_name='workledgerentry', index=models.Index(fields=['assigned_to'],         name='wl_assigned_idx')),
        migrations.AddIndex(model_name='workledgerentry', index=models.Index(fields=['eoffice_file_number'], name='wl_eoffice_idx')),
        migrations.AddIndex(model_name='workledgerentry', index=models.Index(fields=['target_date'],         name='wl_target_date_idx')),
    ]
