# Generated by Django 4.1.2 on 2022-11-01 11:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('auth_APIs', '0011_doeruserdata'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('catAddedBy', models.IntegerField(choices=[(1, 'admin'), (2, 'doer')], default=1)),
                ('catName', models.CharField(blank=True, max_length=255, null=True)),
                ('createdAt', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('updatedAt', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('userId', models.ForeignKey(db_column='userId', on_delete=django.db.models.deletion.CASCADE, related_name='user_cat_ref', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='SubCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('iconUrl', models.CharField(blank=True, max_length=255, null=True)),
                ('subCatName', models.CharField(blank=True, max_length=255, null=True)),
                ('createdAt', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('updatedAt', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('catId', models.ForeignKey(db_column='catId', on_delete=django.db.models.deletion.CASCADE, related_name='cat_ref', to='auth_APIs.category')),
            ],
        ),
    ]