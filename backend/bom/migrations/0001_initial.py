import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]

    operations = [
        migrations.CreateModel(
            name='BOMTree',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True)),
                ('loco_type', models.CharField(max_length=20)),
                ('variant', models.CharField(blank=True, max_length=60)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='bom_trees_created',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'app_label': 'bom',
                'ordering': ['loco_type', 'variant'],
                'unique_together': {('loco_type', 'variant')},
            },
        ),
        migrations.CreateModel(
            name='BOMNode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True)),
                ('pl_number', models.CharField(db_index=True, max_length=50)),
                ('description', models.CharField(blank=True, max_length=300)),
                ('node_type', models.CharField(
                    choices=[('ASSEMBLY', 'Assembly'), ('SUBASSEMBLY', 'Sub-Assembly'),
                             ('COMPONENT', 'Component'), ('PART', 'Part')],
                    default='PART', max_length=15,
                )),
                ('inspection_category', models.CharField(
                    blank=True,
                    choices=[('A', 'A - Safety Critical'), ('B', 'B - Important'),
                             ('C', 'C - Normal'), ('D', 'D - General'), ('', 'Unclassified')],
                    max_length=1,
                )),
                ('safety_item', models.BooleanField(default=False)),
                ('quantity', models.DecimalField(decimal_places=3, default=1, max_digits=10)),
                ('unit', models.CharField(default='Nos', max_length=20)),
                ('position', models.FloatField(default=0)),
                ('level', models.PositiveSmallIntegerField(default=0)),
                ('canvas_x', models.FloatField(default=0)),
                ('canvas_y', models.FloatField(default=0)),
                ('is_active', models.BooleanField(default=True)),
                ('remarks', models.CharField(blank=True, max_length=300)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('tree', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='nodes', to='bom.bomtree',
                )),
                ('parent', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='children', to='bom.bomnode',
                )),
                ('created_by', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='bom_nodes_created', to=settings.AUTH_USER_MODEL,
                )),
                ('updated_by', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='bom_nodes_updated', to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={'app_label': 'bom', 'ordering': ['level', 'position', 'pl_number']},
        ),
        migrations.CreateModel(
            name='BOMSnapshot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=120)),
                ('description', models.CharField(blank=True, max_length=300)),
                ('snapshot_data', models.JSONField(default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('tree', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='snapshots', to='bom.bomtree',
                )),
                ('created_by', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='bom_snapshots_created', to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={'app_label': 'bom', 'ordering': ['-created_at']},
        ),
    ]
