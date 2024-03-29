# Generated by Django 4.1.2 on 2022-10-11 10:33

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='deviceType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('createdAt', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
            ],
            options={
                'db_table': 'deviceTypes',
            },
        ),
        migrations.CreateModel(
            name='genderType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('createdAt', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
            ],
            options={
                'db_table': 'genderTypes',
            },
        ),
        migrations.CreateModel(
            name='userType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('createdAt', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
            ],
            options={
                'db_table': 'userTypes',
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('fullName', models.CharField(max_length=255, null=True)),
                ('mobileNo', models.CharField(max_length=255, unique=True)),
                ('email', models.EmailField(max_length=255, unique=True)),
                ('password', models.CharField(max_length=255)),
                ('isActive', models.BooleanField(default=True)),
                ('isDeleted', models.BooleanField(default=False)),
                ('isVerified', models.BooleanField(default=False)),
                ('countryCode', models.CharField(max_length=255, null=True)),
                ('deviceToken', models.CharField(max_length=255, null=True)),
                ('profileImage', models.CharField(blank=True, max_length=255, null=True)),
                ('lat', models.FloatField(blank=True, default=0.0, null=True)),
                ('lng', models.FloatField(blank=True, default=0.0, null=True)),
                ('state', models.CharField(default=None, max_length=255)),
                ('last_login', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('isAvailable', models.BooleanField(default=False)),
                ('isApproved', models.IntegerField(choices=[(1, 'pending'), (2, 'approved'), (3, 'disapproved')], default=1)),
                ('admin_forget_password_token', models.CharField(default=False, max_length=200, null=True)),
                ('stripeCustomerId', models.CharField(default=None, max_length=255, null=True)),
                ('createdAt', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('updatedAt', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('deviceTypeId', models.ForeignKey(db_column='deviceTypeId', on_delete=django.db.models.deletion.CASCADE, related_name='deviceType_ref', to='auth_APIs.devicetype')),
                ('genderTypeId', models.ForeignKey(db_column='genderTypeId', on_delete=django.db.models.deletion.CASCADE, related_name='genderType_ref', to='auth_APIs.gendertype')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('userTypeId', models.ForeignKey(db_column='userTypeId', on_delete=django.db.models.deletion.CASCADE, related_name='userType_ref', to='auth_APIs.usertype')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'db_table': 'users',
            },
        ),
    ]
