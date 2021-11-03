# Generated by Django 3.2 on 2021-09-28 05:29

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0055_delete_coordinates'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='address',
            field=models.TextField(verbose_name='Адрес доставки'),
        ),
        migrations.AlterField(
            model_name='order',
            name='called_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='время звонка'),
        ),
        migrations.AlterField(
            model_name='order',
            name='comment',
            field=models.TextField(blank=True, verbose_name='Комментарий'),
        ),
        migrations.AlterField(
            model_name='order',
            name='delivered_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='время доставки'),
        ),
        migrations.AlterField(
            model_name='order',
            name='registrated_at',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='дата регистрации'),
        ),
        migrations.AlterField(
            model_name='order',
            name='restaurant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='foodcartapp.restaurant', verbose_name='ресторан'),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='foodcartapp.order', verbose_name='заказ'),
        ),
        migrations.AlterField(
            model_name='product',
            name='description',
            field=models.TextField(blank=True, verbose_name='описание'),
        ),
    ]