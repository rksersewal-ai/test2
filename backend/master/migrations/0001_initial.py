# =============================================================================
# FILE: backend/master/migrations/0001_initial.py
# Creates all base master app tables in one migration.
# =============================================================================
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # ── LocomotiveType ─────────────────────────────────────────────────────────
        migrations.CreateModel(
            name='LocomotiveType',
            fields=[
                ('id',              models.BigAutoField(auto_created=True, primary_key=True)),
                ('model_id',        models.CharField(max_length=30, unique=True)),
                ('name',            models.CharField(max_length=120)),
                ('loco_class',      models.CharField(max_length=60)),
                ('status',          models.CharField(max_length=30, default='Production',
                                    choices=[('Production','Production'),('Testing','Testing'),('Concept','Concept'),('Legacy','Legacy'),('Under Review','Under Review')])),
                ('engine_power',    models.CharField(max_length=30)),
                ('engine_type',     models.CharField(max_length=60, blank=True)),
                ('manufacturer',    models.CharField(max_length=80, blank=True)),
                ('year_introduced', models.PositiveSmallIntegerField(null=True, blank=True)),
                ('notes',           models.TextField(blank=True)),
                ('created_at',      models.DateTimeField(auto_now_add=True)),
                ('updated_at',      models.DateTimeField(auto_now=True)),
                ('updated_by',      models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='loco_updates', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['model_id']},
        ),
        # ── ComponentCatalog ────────────────────────────────────────────────────
        migrations.CreateModel(
            name='ComponentCatalog',
            fields=[
                ('id',              models.BigAutoField(auto_created=True, primary_key=True)),
                ('part_number',     models.CharField(max_length=40, unique=True)),
                ('description',     models.CharField(max_length=200)),
                ('category',        models.CharField(max_length=30, choices=[('Mechanical','Mechanical'),('Electrical','Electrical'),('Pneumatic','Pneumatic'),('Electronic','Electronic'),('Structural','Structural')])),
                ('status',          models.CharField(max_length=30, default='Active', choices=[('Active','Active'),('Obsolete','Obsolete'),('Under Review','Under Review')])),
                ('supplier',        models.CharField(max_length=100, blank=True)),
                ('unit',            models.CharField(max_length=20, default='Nos')),
                ('unit_price',      models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)),
                ('notes',           models.TextField(blank=True)),
                ('created_at',      models.DateTimeField(auto_now_add=True)),
                ('updated_at',      models.DateTimeField(auto_now=True)),
                ('applicable_locos',models.ManyToManyField(blank=True, related_name='components', to='master.locomotivetype')),
            ],
            options={'ordering': ['part_number']},
        ),
        # ── LookupCategory + LookupItem ──────────────────────────────────────────────
        migrations.CreateModel(
            name='LookupCategory',
            fields=[
                ('id',          models.BigAutoField(auto_created=True, primary_key=True)),
                ('name',        models.CharField(max_length=80, unique=True)),
                ('code',        models.CharField(max_length=30, unique=True)),
                ('description', models.TextField(blank=True)),
                ('created_at',  models.DateTimeField(auto_now_add=True)),
            ],
            options={'ordering': ['name'], 'verbose_name_plural': 'Lookup Categories'},
        ),
        migrations.CreateModel(
            name='LookupItem',
            fields=[
                ('id',        models.BigAutoField(auto_created=True, primary_key=True)),
                ('label',     models.CharField(max_length=80)),
                ('value',     models.CharField(max_length=80)),
                ('color',     models.CharField(max_length=20, default='#6b7280')),
                ('order',     models.PositiveSmallIntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
                ('category',  models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='master.lookupcategory')),
            ],
            options={'ordering': ['order', 'label'], 'unique_together': {('category', 'value')}},
        ),
        # ── MasterDataChangeLog ──────────────────────────────────────────────────────
        migrations.CreateModel(
            name='MasterDataChangeLog',
            fields=[
                ('id',          models.BigAutoField(auto_created=True, primary_key=True)),
                ('action',      models.CharField(max_length=20, choices=[('modified','Modified'),('added','Added'),('deprecated','Deprecated')])),
                ('model_name',  models.CharField(max_length=50)),
                ('object_id',   models.CharField(max_length=40)),
                ('description', models.CharField(max_length=200)),
                ('detail',      models.CharField(max_length=200, blank=True)),
                ('timestamp',   models.DateTimeField(auto_now_add=True)),
                ('user',        models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='master_changes', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-timestamp']},
        ),
        # ── PLMasterItem ──────────────────────────────────────────────────────────────
        migrations.CreateModel(
            name='PLMasterItem',
            fields=[
                ('id',                   models.BigAutoField(auto_created=True, primary_key=True)),
                ('pl_number',            models.CharField(max_length=50, unique=True, db_index=True)),
                ('description',          models.CharField(max_length=300, blank=True)),
                ('uvam_id',              models.CharField(max_length=60, blank=True)),
                ('inspection_category',  models.CharField(max_length=1, blank=True, choices=[('A','A — Safety Critical'),('B','B — Important'),('C','C — Normal')])),
                ('safety_item',          models.BooleanField(default=False)),
                ('loco_types',           models.JSONField(default=list, blank=True)),
                ('application_area',     models.CharField(max_length=200, blank=True)),
                ('used_in',              models.CharField(max_length=200, blank=True)),
                ('is_active',            models.BooleanField(default=True)),
                ('remarks',              models.TextField(blank=True)),
                ('created_at',           models.DateTimeField(auto_now_add=True)),
                ('updated_at',           models.DateTimeField(auto_now=True)),
                ('created_by',           models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='pl_items_created', to=settings.AUTH_USER_MODEL)),
                ('updated_by',           models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='pl_items_updated', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'PL Master Item',
                'verbose_name_plural': 'PL Master Items',
                'ordering': ['pl_number'],
                'indexes': [
                    models.Index(fields=['pl_number'],            name='master_plmi_pl_num_idx'),
                    models.Index(fields=['inspection_category'],  name='master_plmi_insp_cat_idx'),
                    models.Index(fields=['safety_item'],          name='master_plmi_safety_idx'),
                ],
            },
        ),
    ]
