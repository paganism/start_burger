# Generated by Django 3.2 on 2021-09-20 06:11

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('coordinates', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='coordinates',
            name='fetched_from_api_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
