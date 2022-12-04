# Generated by Django 4.1.3 on 2022-12-04 13:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lessons', '0002_rename_term_booking_term_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='booking',
            name='invoice_id',
        ),
        migrations.AddField(
            model_name='booking',
            name='invoice',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='lessons.invoice', unique=True),
            preserve_default=False,
        ),
    ]
