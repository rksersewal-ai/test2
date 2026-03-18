from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('edms', '0003_add_auxiliary_models'),
        ('workflow', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ApprovalChain',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_approval_chains', to=settings.AUTH_USER_MODEL)),
                ('document_type', models.ForeignKey(blank=True, help_text='Leave blank for a universal chain applicable to any document type.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approval_chains', to='edms.documenttype')),
            ],
            options={
                'db_table': 'workflow_approval_chain',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='ApprovalRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('PENDING', 'Pending'), ('IN_REVIEW', 'In Review'), ('APPROVED', 'Approved'), ('REJECTED', 'Rejected'), ('WITHDRAWN', 'Withdrawn')], db_index=True, default='PENDING', max_length=20)),
                ('current_step', models.IntegerField(default=0, help_text='step_order of the currently active ApprovalStep')),
                ('initiated_at', models.DateTimeField(auto_now_add=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('remarks', models.TextField(blank=True)),
                ('chain', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='requests', to='workflow.approvalchain')),
                ('initiated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='initiated_approval_requests', to=settings.AUTH_USER_MODEL)),
                ('revision', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='approval_requests', to='edms.revision')),
            ],
            options={
                'db_table': 'workflow_approval_request',
                'ordering': ['-initiated_at'],
                'indexes': [
                    models.Index(fields=['status'], name='workflow_ap_status_afdbda_idx'),
                    models.Index(fields=['revision'], name='workflow_ap_revisio_e16f02_idx'),
                ],
                'unique_together': {('revision', 'chain')},
            },
        ),
        migrations.CreateModel(
            name='ApprovalStep',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('step_order', models.IntegerField(default=0)),
                ('label', models.CharField(help_text='e.g. Checker, Section Engineer, HOD', max_length=120)),
                ('role', models.CharField(blank=True, max_length=50)),
                ('due_days', models.IntegerField(default=3, help_text='SLA: days from step activation to expected vote')),
                ('is_optional', models.BooleanField(default=False)),
                ('assigned_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approval_steps', to=settings.AUTH_USER_MODEL)),
                ('chain', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='steps', to='workflow.approvalchain')),
            ],
            options={
                'db_table': 'workflow_approval_step',
                'ordering': ['chain', 'step_order'],
                'unique_together': {('chain', 'step_order')},
            },
        ),
        migrations.CreateModel(
            name='ApprovalVote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vote', models.CharField(choices=[('APPROVED', 'Approved'), ('REJECTED', 'Rejected'), ('DELEGATED', 'Delegated'), ('RETURNED', 'Returned for Correction')], max_length=15)),
                ('comment', models.TextField(blank=True)),
                ('voted_at', models.DateTimeField(auto_now_add=True)),
                ('request', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='votes', to='workflow.approvalrequest')),
                ('step', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='votes', to='workflow.approvalstep')),
                ('voted_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approval_votes', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'workflow_approval_vote',
                'indexes': [
                    models.Index(fields=['request'], name='workflow_ap_request_43f5c1_idx'),
                    models.Index(fields=['voted_by'], name='workflow_ap_voted_b_3dfa8a_idx'),
                ],
                'unique_together': {('request', 'step')},
            },
        ),
    ]
