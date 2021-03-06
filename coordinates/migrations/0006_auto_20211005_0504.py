# Generated by Django 3.2 on 2021-10-05 04:49

from django.db import migrations
from foodcartapp.coordinates_api_functions import parse_coordinates


def fill_long_lat(apps, schema_editor):
    Coordinates = apps.get_model('coordinates', 'Coordinates')
    coordinates = Coordinates.objects.all()

    for coord in coordinates:
        long_lat = parse_coordinates(coord.coordinates)
        long = long_lat[0]
        lat = long_lat[1]
        coord.long = long
        coord.lat = lat
        coord.save()


class Migration(migrations.Migration):

    dependencies = [
        ('coordinates', '0005_auto_20211005_0502'),
    ]

    operations = [
        migrations.RunPython(fill_long_lat),
    ]
