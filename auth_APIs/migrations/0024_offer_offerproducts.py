# Generated by Django 3.2 on 2022-11-17 06:22

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('auth_APIs', '0023_product'),
    ]

    operations = [
        migrations.CreateModel(
            name='Offer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('offerPercentage', models.DecimalField(decimal_places=2, default=0.0, max_digits=10, max_length=255)),
                ('offerDescription', models.TextField(default=None, null=True)),
                ('isDeleted', models.BooleanField(default=False)),
                ('createdAt', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('updatedAt', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('userId', models.ForeignKey(db_column='userId', on_delete=django.db.models.deletion.CASCADE, related_name='doer_offer_ref', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'doer_offers',
            },
        ),
        migrations.CreateModel(
            name='OfferProducts',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('createdAt', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('updatedAt', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('offerId', models.ForeignKey(db_column='offerId', on_delete=django.db.models.deletion.CASCADE, related_name='doer_offer_products_ref', to='auth_APIs.offer')),
                ('productId', models.ForeignKey(db_column='productId', on_delete=django.db.models.deletion.CASCADE, related_name='doer_offer_product_ref', to='auth_APIs.product')),
            ],
            options={
                'db_table': 'doer_offer_products',
            },
        ),
    ]