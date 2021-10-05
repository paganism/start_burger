# Generated by Django 3.2 on 2021-10-05 05:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coordinates', '0003_alter_coordinates_fetched_from_api_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='coordinates',
            name='lat',
            field=models.DecimalField(decimal_places=8, default=1, max_digits=11, verbose_name='широта'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='coordinates',
            name='long',
            field=models.DecimalField(decimal_places=8, default=1, max_digits=11, verbose_name='долгота'),
            preserve_default=False,
        ),
    ]
