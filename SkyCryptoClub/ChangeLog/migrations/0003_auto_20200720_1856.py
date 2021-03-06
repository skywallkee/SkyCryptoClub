# Generated by Django 3.0.8 on 2020-07-20 18:56

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('ChangeLog', '0002_auto_20200719_2344'),
    ]

    operations = [
        migrations.CreateModel(
            name='FeatureRequest',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('summary', models.TextField()),
                ('requested_by', models.CharField(default='', max_length=15)),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.AlterField(
            model_name='feature',
            name='featureType',
            field=models.CharField(blank=True, max_length=25, null=True),
        ),
    ]
