from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [('edms', '0001_initial')]

    operations = [
        migrations.CreateModel(
            name='OCRQueue',
            fields=[
                ('id',            models.BigAutoField(auto_created=True, primary_key=True)),
                ('status',        models.CharField(choices=[('PENDING','Pending'),('PROCESSING','Processing'),('COMPLETED','Completed'),('FAILED','Failed'),('RETRY','Retry'),('MANUAL_REVIEW','Manual Review')], db_index=True, default='PENDING', max_length=20)),
                ('priority',      models.PositiveSmallIntegerField(default=5)),
                ('attempts',      models.PositiveSmallIntegerField(default=0)),
                ('max_attempts',  models.PositiveSmallIntegerField(default=3)),
                ('ocr_engine',    models.CharField(default='tesseract-5', max_length=40)),
                ('queued_at',     models.DateTimeField(auto_now_add=True, db_index=True)),
                ('started_at',    models.DateTimeField(blank=True, null=True)),
                ('completed_at',  models.DateTimeField(blank=True, null=True)),
                ('processing_time_seconds', models.FloatField(blank=True, null=True)),
                ('failure_reason', models.TextField(blank=True)),
                ('file_attachment', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='ocr_queue_item', to='edms.fileattachment')),
            ],
            options={'db_table': 'ocr_queue', 'ordering': ['priority', 'queued_at']},
        ),
        migrations.AddIndex(model_name='ocrqueue', index=models.Index(fields=['status','priority','queued_at'], name='ocr_queue_status_prio_idx')),
        migrations.CreateModel(
            name='OCRResult',
            fields=[
                ('id',                models.BigAutoField(auto_created=True, primary_key=True)),
                ('full_text',         models.TextField(blank=True)),
                ('confidence',        models.FloatField(blank=True, null=True)),
                ('page_count',        models.PositiveSmallIntegerField(default=1)),
                ('language_detected', models.CharField(blank=True, max_length=10)),
                ('extracted_at',      models.DateTimeField(auto_now_add=True)),
                ('queue_item',        models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='result', to='ocr.ocrqueue')),
            ],
            options={'db_table': 'ocr_result'},
        ),
        migrations.CreateModel(
            name='OCRExtractedEntity',
            fields=[
                ('id',          models.BigAutoField(auto_created=True, primary_key=True)),
                ('entity_type', models.CharField(choices=[('DOC_NUM','Document Number'),('SPEC','Specification'),('STD','Standard'),('DWG','Drawing Number'),('PART','Part Number'),('DATE','Date'),('OTHER','Other')], max_length=20)),
                ('value',       models.CharField(max_length=500)),
                ('confidence',  models.FloatField(blank=True, null=True)),
                ('page_number', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('result',      models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='entities', to='ocr.ocrresult')),
            ],
            options={'db_table': 'ocr_extracted_entity'},
        ),
        migrations.AddIndex(model_name='ocrextractedentity', index=models.Index(fields=['entity_type','value'], name='ocr_entity_type_val_idx')),
    ]
