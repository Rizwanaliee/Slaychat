# Generated by Django 4.1.2 on 2023-01-17 09:29

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('chatPanel', '0008_alter_job_jobstatus'),
        ('auth_APIs', '0029_customercard'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('paymentId', models.CharField(default=None, max_length=255)),
                ('amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=10, max_length=255)),
                ('paymentStatus', models.IntegerField(choices=[(1, 'initiated'), (2, 'success'), (3, 'pending'), (4, 'Falied'), (5, 'refunded'), (6, 'failed'), (7, 'cancelled')], default=1)),
                ('reciept', models.CharField(blank=True, default=None, max_length=255, null=True)),
                ('stripeFee', models.DecimalField(decimal_places=2, default=0.0, max_digits=10, max_length=255, null=True)),
                ('netAmmount', models.DecimalField(decimal_places=2, default=0.0, max_digits=10, max_length=255, null=True)),
                ('adminCharge', models.DecimalField(decimal_places=2, default=0.0, max_digits=10, max_length=255, null=True)),
                ('createdAt', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('updatedAt', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('jobId', models.ForeignKey(db_column='jobId', on_delete=django.db.models.deletion.CASCADE, related_name='job_trans_Id', to='chatPanel.job')),
                ('paymentMethodId', models.ForeignKey(db_column='paymentMethodId', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='payment_method_ref', to='auth_APIs.customercard')),
                ('proposalId', models.ForeignKey(db_column='proposalId', default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='trans_proposal_Id', to='chatPanel.jobproposal')),
                ('userId', models.ForeignKey(db_column='userId', on_delete=django.db.models.deletion.CASCADE, related_name='userId_transaction', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'transactions',
            },
        ),
    ]
