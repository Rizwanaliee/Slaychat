# Generated by Django 4.1.2 on 2022-11-03 12:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth_APIs', '0015_doerselectedsubcategory'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='authServiceProviderId',
            field=models.CharField(max_length=255, null=True, unique=True),
        ),
    ]
