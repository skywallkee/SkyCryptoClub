# Generated by Django 3.0.7 on 2020-06-08 05:22

import SkyCryptoClub.API.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('API', '0004_currency_color'),
    ]

    operations = [
        migrations.AddField(
            model_name='currency',
            name='icon',
            field=models.ImageField(default='default_crypto.png', upload_to=SkyCryptoClub.API.models.currency_icon_upload),
        ),
    ]