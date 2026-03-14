# =============================================================================
# FILE: backend/master/migrations/0003_pl_vendor_info_linked_docs.py
# Run: python manage.py migrate master
# =============================================================================
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('master', '0002_pl_tech_eval_doc'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # ── PLVendorInfo ──────────────────────────────────────────────────────
        migrations.CreateModel(
            name='PLVendorInfo',
            fields=[
                ('id',                   models.BigAutoField(auto_created=True, primary_key=True)),
                ('pl_number',            models.CharField(max_length=50, unique=True, db_index=True)),
                ('vendor_type',          models.CharField(max_length=3, choices=[('VD','VD — Vendor Directory (UVAM)'),('NVD','NVD — Non-Vendor Directory')], default='NVD')),
                ('uvam_vd_number',       models.CharField(max_length=60, blank=True)),
                ('eligibility_criteria', models.TextField(blank=True)),
                ('updated_at',           models.DateTimeField(auto_now=True)),
                ('created_at',           models.DateTimeField(auto_now_add=True)),
                ('updated_by',           models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='pl_vendor_updates', to=settings.AUTH_USER_MODEL)),
            ],
            options={'app_label': 'master', 'ordering': ['pl_number'], 'verbose_name': 'PL Vendor / Eligibility Info'},
        ),
        # ── PLLinkedDocument ──────────────────────────────────────────────────
        migrations.CreateModel(
            name='PLLinkedDocument',
            fields=[
                ('id',              models.BigAutoField(auto_created=True, primary_key=True)),
                ('pl_number',       models.CharField(max_length=50, db_index=True)),
                ('document_id',     models.PositiveIntegerField(null=True, blank=True)),
                ('document_title',  models.CharField(max_length=300, blank=True)),
                ('document_number', models.CharField(max_length=120, blank=True)),
                ('category',        models.CharField(max_length=20, choices=[('SPECIFICATION','Specification'),('DRAWING','Drawing'),('STANDARD','Standard'),('STR','STR — Special Technical Requirement'),('TECH_EVAL','Technical Evaluation Document'),('OTHER','Other Technical Document')], default='OTHER')),
                ('remarks',         models.CharField(max_length=200, blank=True)),
                ('linked_at',       models.DateTimeField(auto_now_add=True)),
                ('linked_by',       models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='pl_doc_links', to=settings.AUTH_USER_MODEL)),
            ],
            options={'app_label': 'master', 'ordering': ['category', 'document_number'], 'verbose_name': 'PL Linked Document',
                     'indexes': [models.Index(fields=['pl_number', 'category'], name='master_plld_pl_cat_idx')],
                     'unique_together': {('pl_number', 'document_id')}},
        ),
    ]
