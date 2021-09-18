# Generated by Django 3.2 on 2021-09-18 06:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0044_alter_orderitem_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('NEW', 'Новый'), ('IN_PROGRESS', 'В работе'), ('CLOSED', 'Завершён')], default='NEW', max_length=20),
        ),
    ]
