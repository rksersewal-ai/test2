# Generated migration for apps.edms
from django.db import migrations, models
import django.db.models.deletion
import apps.edms.models
from django.conf import settings


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('code', models.CharField(max_length=20, unique=True)),
                ('name', models.CharField(max_length=120)),
                ('description', models.TextField(blank=True)),
                ('is_active', models.BooleanField(default=True)),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                                             related_name='children', to='edms.category')),
            ],
            options={'db_table': 'edms_category', 'ordering': ['code'], 'verbose_name_plural': 'Categories'},
        ),
        migrations.CreateModel(
            name='DocumentType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('code', models.CharField(max_length=20, unique=True)),
                ('name', models.CharField(max_length=120)),
                ('description', models.TextField(blank=True)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={'db_table': 'edms_document_type'},
        ),
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('document_number', models.CharField(db_index=True, max_length=100, unique=True)),
                ('title', models.CharField(max_length=300)),
                ('description', models.TextField(blank=True)),
                ('status', models.CharField(
                    choices=[('ACTIVE', 'Active'), ('SUPERSEDED', 'Superseded'),
                             ('OBSOLETE', 'Obsolete'), ('DRAFT', 'Draft')],
                    default='ACTIVE', max_length=20)),
                ('source_standard', models.CharField(blank=True, max_length=100)),
                ('eoffice_file_number', models.CharField(blank=True, db_index=True, max_length=100)),
                ('eoffice_subject', models.CharField(blank=True, max_length=300)),
                ('keywords', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                                               related_name='documents', to='edms.category')),
                ('document_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                                                    related_name='documents', to='edms.documenttype')),
                ('section', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                                              related_name='documents', to='core.section')),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL,
                                                 related_name='documents_created',
                                                 to=settings.AUTH_USER_MODEL)),
            ],
            options={'db_table': 'edms_document', 'ordering': ['document_number']},
        ),
        migrations.CreateModel(
            name='Revision',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('revision_number', models.CharField(max_length=20)),
                ('revision_date', models.DateField(blank=True, null=True)),
                ('status', models.CharField(
                    choices=[('CURRENT', 'Current'), ('SUPERSEDED', 'Superseded'), ('DRAFT', 'Draft')],
                    default='CURRENT', max_length=20)),
                ('change_description', models.TextField(blank=True)),
                ('prepared_by', models.CharField(blank=True, max_length=150)),
                ('approved_by', models.CharField(blank=True, max_length=150)),
                ('eoffice_ref', models.CharField(blank=True, max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('document', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                               related_name='revisions', to='edms.document')),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL,
                                                 related_name='revisions_created',
                                                 to=settings.AUTH_USER_MODEL)),
            ],
            options={'db_table': 'edms_revision', 'ordering': ['document', '-created_at'],
                     'unique_together': {('document', 'revision_number')}},
        ),
        migrations.CreateModel(
            name='FileAttachment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('file_name', models.CharField(max_length=255)),
                ('file_path', models.FileField(max_length=500, upload_to=apps.edms.models.upload_to)),
                ('file_size_bytes', models.BigIntegerField(blank=True, null=True)),
                ('file_type', models.CharField(
                    choices=[('PDF', 'PDF'), ('IMAGE', 'Image'), ('TIFF', 'TIFF')],
                    default='PDF', max_length=10)),
                ('page_count', models.IntegerField(blank=True, null=True)),
                ('checksum_sha256', models.CharField(blank=True, db_index=True, max_length=64)),
                ('is_primary', models.BooleanField(default=False)),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('revision', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                               related_name='files', to='edms.revision')),
                ('uploaded_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL,
                                                  related_name='files_uploaded',
                                                  to=settings.AUTH_USER_MODEL)),
            ],
            options={'db_table': 'edms_file_attachment', 'ordering': ['-uploaded_at']},
        ),
    ]
