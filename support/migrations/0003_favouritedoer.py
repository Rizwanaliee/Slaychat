# Generated by Django 4.1.2 on 2023-02-06 10:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('support', '0002_alter_queryticket_table'),
    ]

    operations = [
        migrations.CreateModel(
            name='FavouriteDoer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('createdAt', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('doerId', models.ForeignKey(db_column='doerId', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='favourite_to_doerId', to=settings.AUTH_USER_MODEL)),
                ('userId', models.ForeignKey(db_column='userId', on_delete=django.db.models.deletion.CASCADE, related_name='favourite_from_userId', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'favourite_doers',
            },
        ),
    ]
