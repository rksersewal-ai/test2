# Generated migration for apps.ocr
from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('edms', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='OCRQueue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('status', models.CharField(
                    choices=[('PENDING', 'Pending'), ('PROCESSING', 'Processing'),
                             ('COMPLETED', 'Completed'), ('FAILED', 'Failed'),
                             ('RETRY', 'Retry'), ('MANUAL_REVIEW', 'Manual Review')],
                    db_index=True, default='PENDING', max_length=20)),
                ('priority', models.IntegerField(default=5)),
                ('attempts', models.IntegerField(default=0)),
                ('max_attempts', models.IntegerField(default=3)),
                ('queued_at', models.DateTimeField(auto_now_add=True)),
                ('started_at', models.DateTimeField(blank=True, null=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('last_error', models.TextField(blank=True)),
                ('processing_time_seconds', models.FloatField(blank=True, null=True)),
                ('ocr_engine', models.CharField(default='tesseract', max_length=50)),
                ('language', models.CharField(default='eng', max_length=10)),
                ('preprocessing_options', models.JSONField(blank=True, default=dict)),
                ('worker_id', models.CharField(blank=True, max_length=100)),
                ('assigned_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('file', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE,
                                              related_name='ocr_queue', to='edms.fileattachment')),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL,
                                                 related_name='ocr_queue_created',
                                                 to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'ocr_queue',
                'ordering': ['priority', 'queued_at'],
                'indexes': [
                    models.Index(fields=['status', 'priority'], name='ocr_queue_status_priority_idx'),
                    models.Index(fields=['status', 'queued_at'], name='ocr_queue_status_queued_idx'),
                ],
            },
        ),
        migrations.CreateModel(
            name='OCRResult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('full_text', models.TextField(blank=True)),
                ('page_count', models.IntegerField(blank=True, null=True)),
                ('confidence_score', models.FloatField(blank=True, null=True)),
                ('page_results', models.JSONField(default=list)),
                ('ocr_engine', models.CharField(default='tesseract', max_length=50)),
                ('ocr_version', models.CharField(blank=True, max_length=30)),
                ('language_detected', models.CharField(blank=True, max_length=10)),
                ('processing_time_seconds', models.FloatField(blank=True, null=True)),
                ('file_size_bytes', models.BigIntegerField(blank=True, null=True)),
                ('processed_at', models.DateTimeField(auto_now_add=True)),
                ('indexed_at', models.DateTimeField(blank=True, null=True)),
                ('file', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE,
                                              related_name='ocr_result', to='edms.fileattachment')),
                ('queue', models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL,
                                               related_name='result', to='ocr.ocrqueue')),
            ],
            options={'db_table': 'ocr_result'},
        ),
        migrations.CreateModel(
            name='ExtractedEntity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('entity_type', models.CharField(
                    choices=[('DOC_NUM', 'Document Number'), ('SPEC_NUM', 'Specification Number'),
                             ('STANDARD', 'Standard Reference'), ('DRG_NUM', 'Drawing Number'),
                             ('DATE', 'Date'), ('REVISION', 'Revision'),
                             ('KEYWORD', 'Keyword'), ('OTHER', 'Other')],
                    max_length=20)),
                ('entity_value', models.CharField(db_index=True, max_length=300)),
                ('confidence', models.FloatField(blank=True, null=True)),
                ('context', models.TextField(blank=True)),
                ('page_number', models.IntegerField(blank=True, null=True)),
                ('bounding_box', models.JSONField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('ocr_result', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                                  related_name='entities', to='ocr.ocrresult')),
            ],
            options={
                'db_table': 'ocr_extracted_entity',
                'indexes': [
                    models.Index(fields=['entity_type', 'entity_value'], name='ocr_entity_type_value_idx'),
                ],
            },
        ),
    ]
