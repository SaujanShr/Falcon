# Generated by Django 4.1.3 on 2022-11-16 13:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lessons', '0002_alter_banktransaction_student'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='balance',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=6),
        ),
    ]