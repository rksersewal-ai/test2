# Generated migration for apps.core
from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=20, unique=True)),
                ('name', models.CharField(max_length=120)),
                ('description', models.TextField(blank=True)),
                ('is_active', models.BooleanField(default=True)),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                                             related_name='children', to='core.section')),
            ],
            options={'db_table': 'core_section', 'ordering': ['code']},
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False)),
                ('username', models.CharField(max_length=60, unique=True)),
                ('email', models.EmailField(blank=True)),
                ('full_name', models.CharField(max_length=150)),
                ('employee_code', models.CharField(blank=True, max_length=30, null=True, unique=True)),
                ('designation', models.CharField(blank=True, max_length=100)),
                ('role', models.CharField(
                    choices=[('ADMIN', 'Administrator'), ('SECTION_HEAD', 'Section Head'),
                             ('ENGINEER', 'Engineer'), ('LDO_STAFF', 'LDO Staff'),
                             ('AUDIT', 'Audit'), ('VIEWER', 'Viewer')],
                    default='VIEWER', max_length=20)),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('last_login_ip', models.GenericIPAddressField(blank=True, null=True)),
                ('groups', models.ManyToManyField(blank=True, related_name='core_user_groups', to='auth.group')),
                ('user_permissions', models.ManyToManyField(blank=True, related_name='core_user_permissions',
                                                             to='auth.permission')),
                ('section', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                                              related_name='users', to='core.section')),
            ],
            options={'db_table': 'core_user', 'ordering': ['username']},
        ),
    ]
