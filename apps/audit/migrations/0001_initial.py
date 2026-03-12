# Generated migration for apps.audit
from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AuditLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('timestamp', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('username', models.CharField(db_index=True, max_length=60)),
                ('action', models.CharField(db_index=True, max_length=50)),
                ('module', models.CharField(db_index=True, max_length=50)),
                ('entity_type', models.CharField(max_length=100)),
                ('entity_id', models.CharField(blank=True, max_length=50)),
                ('entity_identifier', models.CharField(blank=True, max_length=300)),
                ('description', models.TextField(blank=True)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('user_agent', models.CharField(blank=True, max_length=500)),
                ('request_method', models.CharField(blank=True, max_length=10)),
                ('request_path', models.CharField(blank=True, max_length=500)),
                ('before_value', models.JSONField(blank=True, null=True)),
                ('after_value', models.JSONField(blank=True, null=True)),
                ('changes', models.JSONField(blank=True, null=True)),
                ('success', models.BooleanField(default=True)),
                ('error_message', models.TextField(blank=True)),
                ('session_id', models.CharField(blank=True, max_length=100)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL,
                                           related_name='audit_logs', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'audit_log',
                'ordering': ['-timestamp'],
                'indexes': [
                    models.Index(fields=['timestamp', 'module'], name='audit_ts_module_idx'),
                    models.Index(fields=['username', 'action'], name='audit_user_action_idx'),
                    models.Index(fields=['entity_type', 'entity_id'], name='audit_entity_idx'),
                ],
            },
        ),
        migrations.CreateModel(
            name='DocumentAccessLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('timestamp', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('document_id', models.IntegerField(blank=True, db_index=True, null=True)),
                ('revision_id', models.IntegerField(blank=True, null=True)),
                ('file_id', models.IntegerField(blank=True, null=True)),
                ('access_type', models.CharField(
                    choices=[('VIEW', 'View'), ('DOWNLOAD', 'Download'),
                             ('SEARCH', 'Search'), ('UPLOAD', 'Upload')],
                    max_length=20)),
                ('document_number', models.CharField(blank=True, db_index=True, max_length=100)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('session_id', models.CharField(blank=True, max_length=100)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL,
                                           related_name='doc_access_logs', to=settings.AUTH_USER_MODEL)),
            ],
            options={'db_table': 'audit_document_access_log', 'ordering': ['-timestamp']},
        ),
    ]
