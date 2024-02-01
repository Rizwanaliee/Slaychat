# Generated by Django 4.1.2 on 2023-01-20 05:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chatPanel', '0008_alter_job_jobstatus'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='cancelOtherReason',
            field=models.CharField(default=None, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='job',
            name='cancelReason',
            field=models.IntegerField(choices=[(1, 'AcceptedByMistake'), (2, 'DoerWasLate'), (3, 'Doer did not provide the promised services'), (4, 'Doer did not show up'), (5, 'Other reasons')], default=None, null=True),
        ),
    ]