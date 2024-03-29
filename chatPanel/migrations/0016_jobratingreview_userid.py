# Generated by Django 3.2 on 2023-06-21 06:51

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('chatPanel', '0015_alter_job_jobstatus_alter_jobassign_assignstatus'),
    ]

    operations = [
        migrations.AddField(
            model_name='jobratingreview',
            name='userId',
            field=models.ForeignKey(db_column='userId', default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='customer_rating_ref', to=settings.AUTH_USER_MODEL),
        ),
    ]
