from django.db import models
from django.utils import timezone


class Coordinates(models.Model):
    address = models.TextField(
        max_length=100,
        verbose_name='Адрес доставки',
        unique=True
    )
    coordinates = models.JSONField(verbose_name='Координаты')
    fetched_from_api_at = models.DateTimeField(default=timezone.now)


    class Meta:
        verbose_name = 'Координаты'
        verbose_name_plural = 'Координаты'

    def __str__(self): return self.address
