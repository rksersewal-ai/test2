from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('edms', '0002_revision_user_fields'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomFieldDefinition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('field_name', models.CharField(max_length=80)),
                ('field_label', models.CharField(max_length=200)),
                ('field_type', models.CharField(choices=[('text', 'Text'), ('number', 'Number'), ('date', 'Date'), ('select', 'Select (dropdown)'), ('boolean', 'Yes / No')], default='text', max_length=20)),
                ('select_options', models.TextField(blank=True)),
                ('is_required', models.BooleanField(default=False)),
                ('sort_order', models.IntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('document_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='custom_field_definitions', to='edms.documenttype')),
            ],
            options={
                'db_table': 'edms_custom_field_definition',
                'ordering': ['document_type', 'sort_order', 'field_name'],
                'unique_together': {('document_type', 'field_name')},
            },
        ),
        migrations.CreateModel(
            name='Correspondent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=300)),
                ('short_code', models.CharField(max_length=30, unique=True)),
                ('org_type', models.CharField(choices=[('RDSO', 'RDSO'), ('CLW', 'CLW'), ('BLW', 'BLW'), ('ICF', 'ICF'), ('ZR', 'Zonal Railway'), ('HQ', 'Railway Board / HQ'), ('VENDOR', 'Vendor / Supplier'), ('CONTRACTOR', 'Contractor'), ('OTHER', 'Other')], default='OTHER', max_length=20)),
                ('address', models.TextField(blank=True)),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='correspondents_created', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'edms_correspondent',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='DocumentCustomField',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('field_value', models.TextField(blank=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('definition', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='values', to='edms.customfielddefinition')),
                ('document', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='custom_fields', to='edms.document')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='custom_fields_updated', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'edms_document_custom_field',
                'ordering': ['definition__sort_order'],
                'unique_together': {('document', 'definition')},
            },
        ),
        migrations.CreateModel(
            name='DocumentCorrespondentLink',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reference_number', models.CharField(blank=True, max_length=200)),
                ('reference_date', models.DateField(blank=True, null=True)),
                ('link_type', models.CharField(choices=[('ISSUED_BY', 'Issued By'), ('ADDRESSED_TO', 'Addressed To'), ('CC', 'CC'), ('APPROVED_BY', 'Approved By'), ('CONSULTED', 'Consulted')], default='ISSUED_BY', max_length=20)),
                ('remarks', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('correspondent', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='document_links', to='edms.correspondent')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='correspondent_links_created', to=settings.AUTH_USER_MODEL)),
                ('document', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='correspondent_links', to='edms.document')),
            ],
            options={
                'db_table': 'edms_document_correspondent_link',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='DocumentNote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('note_type', models.CharField(choices=[('REVIEW', 'Review Comment'), ('QUERY', 'Query'), ('OBSERVATION', 'Observation'), ('INFO', 'Information'), ('ACTION_REQUIRED', 'Action Required')], default='OBSERVATION', max_length=20)),
                ('note_text', models.TextField()),
                ('is_resolved', models.BooleanField(default=False)),
                ('resolved_at', models.DateTimeField(blank=True, null=True)),
                ('resolution_note', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='notes_created', to=settings.AUTH_USER_MODEL)),
                ('document', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notes', to='edms.document')),
                ('resolved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='notes_resolved', to=settings.AUTH_USER_MODEL)),
                ('revision', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='notes', to='edms.revision')),
            ],
            options={
                'db_table': 'edms_document_note',
                'ordering': ['-created_at'],
            },
        ),
    ]
