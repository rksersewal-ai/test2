from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('edms', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='revision',
            name='approved_by',
        ),
        migrations.RemoveField(
            model_name='revision',
            name='prepared_by',
        ),
        migrations.AddField(
            model_name='revision',
            name='approved_by',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='revisions_approved',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name='revision',
            name='prepared_by',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='revisions_prepared',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
