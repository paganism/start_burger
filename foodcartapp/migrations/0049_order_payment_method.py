# Generated by Django 3.2 on 2021-09-19 05:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0048_auto_20210919_0454'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='payment_method',
            field=models.CharField(choices=[('NON_CACHE', 'Электронно'), ('CACHE', 'Наличностью')], default='CACHE', max_length=20, verbose_name='Способ оплаты'),
        ),
    ]