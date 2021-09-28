# Generated by Django 3.2 on 2021-09-28 05:40

from django.db import migrations, models
import django.utils.timezone
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0057_alter_order_restaurant'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='called_at',
            field=models.DateTimeField(blank=True, db_index=True, null=True, verbose_name='время звонка'),
        ),
        migrations.AlterField(
            model_name='order',
            name='delivered_at',
            field=models.DateTimeField(blank=True, db_index=True, null=True, verbose_name='время доставки'),
        ),
        migrations.AlterField(
            model_name='order',
            name='payment_method',
            field=models.CharField(choices=[('NON_CACHE', 'Электронно'), ('CACHE', 'Наличностью'), ('NOT_SET', 'Не задан')], db_index=True, default='NOT_SET', max_length=20, verbose_name='Способ оплаты'),
        ),
        migrations.AlterField(
            model_name='order',
            name='phonenumber',
            field=phonenumber_field.modelfields.PhoneNumberField(db_index=True, max_length=128, region=None, verbose_name='Мобильный номер'),
        ),
        migrations.AlterField(
            model_name='order',
            name='registrated_at',
            field=models.DateTimeField(db_index=True, default=django.utils.timezone.now, verbose_name='дата регистрации'),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('NEW', 'Новый'), ('IN_PROGRESS', 'В работе'), ('CLOSED', 'Завершён')], db_index=True, default='NEW', max_length=20, verbose_name='Статус'),
        ),
    ]
