# Generated by Django 3.2 on 2021-09-19 11:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0050_order_restaurant'),
    ]

    operations = [
        migrations.AddField(
            model_name='restaurant',
            name='coordinates',
            field=models.JSONField(default=0, verbose_name='Координаты'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='order',
            name='payment_method',
            field=models.CharField(choices=[('NON_CACHE', 'Электронно'), ('CACHE', 'Наличностью'), ('NOT_SET', 'Не задан')], default='NOT_SET', max_length=20, verbose_name='Способ оплаты'),
        ),
    ]
