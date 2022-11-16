# Generated by Django 4.1.3 on 2022-11-16 01:30

import datetime
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import lessons.user_manager


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
            },
            managers=[
                ('objects', lessons.user_manager.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='DayOfTheWeek',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField(validators=[django.core.validators.MaxValueValidator(6)])),
                ('day', models.CharField(editable=False, max_length=10)),
            ],
            options={
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('balance', models.IntegerField(default=0)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='user_record', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Request',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(unique=True, validators=[django.core.validators.MaxValueValidator(limit_value=django.utils.timezone.now, message='')])),
                ('number_of_lessons', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1)])),
                ('interval_between_lessons', models.PositiveIntegerField(choices=[(1, '1 Week'), (2, '2 Weeks')])),
                ('duration_of_lessons', models.PositiveIntegerField(choices=[(30, '30 Minutes'), (45, '45 Minutes'), (60, '60 Minutes')])),
                ('further_information', models.CharField(max_length=500)),
                ('fulfilled', models.BooleanField(default=False)),
                ('availability', models.ManyToManyField(to='lessons.dayoftheweek')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('invoice_id', models.CharField(max_length=8, unique=True, validators=[django.core.validators.RegexValidator(message='Invoice number must follow the format xxxx-yyy where x is the student number and y is the invoice number.', regex='^\\d{4}-\\d{3}$')])),
                ('day_of_the_week', models.PositiveIntegerField(choices=[(1, 'Monday'), (2, 'Tuesday'), (3, 'Wednesday'), (4, 'Thursday'), (5, 'Friday'), (6, 'Saturday'), (7, 'Sunday')])),
                ('time_of_the_day', models.TimeField()),
                ('teacher', models.CharField(max_length=100)),
                ('start_date', models.DateField()),
                ('duration_of_lessons', models.PositiveIntegerField(choices=[(30, '30 Minutes'), (45, '45 Minutes'), (60, '60 Minutes')])),
                ('interval_between_lessons', models.PositiveIntegerField(choices=[(1, '1 Week'), (2, '2 Weeks')])),
                ('number_of_lessons', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1)])),
                ('further_information', models.CharField(max_length=500)),
                ('student', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='BankTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(validators=[django.core.validators.MaxValueValidator(limit_value=datetime.date.today, message='')])),
                ('amount', models.DecimalField(decimal_places=2, max_digits=6)),
                ('invoice_number', models.CharField(max_length=8, unique=True, validators=[django.core.validators.RegexValidator(message='Invoice number must follow the format xxxx-yyy where x is the student number and y is the invoice number.', regex='^\\d{4}-\\d{3}$')])),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
