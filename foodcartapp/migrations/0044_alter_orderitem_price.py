# Generated by Django 3.2 on 2021-09-17 13:06

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0043_auto_20210917_1234'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitem',
            name='price',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=8, validators=[django.core.validators.MinValueValidator(0)], verbose_name='цена'),
        ),
    ]
