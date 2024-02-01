# Generated by Django 4.1.2 on 2023-03-16 11:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chatPanel', '0014_jobratingreview_doerid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='job',
            name='jobStatus',
            field=models.IntegerField(choices=[(1, 'initiated'), (2, 'Running'), (3, 'Accepted'), (4, 'completed'), (5, 'failed'), (6, 'cancelled'), (7, 'cancelTimeOut')], default=1),
        ),
        migrations.AlterField(
            model_name='jobassign',
            name='assignStatus',
            field=models.IntegerField(choices=[(1, 'initiated'), (2, 'ProposalCreated'), (3, 'Accepted'), (4, 'rejected'), (5, 'cancelTimeOut')], default=1),
        ),
    ]