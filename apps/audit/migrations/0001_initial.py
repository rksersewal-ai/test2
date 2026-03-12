from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [
        migrations.CreateModel(
            name='AuditLog',
            fields=[
                ('id',              models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp',       models.DateTimeField(auto_now_add=True, db_index=True)),
                ('username',        models.CharField(blank=True, max_length=150)),
                ('user_full_name',  models.CharField(blank=True, max_length=300)),
                ('module',          models.CharField(choices=[('EDMS','EDMS'),('WORKFLOW','Work Ledger'),('OCR','OCR Pipeline'),('CORE','Core / Admin'),('AUTH','Authentication')], db_index=True, max_length=20)),
                ('action',          models.CharField(db_index=True, max_length=80)),
                ('entity_type',     models.CharField(blank=True, max_length=80)),
                ('entity_id',       models.BigIntegerField(blank=True, null=True)),
                ('entity_identifier', models.CharField(blank=True, max_length=300)),
                ('description',     models.TextField(blank=True)),
                ('extra_data',      models.JSONField(blank=True, null=True)),
                ('ip_address',      models.GenericIPAddressField(blank=True, null=True)),
                ('user_agent',      models.CharField(blank=True, max_length=500)),
                ('success',         models.BooleanField(default=True)),
                ('user',            models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='audit_logs', to=settings.AUTH_USER_MODEL)),
            ],
            options={'db_table': 'audit_log', 'ordering': ['-timestamp']},
        ),
        migrations.AddIndex(model_name='auditlog', index=models.Index(fields=['module','action'], name='audit_log_module_action_idx')),
        migrations.AddIndex(model_name='auditlog', index=models.Index(fields=['entity_type','entity_id'], name='audit_log_entity_idx')),
        migrations.AddIndex(model_name='auditlog', index=models.Index(fields=['user'], name='audit_log_user_idx')),
        migrations.AddIndex(model_name='auditlog', index=models.Index(fields=['timestamp'], name='audit_log_ts_idx')),
    ]
