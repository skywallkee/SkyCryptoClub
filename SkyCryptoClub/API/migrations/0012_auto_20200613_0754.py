# Generated by Django 3.0.7 on 2020-06-13 07:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('API', '0011_exchange_created_at'),
    ]

    operations = [
        migrations.RenameField(
            model_name='exchangetaxpeer',
            old_name='maxamount',
            new_name='maxAmount',
        ),
    ]