# Generated by Django 4.1.2 on 2023-03-01 07:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth_APIs', '0029_customercard'),
    ]

    operations = [
        migrations.AddField(
            model_name='allcountries',
            name='flagIconUrl',
            field=models.CharField(default=None, max_length=255, null=True),
        ),
    ]
