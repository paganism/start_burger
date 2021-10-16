from django.db import models
from django.utils import timezone


class Coordinates(models.Model):
    address = models.TextField(
        max_length=100,
        verbose_name='Адрес доставки',
        unique=True
    )
    lat = models.DecimalField(
        max_digits=11,
        decimal_places=8,
        verbose_name='широта',
    )
    long = models.DecimalField(
        max_digits=11,
        decimal_places=8,
        verbose_name='долгота',
    )
    fetched_from_api_at = models.DateTimeField(
        default=timezone.now,
        db_index=True
    )


    class Meta:
        verbose_name = 'Координаты'
        verbose_name_plural = 'Координаты'

    def __str__(self):
        return self.address
