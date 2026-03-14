# =============================================================================
# FILE: backend/master/migrations/0002_pl_tech_eval_doc.py
# MIGRATION: Creates pl_master_tech_eval_doc table
# Run: python manage.py migrate master
# =============================================================================
from django.conf import settings
from django.db import migrations, models
import master.models_tech_eval
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('master', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='PLTechEvalDocument',
            fields=[
                ('id',            models.BigAutoField(auto_created=True, primary_key=True)),
                ('pl_number',     models.CharField(db_index=True, max_length=50)),
                ('tender_number', models.CharField(max_length=100)),
                ('eval_year',     models.PositiveSmallIntegerField()),
                ('document_file', models.FileField(
                    upload_to=master.models_tech_eval._eval_doc_upload_path,
                    validators=[master.models_tech_eval._validate_eval_doc_format],
                )),
                ('file_name',    models.CharField(max_length=255, editable=False)),
                ('file_format',  models.CharField(
                    max_length=4, editable=False,
                    choices=[('PDF', 'PDF'), ('DOCX', 'DOCX')]
                )),
                ('file_size_kb', models.PositiveIntegerField(editable=False, default=0)),
                ('uploaded_by',  models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='uploaded_eval_docs',
                    to=settings.AUTH_USER_MODEL,
                )),
                ('uploaded_at',  models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'PL Technical Evaluation Document',
                'verbose_name_plural': 'PL Technical Evaluation Documents',
                'ordering': ['-uploaded_at'],
                'indexes': [
                    models.Index(fields=['pl_number', '-uploaded_at'],
                                 name='master_plte_pl_numb_idx'),
                ],
            },
        ),
    ]
