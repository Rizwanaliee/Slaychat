# Generated by Django 4.1.2 on 2022-11-02 11:26

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('auth_APIs', '0014_category_isapproved'),
    ]

    operations = [
        migrations.CreateModel(
            name='DoerSelectedSubCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('createdAt', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('updatedAt', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('doerDataId', models.ForeignKey(db_column='doerDataId', on_delete=django.db.models.deletion.CASCADE, related_name='doer_data_ref', to='auth_APIs.doeruserdata')),
                ('subCatId', models.ForeignKey(db_column='subCatId', on_delete=django.db.models.deletion.CASCADE, related_name='selected_sub_cat_ref', to='auth_APIs.subcategory')),
            ],
            options={
                'db_table': 'doer_selected_sub_category',
            },
        ),
    ]
