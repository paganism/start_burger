# Generated by Django 3.2 on 2021-10-04 18:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0059_alter_orderitem_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='payment_method',
            field=models.CharField(blank=True, choices=[('NON_CACHE', 'Электронно'), ('CACHE', 'Наличностью'), ('', '')], db_index=True, default='', max_length=20, verbose_name='Способ оплаты'),
        ),
    ]
